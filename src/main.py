"""
早安貼文自動發送程式
功能：
1. 每日自動發送早安圖片和天氣預報到 LINE
2. 週一至週五 7:00、週六日 8:00 發送
3. 支持備用天氣資料避免網路問題
4. 智慧化問候語根據天氣變化
"""

from datetime import datetime
import os
import logging
import random
import time
import sys
import requests
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    ImageMessage,
    PushMessageRequest
)
import schedule

# 設置 Python Path 以便能夠導入其他模組
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 設定日誌
log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'morning_post.log')
# 確保 logs 資料夾存在
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 從其他模組導入功能
try:
    # 相對導入
    from src.test_pinterest import get_pinterest_image
except ImportError:
    try:
        # 直接導入
        from test_pinterest import get_pinterest_image
    except ImportError:
        logger.error("無法導入 Pinterest 圖片模組，請檢查路徑")
        # 定義一個備用函數
        def get_pinterest_image():
            logger.warning("使用備用圖片函數")
            return None

# 導入備用圖片服務
try:
    # 相對導入
    from src.backup_image_service import get_backup_image
except ImportError:
    try:
        # 直接導入
        from backup_image_service import get_backup_image
    except ImportError:
        logger.error("無法導入備用圖片服務，請檢查路徑")
        # 定義一個備用函數
        def get_backup_image():
            logger.warning("備用圖片服務不可用，將返回固定 URL")
            return "https://i.pinimg.com/originals/e5/73/7c/e5737c44dd061635766b6682a3e42d69.jpg"

try:
    # 優先使用增強版天氣服務
    try:
        from src.weather_service_enhanced import WeatherService
        logger.info("使用增強版天氣服務 (從 src 導入)")
    except ImportError:
        from weather_service_enhanced import WeatherService
        logger.info("使用增強版天氣服務")
except ImportError:
    # 如果找不到增強版，則使用原始版本
    try:
        from src.weather_service import WeatherService
        logger.info("使用原始版天氣服務 (從 src 導入)")
    except ImportError:
        from weather_service import WeatherService
        logger.info("使用原始版天氣服務")

# 載入環境變數
load_dotenv()

# 獲取Gemini API金鑰 - 注意兩種可能的環境變數名稱
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_KEY')

# 初始化 Gemini API 
gemini_initialized = False
if GEMINI_API_KEY:
    try:
        # 導入套件並設置API金鑰
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_initialized = True
        logger.info("Gemini API 已成功初始化")
    except ImportError:
        logger.warning("未能載入google-generativeai套件，智能問候功能將受限")
    except Exception as e:
        logger.warning(f"初始化Gemini API時發生錯誤: {str(e)}")
else:
    logger.info("未設置Gemini API金鑰，將使用預設問候語")

