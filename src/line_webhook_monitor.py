#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/line_webhook_monitor.py
"""
LINE Bot Webhook 監控工具
用於監控和測試 LINE Bot Webhook 的健康狀態和功能
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

# 設置系統路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 設定日誌
log_path = os.path.join(parent_dir, 'logs', 'line_webhook_monitor.log')
# 確保 logs 資料夾存在
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

# 設定 LINE Bot API 認證
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
WEBHOOK_URL = os.getenv('RENDER_SERVICE_URL')

def check_environment_vars():
    """檢查必要的環境變數是否已設定"""
    missing_vars = []
    if not CHANNEL_ACCESS_TOKEN:
        missing_vars.append('LINE_CHANNEL_ACCESS_TOKEN')
    if not CHANNEL_SECRET:
        missing_vars.append('LINE_CHANNEL_SECRET')
    if not WEBHOOK_URL:
        missing_vars.append('RENDER_SERVICE_URL')
    
    if missing_vars:
        logger.error(f"缺少環境變數: {', '.join(missing_vars)}")
        return False
    return True

def check_webhook_health():
    """檢查 webhook 服務健康狀況"""
    health_url = f"{WEBHOOK_URL}/health" if WEBHOOK_URL else None
    
    if not health_url:
        logger.error("未設定 WEBHOOK_URL，無法檢查健康狀況")
        return False
    
    try:
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            logger.info(f"Webhook 健康檢查成功: {response.json()}")
            return True
        else:
            logger.error(f"Webhook 健康檢查失敗，HTTP 狀態碼: {response.status_code}")
            logger.error(f"回應內容: {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"無法連接到 webhook 服務: {str(e)}")
        return False

def test_webhook_connection():
    """測試是否可以連接到 webhook 端點"""
    webhook_url = f"{WEBHOOK_URL}/webhook" if WEBHOOK_URL else None
    callback_url = f"{WEBHOOK_URL}/callback" if WEBHOOK_URL else None
    
    if not webhook_url or not callback_url:
        logger.error("未設定 WEBHOOK_URL，無法測試連接")
        return False
    
    # 測試 /webhook 端點
    try:
        response = requests.get(webhook_url, timeout=10)
        logger.info(f"/webhook 端點回應: {response.status_code} - {response.reason}")
    except requests.RequestException as e:
        logger.error(f"無法連接到 /webhook 端點: {str(e)}")
    
    # 測試 /callback 端點
    try:
        response = requests.get(callback_url, timeout=10)
        logger.info(f"/callback 端點回應: {response.status_code} - {response.reason}")
    except requests.RequestException as e:
        logger.error(f"無法連接到 /callback 端點: {str(e)}")

def simulate_webhook_event():
    """模擬發送 webhook 事件"""
    if not (WEBHOOK_URL and CHANNEL_SECRET):
        logger.error("缺少必要的環境變數，無法模擬 webhook 事件")
        return
    
    callback_url = f"{WEBHOOK_URL}/callback"
    
    # 創建模擬的 webhook 事件
    current_timestamp = int(time.time() * 1000)
    event = {
        "destination": "xxxxxxxxxx",
        "events": [
            {
                "replyToken": "00000000000000000000000000000000",
                "type": "message",
                "mode": "active",
                "timestamp": current_timestamp,
                "source": {
                    "type": "user",
                    "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"
                },
                "message": {
                    "id": "100001",
                    "type": "text",
                    "text": "AI: 測試訊息"
                },
                "webhookEventId": f"test-event-{current_timestamp}",
                "deliveryContext": {
                    "isRedelivery": False
                },
                "quoteToken": "test-token-123456"
            }
        ]
    }
    
    # 準備請求
    body = json.dumps(event)
    
    # 產生簽名 (需要實作)
    # 注意：這裡僅做示意，實際生產中應該使用適當的簽名生成算法
    import hashlib
    import hmac
    import base64
    
    signature = base64.b64encode(
        hmac.new(
            CHANNEL_SECRET.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    headers = {
        'Content-Type': 'application/json',
        'X-Line-Signature': signature
    }
    
    try:
        logger.info(f"發送模擬 webhook 事件到 {callback_url}")
        logger.info(f"事件內容: {body}")
        
        response = requests.post(
            callback_url,
            headers=headers,
            data=body,
            timeout=30
        )
        
        logger.info(f"回應狀態碼: {response.status_code}")
        logger.info(f"回應內容: {response.text}")
        
        if response.status_code == 200:
            logger.info("模擬 webhook 事件發送成功")
            return True
        else:
            logger.error(f"模擬 webhook 事件發送失敗: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"發送模擬 webhook 事件時發生錯誤: {str(e)}")
        return False

def monitor_logs():
    """監控 webhook 日誌"""
    log_file = os.path.join(parent_dir, 'logs', 'line_webhook.log')
    
    try:
        with open(log_file, 'r') as file:
            # 移動到文件末尾
            file.seek(0, 2)
            
            print(f"監控日誌文件: {log_file}")
            print("按 Ctrl+C 停止監控...")
            
            while True:
                line = file.readline()
                if line:
                    print(line, end='')
                else:
                    time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n已停止日誌監控")
    except FileNotFoundError:
        logger.error(f"找不到日誌文件: {log_file}")
        print(f"找不到日誌文件: {log_file}")

def show_menu():
    """顯示主選單"""
    print("\n" + "="*50)
    print(" LINE Bot Webhook 監控工具 ".center(50, "="))
    print("="*50)
    print("1. 檢查環境變數")
    print("2. 檢查 webhook 健康狀況")
    print("3. 測試 webhook 連接")
    print("4. 發送模擬 webhook 事件")
    print("5. 監控日誌")
    print("0. 退出")
    print("="*50)
    
    choice = input("請選擇操作 [0-5]: ")
    return choice

def main():
    """主函數"""
    while True:
        choice = show_menu()
        
        if choice == '1':
            if check_environment_vars():
                print("\n✅ 所有環境變數已正確設定")
            else:
                print("\n❌ 某些環境變數未設定，請檢查")
        elif choice == '2':
            if check_webhook_health():
                print("\n✅ Webhook 服務運行正常")
            else:
                print("\n❌ Webhook 服務狀態異常，請檢查日誌")
        elif choice == '3':
            test_webhook_connection()
            print("\n🔍 連接測試完成，請查看日誌了解詳情")
        elif choice == '4':
            if simulate_webhook_event():
                print("\n✅ 模擬事件發送成功")
            else:
                print("\n❌ 模擬事件發送失敗，請檢查日誌")
        elif choice == '5':
            monitor_logs()
        elif choice == '0':
            print("\n感謝使用！再見👋")
            break
        else:
            print("\n❗ 無效選擇，請重試")
        
        input("\n按 Enter 繼續...")

if __name__ == "__main__":
    main()
