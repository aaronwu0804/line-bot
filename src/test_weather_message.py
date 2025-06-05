"""
測試使用備用天氣資料發送早安訊息
此腳本測試從備用天氣資料中生成並發送早安訊息到 LINE
"""

from datetime import datetime
import os
import logging
import sys
import socket
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    ImageMessage,
    PushMessageRequest
)

# 設定 Python Path 以便能夠導入其他模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

# 從增強版天氣服務導入功能
try:
    # 相對路徑導入
    from weather_service_enhanced import WeatherService
    logger.info("使用增強版天氣服務")
except ImportError:
    try:
        # 嘗試從當前目錄導入
        from src.weather_service_enhanced import WeatherService
        logger.info("使用增強版天氣服務 (從 src 目錄導入)")
    except ImportError:
        try:
            # 最後嘗試從上層目錄導入
            from weather_service import WeatherService
            logger.info("使用原始版天氣服務")
        except ImportError:
            logger.error("無法導入天氣服務模組，請確認檔案路徑")
            sys.exit(1)

def check_dns_resolution(hostname="opendata.cwb.gov.tw"):
    """測試DNS解析是否正常工作"""
    try:
        logger.info(f"嘗試解析 {hostname}...")
        ip = socket.gethostbyname(hostname)
        logger.info(f"DNS解析成功： {hostname} -> {ip}")
        return True
    except socket.gaierror as e:
        logger.error(f"DNS解析失敗： {hostname}, 錯誤: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"解析時發生未知錯誤： {str(e)}")
        return False

def test_backup_weather():
    """測試備用天氣資料功能"""
    try:
        weather_service = WeatherService(os.getenv('CWB_API_KEY'))
        backup_weather = weather_service.get_backup_weather()
        logger.info(f"成功取得備用天氣資料: {backup_weather}")
        return backup_weather
    except Exception as e:
        logger.error(f"獲取備用天氣資料失敗: {str(e)}")
        return None

def generate_weather_message(weather):
    """根據天氣資料生成消息文字"""
    if not weather:
        return "無法獲取天氣資料，請稍後再試。"
    
    current_time = datetime.now().strftime('%Y年%m月%d日')
    
    # 根據天氣狀況添加適當的表情符號
    weather_emoji = "🌞"  # 預設晴天
    if "雨" in weather['weather']:
        weather_emoji = "🌧️"
    elif "陰" in weather['weather']:
        weather_emoji = "☁️"
    elif "多雲" in weather['weather']:
        weather_emoji = "⛅"
        
    message_text = (
        f"早安！今天又是嶄新的一天！\n"
        f"{current_time}\n\n"
        f"📍 {weather['district']}天氣報報 {weather_emoji}\n"
        f"天氣狀況：{weather['weather']}\n"
        f"溫度：{weather['min_temp']}°C - {weather['max_temp']}°C\n"
        f"降雨機率：{weather['rain_prob']}%\n"
        f"相對濕度：{weather['humidity']}%\n"
        f"舒適度：{weather['comfort']}\n\n"
        f"👉 {weather['description']}"
    )
    return message_text

def get_test_image():
    """獲取測試用的圖片 URL"""
    try:
        # 嘗試導入 Pinterest 圖片獲取函數
        try:
            from test_pinterest import get_pinterest_image
            logger.info("嘗試獲取 Pinterest 圖片...")
            image_url = get_pinterest_image()
            if image_url:
                logger.info(f"成功獲取 Pinterest 圖片: {image_url}")
                return image_url
        except ImportError:
            logger.warning("無法導入 Pinterest 圖片模組")
            
        # 如果無法獲取 Pinterest 圖片，使用預設圖片
        default_image_url = "https://images.pexels.com/photos/1287145/pexels-photo-1287145.jpeg"
        logger.info(f"使用預設圖片 URL: {default_image_url}")
        return default_image_url
    except Exception as e:
        logger.error(f"獲取測試圖片時出錯: {str(e)}")
        return None

def send_test_message():
    """使用備用天氣資料發送測試訊息"""
    try:
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
            
        # 取得備用天氣資料
        weather = test_backup_weather()
        if not weather:
            message_text = "測試訊息: 無法取得備用天氣資料，請檢查程式實作。"
        else:
            message_text = generate_weather_message(weather)
            message_text = "【測試訊息】\n" + message_text
        
        # 創建文字訊息
        text_message = TextMessage(text=message_text)
        messages.append(text_message)
        
        # 嘗試獲取並添加圖片
        try:
            image_url = get_test_image()
            if image_url:
                # 確保圖片 URL 是 HTTPS
                if image_url.startswith('http:'):
                    image_url = image_url.replace('http:', 'https:')
                    
                # 創建圖片訊息
                image_message = ImageMessage(
                    originalContentUrl=image_url,
                    previewImageUrl=image_url
                )
                messages.append(image_message)
                logger.info("已將圖片訊息添加到發送隊列")
        except Exception as img_error:
            logger.error(f"處理圖片時出錯: {str(img_error)}")
            # 繼續執行，即使沒有圖片也至少發送文字訊息
        
        # 發送訊息
        logger.info(f"準備發送測試訊息到: {LINE_USER_ID}")
        line_bot_api.push_message(
            PushMessageRequest(
                to=LINE_USER_ID,
                messages=messages
            )
        )
        logger.info(f"成功發送測試訊息，時間: {datetime.now()}")
        return True
    except Exception as e:
        logger.error(f"發送測試訊息失敗: {str(e)}")
        return False

if __name__ == "__main__":
    # 測試 DNS 解析
    logger.info("====== 測試 DNS 解析 ======")
    dns_result = check_dns_resolution()
    
    # 測試備用天氣資料
    logger.info("====== 測試備用天氣資料 ======")
    backup_weather = test_backup_weather()
    if backup_weather:
        logger.info("備用天氣資料正常")
        logger.info(f"生成的訊息內容: \n{generate_weather_message(backup_weather)}")
    else:
        logger.error("備用天氣資料取得失敗")
    
    # 發送測試訊息
    logger.info("====== 發送測試訊息 ======")
    send_result = send_test_message()
    
    # 測試結果摘要
    logger.info("====== 測試結果摘要 ======")
    logger.info(f"DNS 解析測試: {'成功' if dns_result else '失敗'}")
    logger.info(f"備用天氣資料: {'成功' if backup_weather else '失敗'}")
    logger.info(f"訊息發送測試: {'成功' if send_result else '失敗'}")