def generate_ai_greeting(weather_info=None):
    """使用 Gemini API 生成智能問候語，包含緩存、錯誤處理和指數退避重試"""
    if not gemini_initialized or not GEMINI_API_KEY:
        logger.warning("Gemini API 未初始化或未設定 API 金鑰，將使用預設問候語")
        return None
        
    # 嘗試導入緩存模塊和API監控模塊
    response_cache_module = None
    api_monitor = None
    try:
        # 導入緩存模塊
        from src.response_cache import response_cache as rc
        response_cache_module = rc
        logger.info("成功導入回應緩存模塊")
    except ImportError:
        try:
            from response_cache import response_cache as rc
            response_cache_module = rc
            logger.info("成功導入回應緩存模塊 (直接導入)")
        except ImportError:
            logger.warning("無法導入回應緩存模塊，將不使用緩存")
    
    try:
        # 導入 API 監控模塊
        from src.api_usage_monitor import APIUsageMonitor
        api_monitor = APIUsageMonitor()
        logger.info("成功導入 API 監控模塊")
    except ImportError:
        try:
            from api_usage_monitor import APIUsageMonitor
            api_monitor = APIUsageMonitor()
            logger.info("成功導入 API 監控模塊 (直接導入)")
        except ImportError:
            logger.warning("無法導入 API 監控模塊，將不記錄 API 使用情況")
    
    # 建立緩存鍵
    cache_key = None
    if weather_info:
        cache_key = f"morning_greeting_{weather_info.get('weather', '')}_{weather_info.get('temp', '')}_{weather_info.get('rain_prob', '')}"
    else:
        cache_key = "morning_greeting_default"
    
    # 嘗試從緩存中獲取
    if response_cache_module:
        cached_greeting = response_cache_module.get(cache_key)
        if cached_greeting:
            logger.info("從緩存中獲取問候語")
            return cached_greeting
    
    # API 調用計時開始
    start_time = time.time()
    
    try:
        # 最大重試次數和延遲基數
        max_retries = 3
        base_delay = 2
        available_models = []
        model_name = None
        
        # 嘗試獲取可用模型清單
        for attempt in range(max_retries):
            try:
                available_models = [model.name for model in genai.list_models()]
                
                # 記錄API使用
                if api_monitor:
                    api_monitor.log_api_call(
                        model="list_models",
                        success=True,
                        response_time=(time.time() - start_time) * 1000
                    )
                
                logger.info(f"可用的Gemini模型: {available_models}")
                break
            except Exception as e:
                error_str = str(e)
                logger.warning(f"嘗試 {attempt+1}/{max_retries}: 無法列出Gemini模型: {error_str}")
                
                # 記錄API錯誤
                if api_monitor:
                    api_monitor.log_api_call(
                        model="list_models",
                        success=False,
                        error_code="API_ERROR" if "429" not in error_str else "429",
                        error_message=error_str
                    )
                
                # 配額限制錯誤，實施指數退避
                if "429" in error_str:
                    retry_delay = base_delay * (2 ** attempt)
                    logger.warning(f"API 配額限制，等待 {retry_delay} 秒後重試")
                    time.sleep(retry_delay)
                else:
                    # 其他錯誤，稍微延遲後重試
                    time.sleep(1)
                
                # 最後一次嘗試失敗
                if attempt == max_retries - 1:
                    logger.error("無法列出模型，超過重試次數限制")
                    return None
        
        # 更智能的模型選擇策略 - 處理帶前綴和不帶前綴的模型名稱
        normalized_models = []
        for model in available_models:
            clean_name = model.replace("models/", "")
            normalized_models.append(clean_name)
            if "/" in model:  # 如果有前綴，也保存原始名稱
                normalized_models.append(model)
                
        # 優先使用最新的 Gemini 2.5 模型 (Pro 權限支援最新功能)
        model_preference = ["gemini-2.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-pro-vision", "gemini-pro", "gemini-1.5-pro"]
        for name in model_preference:
            if name in normalized_models or f"models/{name}" in normalized_models:
                model_name = name
                break
                
        if not model_name:
            logger.warning("找不到合適的Gemini模型，將使用預設問候語")
            return None
            
        logger.info(f"使用Gemini模型: {model_name} 生成問候語")
        
        # 建立提示詞
        prompt = "請生成一個簡短友好的早安問候語，不超過30個中文字。"
        
        # 如果有天氣資訊，加入到提示詞
        if weather_info:
            weather = weather_info.get('weather', '')
            temp = weather_info.get('temp', '20')
            rain_prob = weather_info.get('rain_prob', '0')
            
            prompt = f"""
            請根據以下天氣資訊，生成一段簡短、友好的早安問候語，長度不超過40個中文字。
            
            天氣狀況：{weather}
            溫度：{temp}°C
            降雨機率：{rain_prob}%
            
            請使用繁體中文回覆，並包含相應的表情符號。
            回應格式應該是「早安！...」
            """
        
        # 以指數退避策略生成回應
        greeting = None
        for attempt in range(max_retries):
            try:
                # 初始化生成式模型
                model = genai.GenerativeModel(model_name)
                
                # 根據重試次數動態調整參數
                temperature = 0.7 - (0.1 * attempt)  # 隨著重試降低溫度增加穩定性
                max_tokens = 100 - (20 * attempt)    # 隨著重試降低輸出長度
                
                # 設定生成參數，避免過長回應
                generation_config = {
                    "max_output_tokens": max(max_tokens, 40),  # 確保最小有40個令牌
                    "temperature": max(temperature, 0.3),      # 最低溫度不低於0.3
                }
                
                # 生成回應
                response = model.generate_content(prompt, generation_config=generation_config)
                
                # 記錄API成功使用
                if api_monitor:
                    api_monitor.log_api_call(
                        model=model_name,
                        success=True,
                        response_time=(time.time() - start_time) * 1000
                    )
                
                if response and hasattr(response, 'text'):
                    greeting = response.text.strip()
                    
                    # 確保開頭有「早安」
                    if not greeting.startswith("早安"):
                        greeting = f"早安！{greeting}"
                    
                    # 確保長度適中    
                    if len(greeting) > 80:
                        greeting = greeting[:77] + "..."
                        
                    logger.info(f"成功使用Gemini API生成問候語: {greeting}")
                    
                    # 保存到緩存
                    if response_cache_module:
                        response_cache_module.set(cache_key, greeting)
                        logger.info("問候語已保存到緩存")
                        
                    return greeting
                else:
                    logger.warning(f"嘗試 {attempt+1}/{max_retries}: 模型回應缺少文字內容")
            except Exception as e:
                error_str = str(e)
                logger.warning(f"嘗試 {attempt+1}/{max_retries}: 生成問候語時發生錯誤: {error_str}")
                
                # 記錄API錯誤
                if api_monitor:
                    api_monitor.log_api_call(
                        model=model_name,
                        success=False,
                        error_code="429" if "429" in error_str else "API_ERROR",
                        error_message=error_str
                    )
                
                # 配額限制錯誤，實施指數退避
                if "429" in error_str:
                    retry_delay = base_delay * (2 ** attempt)
                    logger.warning(f"API 配額限制，等待 {retry_delay} 秒後重試")
                    time.sleep(retry_delay)
                    
                    # 嘗試切換到更輕量的模型
                    if attempt < len(model_preference) - 1:
                        next_model = model_preference[attempt + 1]
                        if next_model in normalized_models or f"models/{next_model}" in normalized_models:
                            model_name = next_model
                            logger.info(f"切換到更輕量的模型: {model_name}")
                else:
                    # 其他錯誤，稍微延遲後重試
                    time.sleep(1)
                    
                # 簡化提示詞以減少標記數量
                if attempt > 0 and weather_info:
                    prompt = f"請根據天氣「{weather_info.get('weather', '')}」，生成簡短的早安問候語，使用繁體中文，包含表情符號。"
            
        logger.error("生成問候語失敗，超過重試次數限制")
        return None
    except Exception as e:
        logger.error(f"使用Gemini API時發生未預期的錯誤: {str(e)}")
        if api_monitor:
            api_monitor.log_api_call(
                model="unknown",
                success=False,
                error_code="UNEXPECTED_ERROR",
                error_message=str(e)
            )
        return None

