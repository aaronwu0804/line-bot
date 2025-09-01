from datetime import datetime
import os
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    PushMessageRequest
)
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('line_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def test_line_message():
    """測試發送 LINE 訊息"""
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
        current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        message = f"LINE Bot 測試訊息\n發送時間：{current_time}"
        
        # 發送訊息
        line_bot_api.push_message(
            PushMessageRequest(
                to=LINE_USER_ID,
                messages=[TextMessage(text=message)]
            )
        )
        logger.info("測試訊息發送成功！")
        
    except Exception as e:
        logger.error(f"發送訊息失敗：{str(e)}")

if __name__ == "__main__":
    print("開始發送測試訊息...")
    test_line_message()
