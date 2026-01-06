#!/usr/bin/env python3
"""
智能回應版 - LINE Bot Webhook 服務
使用 Gemini API 提供智能 AI 回應
整合所有功能於單一文件
"""

import os
import sys
import time
import json
import datetime
import threading
import logging
import requests
import random
from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, PushMessageRequest, TextMessage, ImageMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# 導入緩存模塊
try:
    from src.response_cache import response_cache
    CACHE_ENABLED = True
except ImportError:
    CACHE_ENABLED = False
    logging.warning("無法導入回應緩存模塊，跳過緩存功能")

print("="*80)
print(f"啟動 LINE Bot Webhook 智能回應服務 v2.1.0 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("增強版 - 直接從app.py啟動，避免LINE SDK衝突")
print("整合Gemini AI回應，提供智能對話功能")
print("添加自動保活機制，防止Render休眠")
print("新增緩存系統及錯誤處理，提升穩定性")
print("="*80)

# 初始化Flask應用
app = Flask(__name__)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 載入環境變數
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("環境變數載入成功")
except Exception as e:
    logger.error(f"載入環境變數時發生錯誤: {str(e)}")

# 環境變數
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
RENDER_SERVICE_URL = os.getenv('RENDER_SERVICE_URL')
# 獲取Gemini API金鑰 - 注意兩種可能的環境變數名稱
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_KEY')

# 對話歷史紀錄儲存
# 使用使用者ID作為鍵，儲存該使用者的對話歷史
conversation_histories = {}

# 對話狀態追蹤
# 使用使用者ID作為鍵，紀錄用戶是否正在進行連續對話及最後互動時間
active_conversations = {}

# 連續對話超時時間（秒）
CONVERSATION_TIMEOUT = 300  # 5分鐘無互動後結束對話

# 對話歷史記錄上限
MAX_HISTORY = 10  # 保留最近10輪對話

# 檢查並載入Gemini API
if GEMINI_API_KEY:
    try:
        # 導入套件並設置API金鑰
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        
        # 測試API連接並列出可用模型
        try:
            models = list(genai.list_models())
            model_names = [model.name for model in models]
            logger.info(f"成功連接Gemini API，可用模型: {model_names}")
        except Exception as api_e:
            logger.warning(f"Gemini API金鑰已設置，但測試連接失敗: {str(api_e)}")
    
    except ImportError:
        logger.warning("未能載入google-generativeai套件，AI回應功能將受限")
        logger.warning("請確認已安裝該套件：pip install google-generativeai>=0.3.1")
else:
    logger.warning("未設置Gemini API金鑰，將使用備用回應系統")

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    logger.error("缺少LINE API憑證")
    logger.error("請設置環境變數: LINE_CHANNEL_ACCESS_TOKEN和LINE_CHANNEL_SECRET")
    # 安全檢查 - 使用預設值以便測試
    if not os.getenv('RENDER', ''):  # 只在Render環境繼續執行
        LINE_CHANNEL_SECRET = "DUMMY_SECRET"
        LINE_CHANNEL_ACCESS_TOKEN = "DUMMY_TOKEN"
        logger.warning("使用虛擬憑證繼續執行 (僅供開發環境)")

# 自我保活機制
def self_ping_service():
    """定期ping自己以保持服務活躍的後台執行緒"""
    # 使用預設URL如果未設定環境變數
    service_url = RENDER_SERVICE_URL or "https://line-bot-pikj.onrender.com"
    
    # 確保URL格式正確
    if not service_url.startswith(('http://', 'https://')):
        service_url = f"https://{service_url}"
    
    health_url = f"{service_url}/health"
    logger.info(f"啟動自我保活機制，每10分鐘ping一次: {health_url}")
    
    # 等待30秒讓應用完全啟動
    time.sleep(30)
    
    # 初始ping測試
    try:
        logger.info("[自我保活] 初始ping測試")
        response = requests.get(health_url, timeout=5)
        logger.info(f"[自我保活] 初始ping回應: {response.status_code}")
    except Exception as e:
        logger.error(f"[自我保活] 初始ping錯誤: {e}")
    
    # 主要ping循環 - 每10分鐘一次
    while True:
        try:
            logger.info(f"[自我保活] Pinging {health_url}")
            response = requests.get(health_url, timeout=5)
            logger.info(f"[自我保活] 收到回應: {response.status_code}")
        except Exception as e:
            logger.error(f"[自我保活] 錯誤: {e}")
        
        # 休眠10分鐘（Render Free Tier休眠時間為15分鐘）
        time.sleep(10 * 60)

# 在Render環境中啟動自我保活機制
if os.getenv('RENDER', ''):
    ping_thread = threading.Thread(target=self_ping_service, daemon=True)
    ping_thread.start()
    logger.info("自我保活機制已在後台啟動")

# LINE Bot API設置
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET or "dummy_secret_for_initialization")

