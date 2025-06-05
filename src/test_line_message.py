import os
import sys
import logging
import requests
from datetime import datetime

# 設置 Python Path 以便能夠導入其他模組
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 從其他模組導入功能
from test_pinterest import get_pinterest_image
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    ImageMessage,
    PushMessageRequest
)
from dotenv import load_dotenv

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

def test_send_image():
    """測試獲取並發送圖片到 LINE"""
    try:
        # 設定 LINE Bot API
        configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
        if not configuration.access_token:
            logger.error("未設定 LINE_CHANNEL_ACCESS_TOKEN")
            return
            
        api_client = ApiClient(configuration)
        line_bot_api = MessagingApi(api_client)
        
        LINE_USER_ID = os.getenv('LINE_USER_ID')
        if not LINE_USER_ID:
            logger.error("未設定 LINE_USER_ID")
            return
        
        # 獲取圖片
        logger.info("開始獲取 Pinterest 圖片...")
        image_url = get_pinterest_image()
        
        if not image_url:
            logger.error("無法獲取圖片")
            return
            
        logger.info(f"成功獲取 Pinterest 圖片 URL: {image_url}")
        
        # 確保圖片 URL 是 HTTPS (LINE 只接受 HTTPS)
        if image_url.startswith('http:'):
            image_url = image_url.replace('http:', 'https:')
            logger.info(f"URL 已轉換為 HTTPS: {image_url}")
        
        # 檢查圖片 URL 是否可以訪問
        try:
            response = requests.head(image_url, timeout=10)
            logger.info(f"圖片 URL 檢查: 狀態碼 {response.status_code}")
        except Exception as e:
            logger.error(f"檢查圖片 URL 時出錯: {str(e)}")
        
        # 準備訊息
        messages = [
            TextMessage(text=f"測試發送中文早安圖片 - {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}"),
            ImageMessage(originalContentUrl=image_url, previewImageUrl=image_url)
        ]
        
        # 發送訊息
        logger.info(f"即將發送訊息到 LINE 用戶 ID: {LINE_USER_ID}")
        line_bot_api.push_message(
            PushMessageRequest(
                to=LINE_USER_ID,
                messages=messages
            )
        )
        logger.info("訊息發送成功！")
        
    except Exception as e:
        logger.error(f"發送訊息時發生錯誤: {str(e)}")
        logger.error(f"詳細錯誤: {repr(e)}")

if __name__ == "__main__":
    test_send_image()