def generate_greeting_message(weather_info=None):
    """根據天氣狀況生成早安問候語，優先使用 Gemini API 生成智能問候語，帶增強型緩存和錯誤處理"""
    # 嘗試導入 API 監控模塊
    api_monitor = None
    try:
        from src.api_usage_monitor import APIUsageMonitor
        api_monitor = APIUsageMonitor()
    except ImportError:
        try:
            from api_usage_monitor import APIUsageMonitor
            api_monitor = APIUsageMonitor()
        except ImportError:
            pass
    
    # 嘗試導入緩存模塊
    response_cache_module = None
    try:
        from src.response_cache import response_cache as rc
        response_cache_module = rc
    except ImportError:
        try:
            from response_cache import response_cache as rc
            response_cache_module = rc
        except ImportError:
            pass
    
    # 建立緩存鍵
    greeting_cache_key = None
    if weather_info:
        # 根據當前日期和天氣創建緩存鍵
        today_date = datetime.now().strftime('%Y%m%d')
        weather_str = weather_info.get('weather', '')
        temp_str = str(weather_info.get('temp', ''))
        rain_str = str(weather_info.get('rain_prob', ''))
        greeting_cache_key = f"greeting_{today_date}_{weather_str}_{temp_str}_{rain_str}"
        
        # 嘗試從緩存中取回問候語
        if response_cache_module:
            cached_greeting = response_cache_module.get(greeting_cache_key)
            if cached_greeting:
                logger.info(f"從緩存中獲取今日問候語: {cached_greeting}")
                return cached_greeting
    
    # 基本問候語集合
    basic_greetings = [
        "早安！今天又是嶄新的一天！",
        "早安！願你擁有美好的一天！",
        "早安！讓我們以微笑迎接今天！",
        "早安！新的一天充滿無限可能！",
        "早安！今天也要加油喔！",
        "早安！每一天都是新的開始！",
        "早安！祝你有個愉快的一天！",
        "早安！讓我們懷著感恩的心開始新的一天！",
        "早安！今天你最棒！",
        "早安！美好的一天從現在開始！",
        "早安！迎接嶄新挑戰的時刻到了！",
        "早安！願你今天的笑容如陽光般燦爛！"
    ]
    
    # 嘗試使用 Gemini API 生成智能問候語
    logger.info("嘗試使用 Gemini API 生成智能問候語...")
    start_time = time.time()
    ai_greeting = generate_ai_greeting(weather_info)
    api_response_time = time.time() - start_time
    
    # 成功生成 AI 問候語
    if ai_greeting:
        logger.info(f"成功生成 AI 問候語，用時: {api_response_time:.2f} 秒")
        
        # 如果有緩存模組且緩存鍵，則將結果保存到緩存
        if response_cache_module and greeting_cache_key:
            try:
                # 將 AI 生成的問候語存入緩存，並設置較長的 TTL (24小時)
                response_cache_module.set(greeting_cache_key, ai_greeting, ttl=86400)
                logger.info(f"AI 問候語已保存到緩存: {greeting_cache_key}")
            except Exception as cache_error:
                logger.warning(f"保存問候語到緩存時出錯: {str(cache_error)}")
                
        return ai_greeting
    else:
        logger.info(f"AI 問候語生成失敗，用時: {api_response_time:.2f} 秒，將使用備用問候語")
        
    # 如果 AI 生成失敗且無天氣信息，直接返回基本問候語
    if not weather_info:
        selected_greeting = random.choice(basic_greetings)
        logger.info(f"使用基本問候語: {selected_greeting}")
        return selected_greeting
    
    # 如果 AI 生成失敗但有天氣信息，則根據天氣情況生成問候語
    weather = weather_info.get('weather', '')
    rain_prob = float(weather_info.get('rain_prob', 0))
    temp = float(weather_info.get('temp', 20))
    
    # 根據天氣狀況的特殊問候語
    weather_greetings = []
    
    # 依據天氣現象選擇問候語
    if "雨" in weather:
        weather_greetings.extend([
            "早安！今天要記得帶傘喔！☔",
            "早安！雨天也要保持好心情！🌧️",
            "早安！下雨天要特別小心路滑！",
            "早安！窗外有雨滴，別忘了雨傘！",
            "早安！雨天出門別忘了帶傘！💦",
            "早安！雨水滋潤萬物，祝你有個美好的一天！"
        ])
    elif "陰" in weather:
        weather_greetings.extend([
            "早安！陰天也不減美好的心情！☁️",
            "早安！灰濛濛的天空也有它的美！",
            "早安！陰天更要用笑容照亮身邊的人！",
            "早安！雖是陰天，但心情要晴朗！",
            "早安！陰雲遮不住我們的好心情！✨",
            "早安！陰天也是美好的一天的開始！"
        ])
    elif "晴" in weather:
        weather_greetings.extend([
            "早安！和煦的陽光已經準備好了！☀️",
            "早安！讓我們迎接燦爛的陽光！",
            "早安！晴朗的天氣配上燦爛的笑容！",
            "早安！藍天白雲，心情也晴朗！",
            "早安！陽光燦爛，活力滿滿的一天！🌞",
            "早安！明媚的陽光照耀著嶄新的一天！"
        ])
    elif "多雲" in weather:
        weather_greetings.extend([
            "早安！多雲的天氣也很舒適！⛅",
            "早安！多雲也是一種美麗的風景！",
            "早安！雲朵遊戲，心情輕鬆！",
            "早安！雲層間透出的陽光格外珍貴！",
            "早安！多雲天氣也是美好的開始！"
        ])
    elif "霧" in weather:
        weather_greetings.extend([
            "早安！霧氣繚繞，宛如仙境！🌫️",
            "早安！霧天行車請注意安全！",
            "早安！霧霾中也要保持好心情！",
            "早安！今晨有霧，請減速慢行！"
        ])
    
    # 依據降雨機率選擇額外問候語
    if rain_prob > 70:
        weather_greetings.extend([
            "早安！降雨機率很高，記得帶傘！☂️",
            "早安！很可能會下雨，出門請做好準備！",
            "早安！降雨機率高，雨具不離身！"
        ])
    
    # 依據溫度選擇額外問候語
    if temp < 15:
        weather_greetings.extend([
            "早安！天氣很涼，記得添加衣物！🧥",
            "早安！別忘了多穿一件外套！",
            "早安！天氣轉涼，注意保暖喔！",
            "早安！今天溫度較低，要注意保暖！",
            "早安！記得穿暖和一點再出門喔！🧣"
        ])
    elif temp > 28:
        weather_greetings.extend([
            "早安！天氣較熱，記得補充水分！💧",
            "早安！請做好防曬措施！🧴",
            "早安！炎熱天氣，請多喝水！",
            "早安！高溫天氣，別忘了防曬！☀️",
            "早安！天氣炎熱，記得補充水分喔！🥤"
        ])
    elif 20 <= temp <= 25:
        weather_greetings.extend([
            "早安！今天溫度宜人，適合外出活動！🚶",
            "早安！舒適的溫度，願你有個美好的一天！",
            "早安！天氣舒適，是個適合出遊的好日子！🌳"
        ])
        
    # 如果有特殊天氣問候語，從中選擇，否則使用基本問候語
    if weather_greetings:
        selected_greeting = random.choice(weather_greetings)
        logger.info(f"使用天氣問候語: {selected_greeting}")
    else:
        selected_greeting = random.choice(basic_greetings)
        logger.info(f"使用基本問候語: {selected_greeting}")
    
    # 保存最終選擇的問候語到緩存
    if response_cache_module and greeting_cache_key:
        try:
            response_cache_module.set(greeting_cache_key, selected_greeting)
            logger.info(f"備用問候語已保存到緩存: {greeting_cache_key}")
        except Exception as cache_error:
            logger.warning(f"保存問候語到緩存時出錯: {str(cache_error)}")
    
    return selected_greeting