@app.route("/", methods=['GET'])
def home():
    """首頁"""
    now = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
    return f"""
    <html>
    <head><title>智能回應版LINE Bot v2.1.0</title></head>
    <body>
        <h1>LINE Bot Webhook服務 - 智能回應增強版 v2.1.0</h1>
        <p>目前時間: {now}</p>
        <p>這是一個智能回應版LINE Bot，整合Gemini API提供智能AI回應。</p>
        <p>狀態: 運行中</p>
        <p>Gemini API: {'已啟用' if GEMINI_API_KEY else '未啟用'}</p>
        <p>緩存系統: {'已啟用' if CACHE_ENABLED else '未啟用'}</p>
        <hr>
        <h2>鉛一：測試用LINE Bot</h2>
        <p><small>更新：增強型錯誤處理和改進的配額限制管理</small></p>
    </body>
    </html>
    """

@app.route("/health", methods=['GET'])
def health():
    """健康檢查"""
    status = "ok" if LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET else "warning"
    message = "LINE Bot Webhook service is running (Smart Response Version)"
    if status == "warning":
        message += " - MISSING CREDENTIALS"
    
    # 檢查Gemini API狀態
    gemini_status = "disabled"
    gemini_details = {}
    
    if GEMINI_API_KEY:
        if 'genai' in globals():
            try:
                # 測試API連接並收集詳細信息
                start_time = time.time()
                models = list(genai.list_models())
                api_response_time = time.time() - start_time
                
                if models:
                    gemini_status = "active"
                    available_models = [model.name for model in models]
                    # 提取模型詳細信息
                    model_details = []
                    for model in models:
                        model_info = {
                            "name": model.name,
                            "supported_generation_methods": getattr(model, "supported_generation_methods", []),
                        }
                        model_details.append(model_info)
                    
                    gemini_details = {
                        "model_count": len(models),
                        "response_time_ms": round(api_response_time * 1000, 2),
                        "available_models": model_details
                    }
                else:
                    gemini_status = "configured_no_models"
                    gemini_details = {"error": "無可用模型"}
            except Exception as api_error:
                gemini_status = "configured_error"
                gemini_details = {"error": str(api_error)}
        else:
            gemini_status = "configured_not_loaded"
            gemini_details = {"error": "套件未載入"}
    
    # 檢查緩存狀態
    cache_info = {
        "enabled": CACHE_ENABLED
    }
    
    if CACHE_ENABLED:
        try:
            # 清理過期緩存
            response_cache.clear_expired()
            
            # 獲取緩存目錄路徑
            cache_info["directory"] = str(response_cache.cache_dir)
            cache_info["ttl"] = response_cache.cache_ttl
            
            # 計算緩存文件數量
            try:
                cache_files = list(response_cache.cache_dir.glob('*.json'))
                cache_info["files"] = len(cache_files)
                
                # 獲取最近的幾個緩存文件
                if cache_files:
                    recent_files = sorted(cache_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]
                    latest_entries = []
                    for file in recent_files:
                        try:
                            with open(file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                latest_entries.append({
                                    "prompt": data.get('prompt', '')[:20] + "...",
                                    "timestamp": data.get('timestamp', ""),
                                })
                        except:
                            continue
                    
                    cache_info["latest"] = latest_entries
            except Exception as file_err:
                cache_info["file_error"] = str(file_err)
            
        except Exception as e:
            cache_info["error"] = str(e)
    else:
        cache_info["reason"] = "緩存模組未載入"
    
    return jsonify({
        "status": status,
        "message": message,
        "version": "2.1.0",  # 更新版本號
        "timestamp": str(os.popen('date').read().strip()),
        "environment": {
            "LINE_CHANNEL_ACCESS_TOKEN": "configured" if LINE_CHANNEL_ACCESS_TOKEN else "missing",
            "LINE_CHANNEL_SECRET": "configured" if LINE_CHANNEL_SECRET else "missing",
            "GEMINI_API": {
                "status": gemini_status,
                "details": gemini_details
            }
        },
        "cache": cache_info
    })

# 對話歷史紀錄儲存
# 使用使用者ID作為鍵，儲存該使用者的對話歷史
conversation_histories = {}

# 對話狀態追蹤
# 使用使用者ID作為鍵，紀錄用戶是否正在進行連續對話及最後互動時間
active_conversations = {}

# 連續對話超時時間（秒）
CONVERSATION_TIMEOUT = 300  # 5分鐘無互動後結束對話

# 對話歷史記錄上限
MAX_HISTORY = 10  # 保留最近10輪對話

# 預先定義的回應模板
weather_response = """
根據我的了解，今天是{current_date}，但我無法實時查詢天氣資訊。

您可以：
1. 使用「中央氣象局」官方網站(www.cwb.gov.tw)查詢最新天氣
2. 下載「氣象局」官方APP隨時掌握最新天氣資訊
3. 查看新聞網站的天氣專區

如需更精確的天氣預報，建議您查詢最新的氣象資料。
""".format(current_date=datetime.datetime.now().strftime('%Y年%m月%d日'))

time_response = """
現在的時間是：{current_time}

祝您有美好的一天！
""".format(current_time=datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))

