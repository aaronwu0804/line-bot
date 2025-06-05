"""
簡單的 LINE 訊息發送測試工具
"""

import os
import sys
from datetime import datetime
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

def main():
    """發送純文字測試訊息"""
    # 如果有命令行參數，使用它作為 token
    if len(sys.argv) > 1:
        access_token = sys.argv[1]
    else:
        access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    
    user_id = os.getenv('LINE_USER_ID')
    
    if not access_token:
        print("錯誤: 未提供 LINE_CHANNEL_ACCESS_TOKEN")
        print("請在命令行參數中提供 token 或設定 .env 檔案")
        return
        
    if not user_id:
        print("錯誤: 未提供 LINE_USER_ID")
        return
        
    print(f"使用 Token 長度: {len(access_token)}")
    print(f"將傳送訊息給使用者 ID: {user_id}")
    
    # 設定 LINE API 客戶端
    configuration = Configuration(access_token=access_token)
    api_client = ApiClient(configuration)
    line_bot_api = MessagingApi(api_client)
    
    # 建立測試訊息
    current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    message = TextMessage(text=f"LINE Bot 測試訊息 - {current_time}\n這是一個簡單的測試訊息，用來驗證 API Token 是否有效。")
    
    try:
        # 發送訊息
        print("正在發送訊息...")
        line_bot_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[message]
            )
        )
        print("✓ 訊息發送成功！")
    except Exception as e:
        print(f"✗ 訊息發送失敗: {str(e)}")

if __name__ == "__main__":
    main()