def send_morning_message():
    """發送早安訊息和天氣預報，使用增強型 Gemini API 和錯誤處理"""
    try:
        # 嘗試導入 API 監控模塊
        api_monitor = None
        try:
            # 嘗試從 src 目錄導入
            from src.api_usage_monitor import APIUsageMonitor
            api_monitor = APIUsageMonitor()
            logger.info("成功導入 API 監控模塊")
        except ImportError:
            try:
                # 嘗試直接導入
                from api_usage_monitor import APIUsageMonitor
                api_monitor = APIUsageMonitor()
                logger.info("成功導入 API 監控模塊 (直接導入)")
            except ImportError:
                logger.warning("無法導入 API 監控模塊，將不記錄 API 使用情況")
        
        # 檢查 Gemini API 狀態
        gemini_status = "未啟用"
        if GEMINI_API_KEY and gemini_initialized:
            logger.info("Gemini API 已啟用，將嘗試生成智能問候語")
            gemini_status = "已啟用"
            
            # 嘗試檢查 Gemini API 可用性，使用指數退避重試
            max_retries = 2
            base_delay = 1
            model_found = False
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"嘗試 {attempt+1}/{max_retries}: 檢查 Gemini API 可用性")
                    models = list(genai.list_models())
                    if models:
                        model_count = len(models)
                        logger.info(f"Gemini API 可用，找到 {model_count} 個模型")
                        
                        # 記錄 API 成功調用
                        if api_monitor:
                            api_monitor.log_api_call(
                                model="list_models",
                                success=True,
                                response_time=0
                            )
                        
                        gemini_status = f"已啟用 ({model_count} 個模型)"
                        model_found = True
                        break
                    else:
                        logger.warning("Gemini API 無法列出模型 (空清單)")
                        gemini_status = "已啟用，無可用模型"
                except Exception as api_error:
                    error_str = str(api_error)
                    logger.warning(f"Gemini API 測試失敗: {error_str}")
                    
                    # 記錄 API 錯誤
                    if api_monitor:
                        api_monitor.log_api_call(
                            model="list_models",
                            success=False,
                            error_code="429" if "429" in error_str else "API_ERROR",
                            error_message=error_str
                        )
                    
                    # 判斷是否為配額限制錯誤
                    if "429" in error_str:
                        retry_delay = base_delay * (2 ** attempt)
                        logger.warning(f"API 配額限制，等待 {retry_delay} 秒後重試")
                        gemini_status = "配額限制"
                        time.sleep(retry_delay)
                    else:
                        # 其他錯誤
                        gemini_status = "連接錯誤"
                        time.sleep(0.5)
                
                # 最後一次嘗試後，如果仍然失敗
                if attempt == max_retries - 1 and not model_found:
                    logger.warning("無法連接到 Gemini API，將使用備用問候語")
        else:
            logger.info("Gemini API 未啟用或未初始化，將使用預設問候語")
        
        # 設定 LINE Bot API
        configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
        if not configuration.access_token:
            raise ValueError("未設定 LINE_CHANNEL_ACCESS_TOKEN")

        api_client = ApiClient(configuration)
        line_bot_api = MessagingApi(api_client)
        
        LINE_USER_ID = os.getenv('LINE_USER_ID')
        if not LINE_USER_ID:
            raise ValueError("未設定 LINE_USER_ID")
            
        # 準備訊息
        messages = []
        
        # 獲取天氣資訊
        logger.info("開始獲取天氣資訊...")
        weather_service = WeatherService(os.getenv('CWB_API_KEY'))
        
        # 直接使用備用天氣資料作為主要資料，而不是先嘗試連接中央氣象局 API
        logger.info("直接使用備用天氣資料作為主要資料")
        weather = weather_service.get_backup_weather()
        
        # 如果備用資料也無法獲取，仍然設置為 None
        if not weather:
            logger.warning("無法獲取備用天氣資料")
        
        # 生成天氣相關的問候語，計時以判別是否為 AI 生成
        current_time = datetime.now().strftime('%Y年%m月%d日')
        start_time = time.time()
        greeting = generate_greeting_message(weather if weather else None)
        process_time = time.time() - start_time
        
        # 判斷是否使用了 AI 生成的問候語
        is_ai_greeting = process_time > 0.5  # 如果處理時間大於0.5秒，可能是使用了 AI API
        logger.info(f"問候語生成耗時: {process_time:.2f}秒，{'看起來是' if is_ai_greeting else '可能不是'} AI 生成")
        
        # 如果是 AI 生成的，記錄成功的 API 使用
        if is_ai_greeting and api_monitor:
            api_monitor.log_api_call(
                model="greeting_generation", 
                success=True,
                response_time=process_time * 1000
            )
        logger.info(f"問候語生成耗時: {process_time:.2f} 秒，{'是' if is_ai_greeting else '不是'} AI 生成")
        
        if weather:
            # 根據天氣狀況添加適當的表情符號
            weather_emoji = "🌞"  # 預設晴天
            if "雨" in weather['weather']:
                weather_emoji = "🌧️"
            elif "陰" in weather['weather']:
                weather_emoji = "☁️"
            elif "多雲" in weather['weather']:
                weather_emoji = "⛅"
                
            message_text = (
                f"{greeting}\n"
                f"{current_time}{' ✨' if is_ai_greeting else ''}\n\n"
                f"📍 {weather['district']}天氣報報 {weather_emoji}\n"
                f"天氣狀況：{weather['weather']}\n"
                f"溫度：{weather['min_temp']}°C - {weather['max_temp']}°C\n"
                f"降雨機率：{weather['rain_prob']}%\n"
                f"相對濕度：{weather['humidity']}%\n"
                f"舒適度：{weather['comfort']}\n\n"
                f"👉 {weather['description']}"
            )
        else:
            message_text = f"{greeting}\n{current_time}{' ✨' if is_ai_greeting else ''}\n\n抱歉，暫時無法獲取天氣資訊。"
            
        # 4. 添加文字訊息
        text_message = TextMessage(text=message_text)
        messages.append(text_message)
        
        # 5. 獲取並添加圖片
        try:
            logger.info("正在獲取 Pinterest 圖片...")
            pinterest_result = get_pinterest_image()
            
            # 強制打印日誌便於調試
            print(f"取得的 Pinterest 結果: {pinterest_result}")
            logger.info(f"取得的 Pinterest 結果: {pinterest_result}")
            
            # 判斷回傳值是本地檔案路徑還是 URL
            image_url = pinterest_result
            if pinterest_result and isinstance(pinterest_result, str) and os.path.isfile(pinterest_result):
                logger.info(f"Pinterest 返回的是本地檔案路徑: {pinterest_result}")
                
                try:
                    # 導入上傳圖床功能
                    try:
                        from src.backup_image_service import upload_image_to_imgbb
                    except ImportError:
                        from backup_image_service import upload_image_to_imgbb
                    
                    # 將本地檔案上傳到圖床
                    logger.info("正在上傳本地圖片到圖床...")
                    upload_url = upload_image_to_imgbb(pinterest_result)
                    if upload_url:
                        logger.info(f"成功將圖片上傳到圖床: {upload_url}")
                        image_url = upload_url
                    else:
                        logger.warning("上傳圖片到圖床失敗，使用備用圖片")
                        image_url = get_backup_image()
                except Exception as upload_error:
                    logger.error(f"上傳圖片時發生錯誤: {str(upload_error)}")
                    image_url = get_backup_image()
            
            # 檢查獲取的圖片 URL 是否有效
            if not image_url or not isinstance(image_url, str) or len(image_url) < 10:
                logger.warning(f"未能獲取有效的圖片資源: '{image_url}'")
                logger.info("嘗試使用備用圖片...")
                image_url = get_backup_image()
                logger.info(f"備用圖片 URL: {image_url}")
            
            # 確保圖片 URL 有效
            if image_url and isinstance(image_url, str) and len(image_url) > 10:
                logger.info(f"成功獲取圖片資源: {image_url}")
                
                # 檢查圖片資源格式
                if not (image_url.startswith('http://') or image_url.startswith('https://')):
                    logger.error(f"圖片資源格式無效 (需要 URL): {image_url}")
                    # 使用備用圖片
                    image_url = get_backup_image()
                    logger.info(f"已切換到備用圖片 URL: {image_url}")
                
                # 確保圖片 URL 是 HTTPS (LINE 只接受 HTTPS)
                if image_url.startswith('http:'):
                    image_url = image_url.replace('http:', 'https:')
                    logger.info(f"URL 已轉換為 HTTPS: {image_url}")
                
                # 檢查圖片 URL 是否可以訪問
                try:
                    response = requests.head(image_url, timeout=10, 
                                           headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
                    logger.info(f"圖片 URL 檢查: 狀態碼 {response.status_code}")
                    if response.status_code != 200:
                        logger.warning(f"圖片 URL 可能無效，狀態碼: {response.status_code}")
                        # 使用備用圖片
                        image_url = get_backup_image()
                        logger.info(f"已切換到備用圖片 URL: {image_url}")
                except Exception as url_check_error:
                    logger.warning(f"檢查圖片 URL 時出錯: {str(url_check_error)}")
                    # 使用備用圖片
                    image_url = get_backup_image()
                    logger.info(f"已切換到備用圖片 URL: {image_url}")
                
                # 確保 URL 格式正確
                if not image_url.startswith('https://'):
                    logger.warning(f"圖片 URL 不是 HTTPS，進行轉換: {image_url}")
                    if image_url.startswith('http://'):
                        image_url = image_url.replace('http://', 'https://')
                    else:
                        image_url = f"https://{image_url}"
                        
                logger.info(f"最終處理後的圖片 URL: {image_url}")
                
                # 創建圖片訊息 - 注意 LINE v3 SDK 的正確參數名稱
                try:
                    # 嘗試新版 SDK 參數名稱
                    image_message = ImageMessage(
                        original_content_url=image_url,
                        preview_image_url=image_url
                    )
                    messages.append(image_message)
                    logger.info("已將圖片訊息添加到發送隊列 (使用新版SDK參數)")
                except Exception as param_error:
                    logger.warning(f"使用新版參數名稱失敗: {str(param_error)}")
                    # 嘗試舊版參數名稱
                    try:
                        image_message = ImageMessage(
                            originalContentUrl=image_url,
                            previewImageUrl=image_url
                        )
                        messages.append(image_message)
                        logger.info("已將圖片訊息添加到發送隊列 (使用舊版SDK參數)")
                    except Exception as old_param_error:
                        logger.error(f"無法創建圖片訊息: {str(old_param_error)}")
                        logger.info("跳過圖片訊息")
            else:
                logger.warning(f"未能獲取有效圖片 URL: '{image_url}'，將只發送文字訊息")
        except Exception as img_error:
            logger.error(f"處理圖片時發生錯誤: {str(img_error)}")
            logger.error(f"詳細錯誤: {repr(img_error)}")
            
            # 最後嘗試使用固定的備用圖片
            try:
                backup_url = "https://i.pinimg.com/originals/e5/73/7c/e5737c44dd061635766b6682a3e42d69.jpg"
                logger.info(f"嘗試使用最終備用圖片: {backup_url}")
                
                try:
                    # 嘗試新版 SDK 參數名稱
                    image_message = ImageMessage(
                        original_content_url=backup_url,
                        preview_image_url=backup_url
                    )
                    messages.append(image_message)
                    logger.info("已將備用圖片訊息添加到發送隊列 (使用新版SDK參數)")
                except Exception as param_error:
                    try:
                        # 嘗試舊版 SDK 參數名稱
                        image_message = ImageMessage(
                            originalContentUrl=backup_url,
                            previewImageUrl=backup_url
                        )
                        messages.append(image_message)
                        logger.info("已將備用圖片訊息添加到發送隊列 (使用舊版SDK參數)")
                    except Exception as old_param_error:
                        logger.error(f"無法創建備用圖片訊息: {str(old_param_error)}")
                        # 跳過圖片訊息
            except Exception as backup_error:
                logger.error(f"添加備用圖片時發生錯誤: {str(backup_error)}")
                # 繼續執行，即使沒有圖片也至少發送文字訊息
        
        # 6. 發送訊息
        try:
            if messages:
                # LINE 訊息有數量限制（最多 5 則），這裡限制為最多 2 則（文字 + 圖片）
                if len(messages) > 2:
                    logger.warning(f"訊息數量超過限制，原始數量 {len(messages)}，將截取前 2 則")
                    messages = messages[:2]
                
                logger.info(f"即將發送 {len(messages)} 則訊息到 LINE，類型: {[type(m).__name__ for m in messages]}")
                
                # 確保每個訊息物件都是有效的
                valid_messages = []
                for msg in messages:
                    if isinstance(msg, (TextMessage, ImageMessage)):
                        valid_messages.append(msg)
                    else:
                        logger.warning(f"忽略無效的訊息類型: {type(msg)}")
                
                if valid_messages:
                    # 檢查訊息格式是否符合 LINE API 要求
                    try:
                        # 確保每個圖片訊息的 URL 以 HTTPS 開頭
                        for i, msg in enumerate(valid_messages):
                            if isinstance(msg, ImageMessage):
                                # 檢查圖片URL的屬性名稱
                                if hasattr(msg, 'originalContentUrl'):
                                    # 舊版屬性名稱
                                    if not msg.originalContentUrl.startswith('https://'):
                                        logger.warning(f"圖片 URL 不是 HTTPS: {msg.originalContentUrl}")
                                        # 嘗試轉換為 HTTPS
                                        msg.originalContentUrl = msg.originalContentUrl.replace('http://', 'https://')
                                        msg.previewImageUrl = msg.previewImageUrl.replace('http://', 'https://')
                                        valid_messages[i] = msg
                                elif hasattr(msg, 'original_content_url'):
                                    # 新版屬性名稱
                                    if not msg.original_content_url.startswith('https://'):
                                        logger.warning(f"圖片 URL 不是 HTTPS: {msg.original_content_url}")
                                        # 嘗試轉換為 HTTPS
                                        msg.original_content_url = msg.original_content_url.replace('http://', 'https://')
                                        msg.preview_image_url = msg.preview_image_url.replace('http://', 'https://')
                                        valid_messages[i] = msg
                                else:
                                    logger.warning(f"無法識別的圖片訊息格式: {msg}")
                    
                        # 發送訊息
                        logger.info(f"發送訊息到用戶: {LINE_USER_ID}")
                        line_bot_api.push_message(
                            PushMessageRequest(
                                to=LINE_USER_ID,
                                messages=valid_messages
                            )
                        )
                        logger.info(f"成功發送 {len(valid_messages)} 則訊息到 LINE")
                        logger.info(f"成功發送早安貼文，時間: {datetime.now()}")
                    except Exception as format_error:
                        logger.error(f"訊息格式錯誤: {str(format_error)}")
                        # 嘗試只發送文字訊息
                        text_only = [msg for msg in valid_messages if isinstance(msg, TextMessage)]
                        if text_only:
                            logger.info("嘗試只發送文字訊息...")
                            line_bot_api.push_message(
                                PushMessageRequest(
                                    to=LINE_USER_ID,
                                    messages=text_only
                                )
                            )
                            logger.info(f"成功發送 {len(text_only)} 則文字訊息到 LINE")
                else:
                    logger.error("沒有有效的訊息可發送")
            else:
                logger.error("沒有可發送的訊息")
        except Exception as send_error:
            logger.error(f"發送 LINE 訊息時發生錯誤: {str(send_error)}")
            logger.error(f"詳細錯誤內容: {repr(send_error)}")
            # 嘗試使用備用方法發送文字訊息
            try:
                fallback_message = TextMessage(text=f"早安！{current_time}\n\n今天的圖片無法顯示，但仍祝您有美好的一天！")
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=LINE_USER_ID,
                        messages=[fallback_message]
                    )
                )
                logger.info("成功發送備用文字訊息")
            except Exception as fallback_error:
                logger.error(f"發送備用訊息也失敗了: {str(fallback_error)}")
            # 不要在這裡拋出異常，讓程式能夠繼續執行
        
        # 清理舊圖片
        try:
            # 導入圖片清理模組
            try:
                from src.image_cleaner import clean_old_images
                logger.info("從 src 導入圖片清理模組")
            except ImportError:
                from image_cleaner import clean_old_images
                logger.info("導入圖片清理模組")
                
            # 設置保留 7 天內的圖片，刪除更舊的
            deleted_count = clean_old_images(max_age_days=7)
            
            if deleted_count > 0:
                logger.info(f"圖片清理完成：已刪除 {deleted_count} 張超過 7 天的舊圖片")
            else:
                logger.info("圖片清理完成：沒有需要刪除的舊圖片")
                
        except Exception as clean_error:
            logger.error(f"清理舊圖片時發生錯誤: {str(clean_error)}")
            # 不讓圖片清理錯誤影響主程式運行
        
    except Exception as e:
        logger.error(f"發送早安訊息失敗：{str(e)}")

