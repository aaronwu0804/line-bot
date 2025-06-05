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

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def check_token_length():
    """檢查 LINE Access Token 是否有效"""
    token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    if not token:
        print("警告: 沒有找到 LINE_CHANNEL_ACCESS_TOKEN 環境變數")
        return
        
    token_length = len(token)
    print(f"LINE Access Token 長度: {token_length} 字元")
    
    # 大多數 LINE 的 Token 長度超過 150 字元，如果少於這個值可能被截斷了
    if token_length < 150:
        print("警告: ACCESS TOKEN 可能被截斷了！")
        print("請確認在 .env 文件中的完整 token 值")
    else:
        print("Token 長度看起來正常。")
        
    # 檢查是否包含常見的 token 字符
    if "/" in token and "+" in token and "=" in token:
        print("Token 格式看起來正常")
    else:
        print("警告: Token 中可能缺少常見的特殊字符 (/, +, =)")
        
    # 使用該 token 嘗試獲取 LINE 的 bot 資訊
    try:
        print("測試 Token 是否有效...")
        configuration = Configuration(access_token=token)
        api_client = ApiClient(configuration)
        line_bot_api = MessagingApi(api_client)
        
        # 嘗試發送一條測試訊息到自己
        LINE_USER_ID = os.getenv('LINE_USER_ID')
        if LINE_USER_ID:
            print(f"使用者 ID: {LINE_USER_ID}")
            test_message = TextMessage(text=f"Token 驗證測試 {datetime.now().strftime('%H:%M:%S')}")
            
            line_bot_api.push_message(
                PushMessageRequest(
                    to=LINE_USER_ID,
                    messages=[test_message]
                )
            )
            print("測試訊息發送成功！Token 有效")
        else:
            print("沒有找到 LINE_USER_ID 環境變數，無法發送測試訊息")
            
    except Exception as e:
        print(f"Token 驗證失敗: {str(e)}")
        print("請更新 .env 文件中的 LINE_CHANNEL_ACCESS_TOKEN")

if __name__ == "__main__":
    check_token_length()
