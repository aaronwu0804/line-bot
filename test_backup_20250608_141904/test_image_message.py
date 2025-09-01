#!/usr/bin/env python3
"""
專門測試圖片訊息發送的腳本
"""

import os
import logging
import sys
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    ImageMessage,
    PushMessageRequest
)

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 設定日誌
logging.basicConfig(
    level=logging.DEBUG,  # 使用 DEBUG 級別來獲取最詳細的日誌
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def test_image_url(image_url):
    """測試圖片 URL 是否可以成功發送"""
    import requests
    
    # 測試圖片 URL 是否可訪問
    try:
        response = requests.head(image_url, timeout=10)
        logger.info(f"圖片 URL 檢查: {image_url}, 狀態碼: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"檢查圖片 URL 時出錯: {str(e)}")
        return False

def send_image_message():
    """專門測試發送圖片訊息"""
    try:
        # 1. 設定 LINE API 客戶端
        configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
        if not configuration.access_token:
            raise ValueError("未設定 LINE_CHANNEL_ACCESS_TOKEN")

        api_client = ApiClient(configuration)
        line_bot_api = MessagingApi(api_client)
        
        LINE_USER_ID = os.getenv('LINE_USER_ID')
        if not LINE_USER_ID:
            raise ValueError("未設定 LINE_USER_ID")
            
        # 2. 獲取圖片
        from test_pinterest import get_pinterest_image
        logger.info("正在獲取 Pinterest 圖片...")
        
        image_url = get_pinterest_image()
        if not image_url:
            logger.error("未能獲取圖片 URL")
            return False
            
        logger.info(f"成功獲取圖片 URL: {image_url}")
        
        # 3. 檢查圖片 URL 格式
        if not (image_url.startswith('http://') or image_url.startswith('https://')):
            logger.error(f"圖片 URL 格式無效: {image_url}")
            return False
        
        # 4. 確保圖片 URL 是 HTTPS (LINE 只接受 HTTPS)
        if image_url.startswith('http:'):
            image_url = image_url.replace('http:', 'https:')
            logger.info(f"URL 已轉換為 HTTPS: {image_url}")
        
        # 5. 測試圖片 URL 是否可訪問
        if not test_image_url(image_url):
            logger.error("圖片 URL 無法訪問")
            return False
            
        # 6. 創建文字訊息
        text_message = TextMessage(text="這是測試圖片訊息")
        
        # 7. 創建圖片訊息
        logger.info(f"正在創建圖片訊息，URL: {image_url}")
        image_message = ImageMessage(
            originalContentUrl=image_url,
            previewImageUrl=image_url
        )
        
        # 8. 發送訊息
        logger.info(f"發送訊息到用戶: {LINE_USER_ID}")
        line_bot_api.push_message(
            PushMessageRequest(
                to=LINE_USER_ID,
                messages=[text_message, image_message]
            )
        )
        logger.info("成功發送測試圖片訊息")
        return True
        
    except Exception as e:
        logger.error(f"發送圖片訊息失敗: {str(e)}")
        logger.exception("詳細錯誤:")
        return False

if __name__ == "__main__":
    result = send_image_message()
    print(f"測試結果: {'成功' if result else '失敗'}")