greeting_response = """
你好！很高興與你交流。
我是一個AI助手，有什麼我可以幫助你的嗎？
"""

self_intro_response = """
我是一個由鉛一開發的AI助手，
目前整合了Gemini API，可以回答各種問題。
很高興能夠為您服務！
"""

help_response = """
👋 歡迎使用智能早安助理！

📅 我會在每個工作日早上 7:00 和週末早上 8:00 自動發送早安問候和天氣預報。

💬 我還可以幫您回答各種問題！使用方式如下：
- 輸入「AI: 您的問題」(例如：AI: 推薦幾本好書)
- 或輸入「@AI 您的問題」(例如：@AI 今天的天氣如何？)
- 或喊「小幫手」(例如：小幫手，介紹台灣夜市文化)
- 或喊「花生」(例如：花生，幫我查一下這個字怎麼念)

🔄 我具備上下文理解功能，一旦開始對話後，您可以直接提問，無需再加上前綴！

⏱️ 對話將在5分鐘無互動後自動結束，或您可以輸入「結束對話」來主動結束

🌟 AI小幫手花生祝您使用愉快！
"""

def extract_query(message):
    """從訊息中提取實際查詢內容"""
    user_question = message.strip()
    
    # 處理明確的前綴
    for prefix in ['ai:', 'ai：', '@ai ', '@ai', 'ai ']:
        if user_question.lower().startswith(prefix):
            user_question = user_question[len(prefix):]
            break
    
    # 處理「小幫手」和「花生」關鍵字
    keywords = ['小幫手', '花生', 'AI', 'ai']
    
    for keyword in keywords:
        # 如果關鍵字在開頭，移除它
        if user_question.startswith(keyword):
            user_question = user_question[len(keyword):]
            break
    
    # 處理允許的前導字符
    allowed_prefixes = ['!', '！', ',', '，', '。', '.', '?', '？', ' ', '　', ':', '：', '@', '#', '$', '%', '、', '~', '～']
    keywords = ['小幫手', '花生']
    
    for keyword in keywords:
        # 如果關鍵字在開頭，移除它
        if message.startswith(keyword):
            return message[len(keyword):].strip()
        
        # 處理有前導字符的情況
        if len(message) > 1:
            first_char = message[0]
            # 單個前導字符
            if first_char in allowed_prefixes and message[1:].startswith(keyword):
                return message[1 + len(keyword):].strip()
            
            # 前導字符+空格的情況 (如 ". 小幫手")
            if len(message) > 2 and first_char in allowed_prefixes and message[1] == ' ':
                if message[2:].startswith(keyword):
                    return message[2 + len(keyword):].strip()
    
    # 處理「花生」字符級別檢測
    flower_char = '花'
    life_char = '生'
    
    # 直接在句首的「花生」
    if message.startswith(flower_char) and len(message) > 1:
        if message[1] == life_char:
            return message[2:].strip()
    
    # 允許的前導字符後的「花生」
    if len(message) > 2 and message[0] in allowed_prefixes:
        # 一個前導字符的情況
        if message[1] == flower_char and message[2] == life_char:
            return message[3:].strip()
        
        # 前導字符+空格的情況
        elif message[1] == ' ' and len(message) > 3:
            if message[2] == flower_char and message[3] == life_char:
                return message[4:].strip()
    
    return user_question.strip()

