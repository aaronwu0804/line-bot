from datetime import datetime
import os
import logging
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    ImageMessage,
    PushMessageRequest
)

# 從 test_pinterest.py 導入圖片獲取函數
from test_pinterest import get_pinterest_image
from weather_service import WeatherService

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('line_bot_image_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def send_image_message():
    """發送圖片測試訊息"""
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
            
        # 獲取 Pinterest 圖片
        image_url = get_pinterest_image()
        if not image_url:
            raise ValueError("無法獲取圖片")
            
        # 準備訊息
        messages = []
        
        # 獲取天氣資訊
        weather_service = WeatherService(os.getenv('CWB_API_KEY'))
        weather = weather_service.get_taoyuan_weather()
        
        # 添加文字訊息
        current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        message_text = f"早安！\n發送時間：{current_time}"
        
        if weather:
            message_text += f"\n\n桃園市今日天氣:\n溫度: {weather['min_temp']}°C - {weather['max_temp']}°C\n降雨機率: {weather['rain_prob']}%"
        
        text_message = TextMessage(text=message_text)
        messages.append(text_message)
        
        # 添加圖片訊息
        image_message = ImageMessage(
            originalContentUrl=image_url,
            previewImageUrl=image_url
        )
        messages.append(image_message)
        
        # 發送訊息
        line_bot_api.push_message(
            PushMessageRequest(
                to=LINE_USER_ID,
                messages=messages
            )
        )
        logger.info("圖片訊息發送成功！")
        
    except Exception as e:
        logger.error(f"發送失敗：{str(e)}")

if __name__ == "__main__":
    logger.info("開始發送圖片測試訊息...")
    send_image_message()