def main():
    """主程式"""
    # 設定週一至週五早上 7 點發送訊息
    schedule.every().monday.at("07:00").do(send_morning_message)
    schedule.every().tuesday.at("07:00").do(send_morning_message)
    schedule.every().wednesday.at("07:00").do(send_morning_message)
    schedule.every().thursday.at("07:00").do(send_morning_message)
    schedule.every().friday.at("07:00").do(send_morning_message)
    
    # 設定週六和週日早上 8 點發送訊息
    schedule.every().saturday.at("08:00").do(send_morning_message)
    schedule.every().sunday.at("08:00").do(send_morning_message)
    
    logger.info("排程已啟動：平日 07:00、週末 08:00")
    
    while True:
        pending_jobs = schedule.get_jobs()
        next_run = min([job.next_run for job in pending_jobs]) if pending_jobs else None
        if next_run:
            logger.info(f"等待下次排程執行，下次執行時間: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 檢查並記錄當前時間
        current_time = datetime.now()
        logger.debug(f"當前時間: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    try:
        print("=" * 60)
        print(f"LINE Bot 早安訊息服務 v2.1.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("已整合 Gemini API 智能問候功能")
        print("=" * 60)
        
        logger.info("程式開始執行...")
        logger.info(f"Gemini API 狀態: {'已啟用' if gemini_initialized else '未啟用'}")
        logger.info(f"環境變數: LINE_USER_ID={'已設定' if os.getenv('LINE_USER_ID') else '未設定'}")
        logger.info(f"環境變數: LINE_CHANNEL_ACCESS_TOKEN={'已設定' if os.getenv('LINE_CHANNEL_ACCESS_TOKEN') else '未設定'}")
        logger.info(f"環境變數: CWB_API_KEY={'已設定' if os.getenv('CWB_API_KEY') else '未設定'}")
        
        # 檢查命令行參數
        import sys
        if len(sys.argv) > 1:
            if sys.argv[1] == "--test":
                logger.info("==== 執行測試模式 ====")
                logger.info("發送一次測試訊息，不啟動排程")
                send_morning_message()
                logger.info("測試訊息發送完成")
            elif sys.argv[1] == "--schedule-only":
                logger.info("==== 僅啟動排程模式 ====")
                logger.info("跳過初始訊息，直接啟動排程")
                # 只啟動排程，不發送立即訊息
                main()
            elif sys.argv[1] == "--clean-images":
                logger.info("==== 執行圖片清理模式 ====")
                try:
                    from src.image_cleaner import clean_old_images
                except ImportError:
                    from image_cleaner import clean_old_images
                    
                # 如果有指定天數參數，則使用該參數
                max_age_days = 7  # 預設 7 天
                if len(sys.argv) > 2:
                    try:
                        max_age_days = int(sys.argv[2])
                    except ValueError:
                        logger.warning(f"無效的天數參數: {sys.argv[2]}，使用預設值 7 天")
                
                deleted = clean_old_images(max_age_days=max_age_days)
                logger.info(f"圖片清理完成: 已刪除 {deleted} 張超過 {max_age_days} 天的舊圖片")
        else:
            logger.info("==== 開始發送早安訊息 ====")
            # 立即發送一次訊息
            send_morning_message()
            logger.info("==== 早安訊息發送完成，開始設置排程 ====")
            # 啟動排程
            main()
    except KeyboardInterrupt:
        logger.info("程式已停止")
    except Exception as e:
        logger.error(f"程式執行時發生錯誤: {str(e)}")
        logger.exception("詳細錯誤追蹤：")  # 這會記錄完整的堆棧追蹤