def get_ai_response(message, conversation_history=None):
    """獲取AI回應"""
    # 提取用戶問題
    user_question = message
    
    # 嘗試從緩存中獲取回應
    if CACHE_ENABLED:
        cached_response = response_cache.get(user_question)
        if cached_response:
            logger.info(f"使用緩存回應: {user_question[:30]}...")
            return cached_response
    
    # 嘗試使用Gemini API (如果可用)
    try:
        if GEMINI_API_KEY and 'genai' in globals():
            try:
                # 獲取可用模型列表
                available_models = [model.name for model in genai.list_models()]
                logger.info(f"可用的Gemini模型: {available_models}")
                
                # 選擇適合的模型
                model_name = None
                # 創建實際可用模型的列表（處理帶前綴和不帶前綴的情況）
                normalized_models = []
                for model in available_models:
                    # 移除可能的前綴以標準化比較
                    clean_name = model.replace("models/", "")
                    normalized_models.append(clean_name)
                    if "/" in model:  # 如果有前綴，也保存原始名稱
                        normalized_models.append(model)
                
                logger.info(f"標準化後的可用模型列表: {normalized_models}")
                
                # 優先考慮較輕量的模型來避免API限制問題
                model_preference = ["gemini-1.5-flash", "gemini-1.0-flash", "gemini-1.5-pro", "gemini-pro", "gemini-1.0-pro"]
                for name in model_preference:
                    if name in normalized_models or f"models/{name}" in normalized_models:
                        model_name = name
                        logger.info(f"選擇到最適合的模型: {model_name}")
                        break
                
                if not model_name:
                    logger.warning("找不到優先列表中的Gemini模型，嘗試使用可用列表中的第一個模型")
                    # 嘗試選擇列表中的第一個模型（如果有）
                    for model in normalized_models:
                        if "gemini" in model.lower():
                            model_name = model.replace("models/", "") 
                            logger.info(f"選擇列表中的模型: {model_name}")
                            break
                    
                    # 如果仍然沒有找到，使用預設值
                    if not model_name:
                        model_name = "gemini-1.5-flash"  # 使用較輕量的模型作為預設值
                        logger.warning(f"未找到任何可用模型，使用預設模型: {model_name}")
                
                logger.info(f"使用Gemini模型: {model_name}")
                
                # 初始化生成式模型
                model = genai.GenerativeModel(model_name)
                
                # 添加提示詞引導回答風格和語言，減少令牌量
                prompt = f"""簡短、友好、繁體中文回覆：{user_question}"""
                
                # 設置重試次數和延遲
                max_retries = 3  # 增加重試次數
                base_retry_delay = 2  # 基礎重試延遲（秒）
                
                # 記錄開始生成回應的時間
                generation_start_time = time.time()
                
                # 使用指數退避策略嘗試生成回應
                for retry in range(max_retries + 1):
                    try:
                        # 根據重試次數調整請求參數
                        generation_config = {}
                        
                        # 如果不是第一次嘗試，調整參數以降低複雜度和提高成功率
                        if retry > 0:
                            # 降低輸出長度，提高溫度以獲得更多樣化但可能更短的回應
                            generation_config = {
                                "max_output_tokens": 256 - retry * 64,  # 逐漸減少輸出長度
                                "temperature": 0.5 + retry * 0.2,       # 逐漸增加溫度
                            }
                            # 簡化提示詞，減少令牌消耗
                            prompt = f"簡單回答: {user_question}"
                        
                        logger.info(f"嘗試 #{retry+1}/{max_retries+1}，調用Gemini API生成回應")
                        
                        # 生成回應
                        if generation_config and retry > 0:
                            response = model.generate_content(prompt, generation_config=generation_config)
                        else:
                            response = model.generate_content(prompt)
                        
                        if response and hasattr(response, 'text') and response.text:
                            # 檢查回應內容是否有效
                            response_text = response.text
                            
                            # 使用專用緩存模組保存回應
                            if CACHE_ENABLED:
                                try:
                                    response_cache.set(user_question, response_text)
                                    logger.info(f"回應已成功緩存: {user_question[:30]}...")
                                except Exception as cache_error:
                                    logger.warning(f"更新緩存時出錯: {str(cache_error)}")
                            
                            return response_text
                        else:
                            logger.warning("API返回了空回應，可能需要重試")
                            time.sleep(base_retry_delay)
                            continue
                            
                    except Exception as retry_error:
                        error_str = str(retry_error)
                        
                        # 更細緻的錯誤分類
                        if "429" in error_str:  # 配額限制錯誤
                            # 使用指數退避策略
                            retry_delay_seconds = min(base_retry_delay * (2 ** retry), 15)
                            logger.warning(f"Gemini API配額限制(429)，等待{retry_delay_seconds}秒後重試 ({retry+1}/{max_retries})")
                            time.sleep(retry_delay_seconds)
                            continue
                            
                        elif "404" in error_str:  # 模型未找到錯誤
                            logger.error(f"模型'{model_name}'未找到(404)，嘗試其他模型")
                            # 嘗試回退到其他模型
                            fallback_models = ["gemini-pro", "gemini-1.0-pro"]
                            for fallback in fallback_models:
                                if fallback != model_name:
                                    try:
                                        logger.info(f"嘗試回退模型: {fallback}")
                                        fallback_model = genai.GenerativeModel(fallback)
                                        response = fallback_model.generate_content(prompt)
                                        if response and hasattr(response, 'text') and response.text:
                                            return response.text
                                    except Exception as fallback_error:
                                        logger.warning(f"回退模型'{fallback}'也失敗: {str(fallback_error)}")
                            # 所有回退模型都失敗
                            break
                            
                        elif "400" in error_str:  # 請求格式錯誤
                            logger.error(f"請求格式錯誤(400): {error_str}")
                            # 簡化提示詞再試
                            if retry < max_retries:
                                prompt = f"回答: {user_question.split()[-10:]}"  # 只用問題的最後幾個詞
                                time.sleep(base_retry_delay)
                                continue
                            else:
                                break
                                
                        elif retry < max_retries:  # 其他錯誤，但未達最大重試次數
                            retry_delay_seconds = base_retry_delay * (retry + 1)
                            logger.warning(f"Gemini API錯誤，等待{retry_delay_seconds}秒後重試 ({retry+1}/{max_retries}): {error_str}")
                            time.sleep(retry_delay_seconds)
                            continue
                        else:
                            # 其他錯誤或已達到最大重試次數
                            logger.error(f"生成Gemini回應時出錯，已放棄重試: {error_str}")
                            break
                            
            except Exception as e:
                logger.error(f"生成Gemini回應時出錯: {str(e)}")
                # 繼續使用備用系統
    except Exception as e:
        logger.error(f"調用Gemini API時出錯: {str(e)}")
    
    # 備用系統：關鍵字回應
    question_lower = user_question.lower()
    current_date = datetime.datetime.now().strftime('%Y年%m月%d日')
    
    # 天氣相關問題
    if any(keyword in question_lower for keyword in ['天氣', '下雨', '氣象', '溫度', '濕度', '颱風', '紫外線']):
        return weather_response
    
    # 時間相關問題
    if any(keyword in question_lower for keyword in ['時間', '日期', '現在幾點', '今天幾號', '星期幾']):
        return time_response
    
    # 問候相關問題
    if any(keyword in question_lower for keyword in ['你好', '嗨', '哈囉', 'hi', 'hello', '早安', '午安', '晚安']):
        return greeting_response
    
    # 自我介紹相關問題
    if any(keyword in question_lower for keyword in ['你是誰', '介紹自己', '自我介紹', '關於你', '你的功能']):
        return self_intro_response
    
    # 尋求幫助相關問題
    if any(keyword in question_lower for keyword in ['幫助', '怎麼用', '如何使用', 'help', '指令', '說明']):
        return help_response
        
    # 旅遊相關問題
    if any(keyword in question_lower for keyword in ['旅遊', '旅行', '景點', '觀光', '行程', '飯店', '訂票']):
        return f"""關於旅遊問題「{user_question}」：

旅遊規劃需要考慮多方面因素，包括：
• 目的地的季節與天氣
• 預算考量
• 交通方式
• 住宿選擇
• 必訪景點

建議您可以參考各大旅遊網站、部落格，或使用專業旅遊App獲取最新資訊。
如果您需要更具體的建議，請提供更多細節，讓我更好地協助您。"""
    
    # 環球影城相關問題
    if any(keyword in question_lower for keyword in ['大阪', '京都', '大版', '日本', '環球', '影城', 'usj']):
        return f"""關於「{user_question}」：

日本環球影城(USJ)門票資訊：
• 可在官網購買: https://www.usj.co.jp/
• 或透過旅行社、KLOOK、KKDay等平台購買
• 建議提前預約，特別是假日期間
• 門票種類包括：1日券、2日券、快速通關等選項
• 有些特殊活動可能需要額外購票

購票時請注意查看官網最新資訊，價格和活動可能隨時變動。"""
        
    # 餐飲美食相關問題
    if any(keyword in question_lower for keyword in ['餐廳', '美食', '好吃', '推薦', '料理', '菜單', '食物']):
        return f"""關於美食問題「{user_question}」：

我很遺憾無法提供即時的餐廳推薦，因為餐廳資訊經常變動，且個人口味偏好各不相同。

您可以：
• 使用Google Map或其他美食App查詢附近評分高的餐廳
• 參考美食部落客的最新推薦
• 詢問當地朋友的建議

希望您能找到合適的美食選擇！"""
    
    # 日期計算相關問題
    if any(keyword in question_lower for keyword in ['幾天', '計算日期', '倒數', '幾週', '幾個月']):
        return f"""今天是{current_date}。

很抱歉，我無法進行精確的日期計算。要計算日期差異，您可以：
• 使用手機內建的日曆App
• 使用Excel或Google試算表
• 使用專門的日期計算工具網站

如果您有特定的日期計算需求，建議使用以上工具來獲得準確結果。"""
    
    # 緊急狀況相關詞彙
    if any(keyword in question_lower for keyword in ['緊急', '救護車', '警察', '火災', '地震', '颱風警報']):
        return """如果您正在經歷緊急狀況，請：

• 立即撥打119（火災/急救）
• 或撥打110（警察）
• 或聯繫當地緊急服務

此LINE Bot無法處理緊急情況。請務必尋求專業人員的及時協助。"""
    
    # 技術問題
    if any(keyword in question_lower for keyword in ['程式', '程式碼', '開發', '技術', 'python', 'javascript', 'coding']):
        return f"""關於技術問題「{user_question}」：

我是一個簡單的LINE Bot，無法提供深入的技術支援。
對於程式開發問題，建議您參考：

• Stack Overflow等技術社群
• GitHub文檔
• 官方API文檔
• 相關技術的教學網站或書籍

如需更專業的協助，建議尋找該領域的專家或參與相關技術社群。"""
    
    # 預設回應 - 提供更友好的無法回答訊息
    return f"""您的問題：「{user_question}」

很抱歉，我目前無法精確回答這個問題。我是一個簡單的AI助手，能力有限。

如果您的問題與天氣、時間、旅遊或日常問候相關，可以嘗試用更具體的方式提問。

感謝您的理解！"""

