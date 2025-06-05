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

# 載入環境變數
load_dotenv()

# 初始化 LINE Bot API
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
if not configuration.access_token:
    raise ValueError("未設定 LINE_CHANNEL_ACCESS_TOKEN")

api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)
LINE_USER_ID = os.getenv('LINE_USER_ID')
if not LINE_USER_ID:
    raise ValueError("未設定 LINE_USER_ID")

def send_test_message():
    """發送測試訊息"""
    try:
        current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        message = f"測試訊息\n發送時間：{current_time}"
        
        line_bot_api.push_message(
            LINE_USER_ID,
            TextSendMessage(text=message)
        )
        print("測試訊息發送成功！")
        
    except LineBotApiError as e:
        print(f"發送失敗：{str(e)}")
    except Exception as e:
        print(f"發生錯誤：{str(e)}")

if __name__ == "__main__":
    print("開始發送測試訊息...")
    send_test_message()
