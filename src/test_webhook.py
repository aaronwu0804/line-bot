#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/test_webhook.py
"""
測試 LINE Webhook 服務的腳本
用於模擬 LINE 平台發送的請求，方便本地調試
"""

import os
import sys
import json
import logging
import requests
import argparse
from datetime import datetime
from dotenv import load_dotenv

# 設置系統路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

# 從 LINE 文檔中參考的示例訊息格式
def generate_text_message_event(text, user_id=None):
    """生成模擬的 LINE 文字訊息事件 JSON"""
    if user_id is None:
        user_id = os.getenv('LINE_USER_ID', 'U0123456789abcdef0123456789abcdef')
    
    timestamp = int(datetime.now().timestamp() * 1000)
    
    return {
        "destination": "Udeadbeefdeadbeefdeadbeefdeadbeef",
        "events": [
            {
                "type": "message",
                "message": {
                    "type": "text",
                    "id": "12345678901234",
                    "text": text
                },
                "timestamp": timestamp,
                "source": {
                    "type": "user",
                    "userId": user_id
                },
                "replyToken": "0123456789abcdef0123456789abcdef",
                "mode": "active"
            }
        ]
    }

def send_test_request(webhook_url, is_ai_request=False, text=None):
    """發送測試請求到 webhook URL"""
    channel_secret = os.getenv('LINE_CHANNEL_SECRET')
    if not channel_secret:
        logger.error("未設定 LINE_CHANNEL_SECRET 環境變數")
        return False
    
    # 準備訊息文本
    if text is None:
        if is_ai_request:
            text = "AI: 你好，這是一個測試訊息"
        else:
            text = "你好，這是一個普通的測試訊息"
    
    # 生成 event payload
    payload = generate_text_message_event(text)
    payload_json = json.dumps(payload)
    
    logger.info(f"發送測試請求到 {webhook_url}")
    logger.info(f"載荷: {payload_json}")
    
    # 發送請求
    try:
        # 在實際場景中，LINE 平台會使用 channel secret 計算簽名
        # 但這裡為了簡化，我們省略了簽名部分
        response = requests.post(
            webhook_url,
            headers={
                'Content-Type': 'application/json',
                'X-Line-Signature': 'dummy_signature'  # 實際部署時需要正確簽名
            },
            data=payload_json
        )
        
        logger.info(f"響應狀態碼: {response.status_code}")
        logger.info(f"響應內容: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        logger.error(f"發送請求時發生錯誤: {str(e)}")
        return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='測試 LINE Webhook 服務')
    parser.add_argument('--url', type=str, help='webhook URL', default='http://localhost:5000/callback')
    parser.add_argument('--ai', action='store_true', help='發送 AI 請求')
    parser.add_argument('--text', type=str, help='自定義訊息文本')
    
    args = parser.parse_args()
    
    success = send_test_request(args.url, args.ai, args.text)
    
    if success:
        logger.info("測試成功！")
    else:
        logger.error("測試失敗！")

if __name__ == "__main__":
    main()
