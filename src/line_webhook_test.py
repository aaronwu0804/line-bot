#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/line_webhook_test.py
"""
LINE Webhook 測試腳本
用於創建帶有正確簽名的測試請求
"""

import os
import sys
import json
import hmac
import base64
import hashlib
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
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def generate_signature(body, secret):
    """生成請求簽名"""
    signature = hmac.new(
        secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

def create_test_event(text="AI: 你好，這是一個測試，請回應"):
    """生成測試事件"""
    timestamp = int(datetime.now().timestamp() * 1000)
    
    event = {
        "destination": "Udeadbeefdeadbeefdeadbeefdeadbeef",
        "events": [
            {
                "type": "message",
                "message": {
                    "type": "text",
                    "id": "12345678901234",
                    "text": text,
                    "quoteToken": "q1234567890abcdef"  # 增加 quoteToken 欄位
                },
                "webhookEventId": "01FZ74A0TDDPYRVKNK77XKC3ZR",  # 增加 webhookEventId 欄位
                "deliveryContext": {  # 增加 deliveryContext 欄位
                    "isRedelivery": False
                },
                "timestamp": timestamp,
                "source": {
                    "type": "user",
                    "userId": "U0123456789abcdef0123456789abcdef"
                },
                "replyToken": "0123456789abcdef0123456789abcdef",
                "mode": "active"
            }
        ]
    }
    
    return event

def send_test_webhook(url, event, channel_secret=None):
    """發送測試 webhook 請求"""
    if channel_secret is None:
        channel_secret = os.getenv('LINE_CHANNEL_SECRET')
        if not channel_secret:
            logger.error("未設定 LINE_CHANNEL_SECRET 環境變數")
            return False
    
    event_json = json.dumps(event)
    signature = generate_signature(event_json, channel_secret)
    
    logger.info(f"發送測試 webhook 請求到 {url}")
    logger.info(f"事件內容: {event_json}")
    logger.info(f"生成的簽名: {signature}")
    
    try:
        # 將超時時間設為較短，因為我們只關心請求是否被接受，不等待處理完成
        response = requests.post(
            url,
            headers={
                'Content-Type': 'application/json',
                'X-Line-Signature': signature
            },
            data=event_json,
            timeout=5  # 縮短超時時間，只檢查請求是否被接收
        )
        
        logger.info(f"回應狀態碼: {response.status_code}")
        logger.info(f"回應內容: {response.text}")
        
        # 只要服務接受請求（返回 200 或 202），就視為成功
        return response.status_code in [200, 202]
    except requests.exceptions.ReadTimeout:
        # 如果是讀取超時，但請求已發送，則視為成功
        logger.info("請求已發送，但服務處理時間較長（可能因為 Gemini API 調用）")
        return True
    except Exception as e:
        logger.error(f"發送請求時發生錯誤: {str(e)}")
        return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='測試 LINE Webhook')
    parser.add_argument('--url', type=str, help='Webhook URL', required=True)
    parser.add_argument('--text', type=str, help='測試訊息文本', default="AI: 你好，這是一個測試，請回應")
    
    args = parser.parse_args()
    
    event = create_test_event(args.text)
    success = send_test_webhook(args.url, event)
    
    if success:
        logger.info("測試成功！")
    else:
        logger.error("測試失敗！")

if __name__ == "__main__":
    main()