def is_ai_request(message):
    """檢查是否為AI請求 (最終版: 僅檢測訊息開頭或帶允許前導字符的關鍵字)"""
    if not message:
        return False
    
    # 添加日誌以查看接收到的確切訊息
    logger.info(f"檢測訊息是否為AI請求: '{message}'")
    
    # 嘗試處理可能的特殊字符或編碼問題
    normalized_message = message
    try:
        # 先嘗試規範化字符
        import unicodedata
        normalized_message = unicodedata.normalize('NFKC', message)
        if normalized_message != message:
            logger.info(f"已規範化訊息: '{normalized_message}'")
    except Exception as e:
        logger.error(f"規範化訊息時出錯: {str(e)}")
    
    # 去除前後空格，便於檢查句首關鍵字
    trimmed_message = normalized_message.strip()
    message_lower = trimmed_message.lower()
    
    # 1. 檢查常見的AI前綴 (必須在句首)
    if (message_lower.startswith(('ai:', 'ai：')) or 
        message_lower.startswith(('@ai', '@ai ')) or
        message_lower.startswith('ai ') or 
        message_lower == 'ai'):
        logger.info("識別為AI請求: 前綴匹配")
        return True
    
    # 2. 檢查中文關鍵字是否在句首或帶有允許的前導字符
    keywords = ['小幫手', '花生']
    
    # 允許的前導字符列表
    allowed_prefixes = ['!', '！', ',', '，', '。', '.', '?', '？', ' ', '　', ':', '：', '@', '#', '$', '%', '、', '~', '～']
    
    for keyword in keywords:
        # 檢查關鍵字是否在句首
        if trimmed_message.startswith(keyword):
            logger.info(f"識別為AI請求: 檢測到句首關鍵字 '{keyword}'")
            return True
        
        # 檢查是否有允許的前導字符後接關鍵字
        if len(trimmed_message) > 1:
            # 處理只有一個前導字符的情況
            first_char = trimmed_message[0]
            if first_char in allowed_prefixes and trimmed_message[1:].startswith(keyword):
                logger.info(f"識別為AI請求: 檢測到帶前導字符的關鍵字 '{keyword}', 前導字符: '{first_char}'")
                return True
            
            # 處理有前導字符和空格的情況 (如 ". 小幫手")
            if len(trimmed_message) > 2 and first_char in allowed_prefixes:
                # 特殊處理點號+空格情況
                if first_char == '.' and trimmed_message[1] == ' ' and trimmed_message[2:].startswith(keyword):
                    logger.info(f"識別為AI請求: 檢測到特殊點號和空格前導的關鍵字 '{keyword}'")
                    return True
                
                # 正常處理其他前導字符+空格情況
                if trimmed_message[1] == ' ' and trimmed_message[2:].startswith(keyword):
                    logger.info(f"識別為AI請求: 檢測到帶前導字符和空格的關鍵字 '{keyword}', 前導字符: '{first_char} '")
                    return True
    
    # 3. 特殊處理「花生」(字符級別)
    flower_char = '花'
    life_char = '生'
    
    # 直接在句首的「花生」
    if trimmed_message.startswith(flower_char) and len(trimmed_message) > 1:
        if trimmed_message[1] == life_char:
            logger.info(f"識別為AI請求: 通過字符級別檢測到句首 '花生' 關鍵字")
            return True
    
    # 允許的前導字符後的「花生」
    if len(trimmed_message) > 2 and trimmed_message[0] in allowed_prefixes:
        # 一個前導字符的情況
        if trimmed_message[1] == flower_char and trimmed_message[2] == life_char:
            logger.info(f"識別為AI請求: 通過字符級別檢測到帶前導字符的 '花生' 關鍵字")
            return True
            
        # 前導字符+空格的情況 (如 ". 花生")
        elif trimmed_message[1] == ' ' and len(trimmed_message) > 3:
            if trimmed_message[2] == flower_char and trimmed_message[3] == life_char:
                logger.info(f"識別為AI請求: 通過字符級別檢測到帶前導字符和空格的 '花生' 關鍵字")
                return True
    
    # 所有檢查都未通過
    logger.info("非AI請求: 未檢測到句首或帶允許前導字符的觸發關鍵字")
    return False
    
    # 如果經過所有檢查都不符合條件
    logger.info("非AI請求: 未檢測到任何觸發關鍵字")
    return False

