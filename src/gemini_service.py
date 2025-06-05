"""
Gemini API 設定和管理模組
負責與 Google Gemini API 通信
包含配額限制處理和備用回應機制
"""

import os
import logging
import time
import random
import google.generativeai as genai
from dotenv import load_dotenv

# 嘗試導入流量限制器
try:
    from rate_limiter import gemini_limiter
    USE_RATE_LIMITER = True
    logger = logging.getLogger(__name__)
    logger.info("已啟用 Gemini API 流量限制器")
except ImportError:
    try:
        from src.rate_limiter import gemini_limiter
        USE_RATE_LIMITER = True
        logger = logging.getLogger(__name__)
        logger.info("已啟用 Gemini API 流量限制器 (從 src 導入)")
    except ImportError:
        USE_RATE_LIMITER = False
        logger = logging.getLogger(__name__)
        logger.warning("流量限制器導入失敗，將不使用流量控制功能")

def init_genai():
    """初始化 Google Generative AI API"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("未設定 GEMINI_API_KEY 環境變數，Gemini 功能將無法使用")
        return False
        
    try:
        # 配置 Gemini API
        genai.configure(api_key=api_key)
        logger.info("Gemini API 初始化成功")
        return True
    except Exception as e:
        logger.error(f"初始化 Gemini API 時發生錯誤: {str(e)}")
        return False

def get_gemini_response(prompt, conversation_history=None, max_retries=5, retry_delay=3):
    """
    獲取 Gemini 的回應，包含重試機制和配額限制處理
    
    參數:
        prompt: 用戶的問題或提示
        conversation_history: 對話歷史記錄，用於維持上下文 (選填)
        max_retries: 最大重試次數 (默認為 5)
        retry_delay: 重試前的等待秒數 (默認為 3)
        
    返回:
        回應文本，若有錯誤則返回錯誤訊息或備用回應
    """
    # 確保提示不為空
    if not prompt or prompt.strip() == "":
        return "請提供一個問題或指示，我會盡力回答。"
    
    # 初始化 Gemini API
    if not init_genai():
        logger.error("Gemini API 初始化失敗")
        return "抱歉，Gemini 服務目前無法使用。請確認 API 金鑰設定正確。"
    
    # 記錄詳細的提示資訊，但保護隱私
    safe_prompt = prompt[:20] + "..." if len(prompt) > 20 else prompt
    logger.info(f"處理提示: '{safe_prompt}'，歷史記錄長度: {len(conversation_history) if conversation_history else 0}")
    
    # 可供使用的模型列表，按優先順序排列
    models = ['gemini-1.5-pro', 'gemini-1.0-pro', 'gemini-pro']
    
    # 如果啟用了流量限制器，使用流量限制器執行 API 請求
    if USE_RATE_LIMITER:
        def execute_api_request():
            # 每次嘗試選擇一個模型
            for model_name in models:
                try:
                    # 設定模型
                    model = genai.GenerativeModel(model_name)
                    logger.info(f"嘗試使用模型: {model_name}")
                    
                    # 如果有對話歷史，使用 chat 模式
                    if conversation_history:
                        chat = model.start_chat(history=conversation_history)
                        response = chat.send_message(prompt)
                        return response.text
                    else:
                        # 單次回應
                        response = model.generate_content(prompt)
                        return response.text
                except Exception as e:
                    if "404" in str(e) and (model_name != models[-1]):
                        # 如果是模型不存在錯誤，且不是最後一個模型，則嘗試下一個模型
                        logger.warning(f"模型 {model_name} 不可用: {str(e)}")
                        continue
                    else:
                        # 其他錯誤，向上拋出
                        raise
        
        # 使用流量限制器執行請求
        result, error = gemini_limiter.execute_with_rate_limit(
            execute_api_request, max_retries=max_retries
        )
        
        if result:
            return result
        elif error:
            # 檢查是否是配額限制錯誤
            if "429" in error and "quota" in error.lower():
                logger.warning(f"Gemini API 遇到配額限制: {error}")
                backup_response = get_backup_response(prompt)
                if backup_response:
                    return backup_response
                return f"抱歉，Gemini API 目前遇到配額限制，請稍後再試。或者可以嘗試在白天使用，因為配額每天會重置。"
            else:
                logger.error(f"Gemini API 請求失敗: {error}")
                backup_response = get_backup_response(prompt)
                if backup_response:
                    return backup_response
                return f"抱歉，在處理您的請求時發生錯誤：{error}"
    
    # 如果沒有啟用流量限制器，使用原始的重試機制
    else:
        # 當前嘗試次數
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            # 每次嘗試選擇一個可用的模型
            model_index = min(retry_count, len(models) - 1)
            model_name = models[model_index]
            
            try:
                # 設定模型
                model = genai.GenerativeModel(model_name)
                logger.info(f"嘗試使用模型: {model_name} (嘗試 {retry_count + 1}/{max_retries})")
                
                # 如果有對話歷史，使用 chat 模式
                if conversation_history:
                    chat = model.start_chat(history=conversation_history)
                    response = chat.send_message(prompt)
                    return response.text
                else:
                    # 單次回應
                    response = model.generate_content(prompt)
                    return response.text
                    
            except Exception as e:
                last_error = e
                error_message = str(e)
                logger.error(f"與 Gemini API 通訊時發生錯誤 (嘗試 {retry_count + 1}/{max_retries}): {error_message}")
                
                # 如果是配額限制錯誤 (HTTP 429)
                if "429" in error_message and "quota" in error_message.lower():
                    retry_seconds = parse_retry_delay(error_message) or retry_delay
                    logger.info(f"遇到配額限制，等待 {retry_seconds} 秒後重試...")
                    time.sleep(retry_seconds)
                else:
                    # 其他錯誤，等待基本延遲時間後重試
                    time.sleep(retry_delay)
                
                retry_count += 1
        
        # 如果所有重試都失敗，返回友好錯誤訊息和備用回應
        if "429" in str(last_error) and "quota" in str(last_error).lower():
            return get_backup_response(prompt) or f"抱歉，Gemini API 目前遇到配額限制，請稍後再試。或者可以嘗試在白天使用，因為配額每天會重置。"
        else:
            return get_backup_response(prompt) or f"抱歉，在處理您的請求時發生錯誤：{str(last_error)}"


def parse_retry_delay(error_message):
    """從錯誤訊息中解析建議的重試延遲時間"""
    try:
        if "retry_delay" in error_message and "seconds" in error_message:
            # 嘗試從錯誤訊息中提取建議的重試時間
            import re
            match = re.search(r'retry_delay\s*{\s*seconds:\s*(\d+)\s*}', error_message)
            if match:
                return int(match.group(1))
    except Exception:
        pass
    return None


def get_backup_response(prompt):
    """提供基本的備用回應，當 Gemini API 不可用時使用"""
    
    if not prompt:
        return "您好！請問有什麼我可以幫助您的嗎？"
    
    # 簡單的關鍵詞匹配，用於判斷問題類型和提供適當回應
    prompt_lower = prompt.lower().strip()
    
    # 問候類
    if any(word in prompt_lower for word in ['你好', '哈囉', '嗨', 'hi', 'hello', '早安', '午安', '晚安']):
        greetings = [
            "你好！很高興為您服務。有什麼我能幫助您的嗎？", 
            "哈囉！有什麼我能幫助您的嗎？今天過得如何？", 
            "嗨！今天有什麼我可以協助您的？很高興見到您！", 
            "你好啊！很高興收到您的訊息。希望您今天過得愉快！"
        ]
        return random.choice(greetings)
        
    # 感謝類
    elif any(word in prompt_lower for word in ['謝謝', '感謝', 'thanks', 'thank you']):
        thanks = ["不客氣！很高興能幫到您。", "您太客氣了，這是我應該做的。", 
                  "不用謝！如果有其他需要，隨時告訴我。",
                  "很開心能提供幫助，隨時為您服務！"]
        return random.choice(thanks)
        
    # 詢問機器人狀態
    elif any(phrase in prompt_lower for phrase in ['你是誰', '你叫什麼', '自我介紹', '介紹自己']):
        return "我是您的智能早安助理，每天會自動發送早安問候和天氣預報。目前 Gemini AI 服務可能暫時無法使用，但我仍然會盡力協助您。"
    
    # 詢問天氣
    elif any(word in prompt_lower for word in ['天氣', '氣象', '下雨', '溫度', '預報']):
        weather_responses = [
            "抱歉，我目前無法獲取即時天氣資訊。不過，您可以期待明天早上的天氣預報推送。",
            "目前無法連接天氣服務，請稍後再試。每天早上我會自動發送天氣預報給您。",
            "天氣資訊暫時無法提供。不過別擔心，我會在每個工作日早上 7 點和週末早上 8 點自動發送天氣預報。"
        ]
        return random.choice(weather_responses)
        
    # 詢問功能
    elif any(word in prompt_lower for word in ['功能', '說明', '怎麼用', '幫助', 'help']):
        return ("以下是我的主要功能：\n"
                "1. 每日自動發送早安圖片和天氣預報（平日 7:00，週末 8:00）\n"
                "2. 根據天氣變化提供智慧化問候語\n"
                "3. 支援 AI 對話功能（以「AI:」或「@AI」開頭的訊息）\n\n"
                "目前 AI 對話功能暫時受限，請稍後再試。")
    
    # 測試訊息
    elif any(word in prompt_lower for word in ['測試', '測試中', 'test']):
        return "收到您的測試訊息。系統運作正常，不過 AI 對話功能暫時受到流量限制，請稍後再試。"
    
    # 預設回應
    return ("抱歉，由於 Gemini API 目前遇到流量限制，我無法提供完整的 AI 回應。"
            "請稍後再試，或是在白天時段使用，因為配額每天會重置。"
            "您也可以查看我的自動早安問候和天氣預報功能。")

# 簡單的測試函數
def test_gemini_api():
    """測試 Gemini API 連接"""
    if not init_genai():
        return "API 初始化失敗"
        
    try:
        response = get_gemini_response("你好，請用繁體中文簡短地自我介紹一下")
        return f"API 測試成功，回應: {response[:100]}..." if response else "API 回應為空"
    except Exception as e:
        return f"API 測試失敗: {str(e)}"
        
if __name__ == "__main__":
    # 設定日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 載入環境變數
    load_dotenv()
    
    # 測試 API
    result = test_gemini_api()
    print(result)
