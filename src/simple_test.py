"""
簡單的 LINE 文字訊息發送測試腳本
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    PushMessageRequest
)

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def send_test_message():
    """發送測試文字訊息到 LINE"""
    try:
        # 獲取 LINE API 設定
        LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        LINE_USER_ID = os.getenv('LINE_USER_ID')
        
        if not LINE_CHANNEL_ACCESS_TOKEN:
            logger.error("未設定 LINE_CHANNEL_ACCESS_TOKEN")
            return False
            
        if not LINE_USER_ID:
            logger.error("未設定 LINE_USER_ID")
            return False
            
        logger.info("開始測試 LINE 訊息發送功能...")
        
        # 設定 LINE API 客戶端
        configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
        api_client = ApiClient(configuration)
        line_bot_api = MessagingApi(api_client)
        
        # 建立測試訊息
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        test_message = TextMessage(text=f"測試訊息 - {current_time}\n\n這是一則簡單的測試訊息，用來確認 LINE Bot 運作正常。")
        
        # 發送訊息
        logger.info(f"發送訊息到用戶 ID: {LINE_USER_ID}")
        line_bot_api.push_message(
            PushMessageRequest(
                to=LINE_USER_ID,
                messages=[test_message]
            )
        )
        
        logger.info("訊息發送成功！")
        return True
        
    except Exception as e:
        logger.error(f"發送訊息時發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    if send_test_message():
        print("\n✓ 訊息測試成功！")
    else:
        print("\n✗ 訊息測試失敗！")