@app.route("/callback", methods=['POST'])
def callback():
    """處理LINE Webhook回調"""
    logger.info("收到webhook回調")
    
    # 獲取X-Line-Signature標頭值
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        logger.error("缺少簽名")
        abort(400)
    
    # 獲取請求體
    body = request.get_data(as_text=True)
    logger.info("請求體: %s", body)
    
    # 處理webhook請求體
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("無效的簽名")
        abort(400)
    except Exception as e:
        logger.error("處理webhook時出錯: %s", e)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """處理文字訊息"""
    logger.info("收到訊息事件: %s", event)
    
    user_id = event.source.user_id
    user_message = event.message.text
    reply_token = event.reply_token
    
    logger.info("用戶 %s 發送訊息: %s", user_id, user_message)
    
    # 檢查是否為「生成圖片」指令
    if user_message.strip().startswith('生成圖片'):
        try:
            # 提取圖片描述提示詞
            prompt = user_message.strip()[4:].strip()  # 移除「生成圖片」四個字
            
            if not prompt:
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=reply_token,
                            messages=[TextMessage(text="請提供圖片描述！\n\n使用方式：\n生成圖片 一隻可愛的貓咪在玩毛線球")]
                        )
                    )
                return
            
            # 先回覆「正在生成」訊息
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=[TextMessage(text=f"🎨 正在為您生成圖片...\n描述：{prompt}\n\n使用 AI 圖片生成技術\n請稍候約10-15秒")]
                    )
                )
            
            # 生成圖片
            from src.image_generation_service import generate_image_with_gemini
            
            logger.info(f"開始生成圖片，提示詞: {prompt}")
            image_url = generate_image_with_gemini(prompt)
            
            if image_url:
                # 推送圖片訊息給用戶
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    
                    # 直接發送圖片訊息
                    line_bot_api.push_message(
                        PushMessageRequest(
                            to=user_id,
                            messages=[
                                TextMessage(text=f"✅ 圖片生成成功！\n描述：{prompt}"),
                                ImageMessage(
                                    original_content_url=image_url,
                                    preview_image_url=image_url
                                )
                            ]
                        )
                    )
                
                logger.info(f"圖片生成成功: {image_url}")
            else:
                # 生成失敗
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    line_bot_api.push_message(
                        PushMessageRequest(
                            to=user_id,
                            messages=[TextMessage(text="❌ 圖片生成失敗，請稍後再試\n\n可能原因：\n1. 網路連線問題\n2. 提示詞包含不當內容\n3. 服務暫時不可用")]
                        )
                    )
            
            return
            
        except Exception as e:
            logger.error(f"處理圖片生成時出錯: {str(e)}")
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=user_id,
                        messages=[TextMessage(text=f"❌ 處理圖片生成時發生錯誤：{str(e)}")]
                    )
                )
            return
    
    # 檢查是否為「每日單字」指令
    if user_message.strip() in ['每日單字', '每日英語', 'Daily English', 'daily english', '單字']:
        try:
            from src.daily_english_service import get_daily_word, format_daily_english_message, get_word_audio_url, get_sentence_audio_url
            
            # 獲取今日單字
            word_data = get_daily_word()
            message_text = format_daily_english_message(word_data)
            
            # 獲取單字和例句的語音URL
            word_audio_url = get_word_audio_url(word_data['word'])
            sentence_audio_url = get_sentence_audio_url(word_data['sentence'])
            
            # 回覆訊息
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                
                messages = [TextMessage(text=message_text)]
                
                # 添加發音連結
                audio_links = []
                if word_audio_url:
                    audio_links.append(f"🔊 單字發音:\n{word_audio_url}")
                if sentence_audio_url:
                    audio_links.append(f"🔊 例句發音:\n{sentence_audio_url}")
                
                if audio_links:
                    audio_message = "\n\n".join(audio_links)
                    messages.append(TextMessage(text=audio_message))
                
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=messages
                    )
                )
                logger.info("已回覆每日單字")
            return
            
        except Exception as e:
            logger.error(f"處理每日單字時出錯: {str(e)}")
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=[TextMessage(text="抱歉,獲取每日單字時發生錯誤,請稍後再試。")]
                    )
                )
            return
    
    # 檢查用戶是否處於活躍對話狀態
    current_time = time.time()
    is_active_conversation = check_active_conversation(user_id, current_time)
    
    # 檢查是否要結束對話
    if user_message.lower().strip() in ['結束', '結束對話', '停止', '停止對話', 'exit', 'quit', 'stop']:
        if is_active_conversation:
            # 結束對話
            end_conversation(user_id)
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=[TextMessage(text="好的，已結束本次對話。有需要時請隨時呼喚我！")]
                    )
                )
            return
    
    # 檢查訊息是否為 AI 對話請求 (活躍對話或匹配關鍵詞)
    if is_active_conversation or is_ai_request(user_message):
        # 如果是新的對話或匹配了關鍵詞，將用戶設為活躍對話狀態
        start_conversation(user_id)
        logger.info("檢測到AI請求或活躍對話，正在處理...")
        try:
            # 取出真實查詢內容（去除前綴）
            query = user_message
            if is_ai_request(user_message):
                # 如果是關鍵字觸發，需要提取查詢內容
                query = extract_query(user_message)
            
            # 獲取或初始化對話歷史
            conversation_history = conversation_histories.get(user_id, [])
            
            # 獲取AI回應
            start_time = time.time()
            ai_response = get_ai_response(query)
            process_time = time.time() - start_time
            logger.info(f"生成AI回應完成，耗時 {process_time:.2f} 秒")
            
            # 更新對話歷史
            update_conversation_history(user_id, query, ai_response)
            
            # 檢查回應是否為空
            if not ai_response:
                ai_response = "抱歉，我目前無法回答這個問題。請稍後再試。"
            
            # 回覆訊息
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                
                # 發送回覆
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=[TextMessage(text=ai_response)]
                    )
                )
                logger.info("已回覆AI請求")
            
        except Exception as e:
            logger.error(f"回覆AI訊息時出錯: {str(e)}")
            try:
                # 嘗試發送錯誤回覆
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    error_message = "抱歉，處理您的請求時發生錯誤，請稍後再試。"
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=reply_token,
                            messages=[TextMessage(text=error_message)]
                        )
                    )
            except Exception as reply_error:
                logger.error(f"發送錯誤回覆時出錯: {str(reply_error)}")
    else:
        logger.info("非AI請求，不處理")

# 讓gunicorn能夠找到應用
application = app

# 對話狀態管理相關的函數
def check_active_conversation(user_id, current_time):
    """檢查用戶是否處於活躍對話狀態"""
    if user_id in active_conversations:
        last_activity_time = active_conversations[user_id]
        # 檢查是否超時
        if current_time - last_activity_time <= CONVERSATION_TIMEOUT:
            return True
        else:
            # 超時自動結束對話
            end_conversation(user_id)
            return False
    return False

def start_conversation(user_id):
    """將用戶標記為活躍對話狀態"""
    active_conversations[user_id] = time.time()
    logger.info(f"用戶 {user_id} 開始/繼續對話")

def end_conversation(user_id):
    """結束用戶的對話狀態"""
    if user_id in active_conversations:
        del active_conversations[user_id]
        logger.info(f"用戶 {user_id} 結束對話")
    # 可選：根據需求決定是否要清除對話歷史
    # if user_id in conversation_histories:
    #     del conversation_histories[user_id]

def update_conversation_history(user_id, query, response):
    """更新使用者的對話歷史記錄"""
    # MAX_HISTORY 已在全域定義
    
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []
    
    # 添加新的對話
    conversation_histories[user_id].append({"role": "user", "parts": [query]})
    conversation_histories[user_id].append({"role": "model", "parts": [response]})
    
    # 如果歷史紀錄太長，移除最舊的對話
    if len(conversation_histories[user_id]) > MAX_HISTORY * 2:  # 一輪對話有兩條紀錄
        conversation_histories[user_id] = conversation_histories[user_id][-MAX_HISTORY*2:]
        
    # 更新對話狀態 (設定最新活動時間)
    start_conversation(user_id)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"在端口 {port} 啟動應用")
    app.run(host='0.0.0.0', port=port)
