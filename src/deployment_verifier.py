#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/deployment_verifier.py
"""
部署驗證工具
用於檢查 LINE Bot Webhook 服務部署是否正確
並檢查各個組件是否正常工作
"""

import os
import sys
import json
import logging
import argparse
import requests
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

def check_env_vars():
    """檢查必要的環境變數是否已設定"""
    required_vars = [
        'LINE_CHANNEL_ACCESS_TOKEN',
        'LINE_CHANNEL_SECRET',
        'GEMINI_API_KEY',
        'RENDER_SERVICE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"缺少以下環境變數: {', '.join(missing_vars)}")
        return False
    
    logger.info("環境變數檢查通過")
    return True

def test_gemini_api():
    """測試 Gemini API 是否正常工作"""
    try:
        from src.gemini_service import get_gemini_response
    except ImportError:
        try:
            from gemini_service import get_gemini_response
        except ImportError:
            logger.error("無法導入 Gemini 服務，請檢查路徑")
            return False
            
    try:
        logger.info("測試 Gemini API...")
        response = get_gemini_response("Hello, please respond with 'Gemini API is working' in Traditional Chinese")
        logger.info(f"Gemini API 回應: {response}")
        
        if response and len(response) > 0 and "Gemini" in response:
            logger.info("Gemini API 測試成功")
            return True
        else:
            logger.error("Gemini API 測試失敗: 回應內容不符合預期")
            return False
    except Exception as e:
        logger.error(f"Gemini API 測試失敗: {str(e)}")
        return False

def test_webhook_endpoint(url=None):
    """測試 Webhook 端點是否可訪問"""
    if url is None:
        service_url = os.getenv('RENDER_SERVICE_URL')
        if not service_url:
            logger.error("未設定 RENDER_SERVICE_URL 環境變數")
            return False
        url = f"{service_url}/callback"
    
    logger.info(f"測試 Webhook 端點: {url}")
    
    try:
        # 測試 webhook 端點的健康狀態
        health_url = url.replace('/callback', '/health')
        logger.info(f"檢查健康端點: {health_url}")
        health_response = requests.get(health_url, timeout=10)
        
        if health_response.status_code == 200:
            logger.info(f"健康端點返回 200 OK: {health_response.text}")
        else:
            logger.warning(f"健康端點返回非 200 狀態碼: {health_response.status_code}")
        
        # 測試 webhook 端點能否處理 POST 請求
        logger.info(f"檢查 Webhook 端點: {url}...")
        
        # 簡單的測試負載，不包含有效的簽名
        test_payload = {
            "destination": "test",
            "events": [
                {
                    "type": "message",
                    "message": {
                        "type": "text",
                        "id": "12345",
                        "text": "This is a test message"
                    },
                    "source": {
                        "type": "user",
                        "userId": "test_user"
                    },
                    "replyToken": "test_token",
                    "timestamp": 1625097600000
                }
            ]
        }
        
        # 我們預期這會因為簽名無效而失敗，但至少應該返回 400 而不是連接錯誤
        try:
            webhook_response = requests.post(
                url, 
                headers={'Content-Type': 'application/json'},
                data=json.dumps(test_payload),
                timeout=10
            )
            
            logger.info(f"Webhook 端點返回狀態碼: {webhook_response.status_code}")
            logger.info(f"Webhook 端點返回內容: {webhook_response.text}")
            
            # 預期返回 400 (簽名驗證失敗)，這表明 webhook 端點存在並在處理請求
            if webhook_response.status_code in [400, 401, 403]:
                logger.info("Webhook 端點檢查通過: 返回預期的驗證失敗狀態碼")
                return True
            elif webhook_response.status_code == 200:
                logger.warning("Webhook 端點返回 200 狀態碼，這可能表示簽名驗證被跳過了")
                return True
            else:
                logger.warning(f"Webhook 端點返回非預期狀態碼: {webhook_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"測試 Webhook 端點時發生錯誤: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"測試 Webhook 端點時發生錯誤: {str(e)}")
        return False

def test_line_api():
    """測試 LINE Messaging API 是否能夠發送訊息"""
    from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, PushMessageRequest, TextMessage
    from datetime import datetime
    
    channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    user_id = os.getenv('LINE_USER_ID')
    
    if not channel_access_token:
        logger.error("未設定 LINE_CHANNEL_ACCESS_TOKEN 環境變數")
        return False
        
    if not user_id:
        logger.error("未設定 LINE_USER_ID 環境變數，無法測試發送訊息功能")
        return False
        
    logger.info(f"測試 LINE Messaging API...")
    
    try:
        configuration = Configuration(access_token=channel_access_token)
        
        message = f"這是一條測試訊息，發送時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=[TextMessage(text=message)]
                )
            )
        
        logger.info("LINE Messaging API 測試成功")
        return True
    except Exception as e:
        logger.error(f"LINE Messaging API 測試失敗: {str(e)}")
        return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='驗證 LINE Bot Webhook 服務部署')
    parser.add_argument('--url', type=str, help='Webhook URL', default=None)
    parser.add_argument('--gemini', action='store_true', help='測試 Gemini API')
    parser.add_argument('--webhook', action='store_true', help='測試 Webhook 端點')
    parser.add_argument('--line', action='store_true', help='測試 LINE Messaging API')
    parser.add_argument('--all', action='store_true', help='執行所有測試')
    
    args = parser.parse_args()
    
    if not (args.gemini or args.webhook or args.line or args.all):
        logger.info("未指定測試項目，將執行所有測試")
        args.all = True
        
    # 檢查環境變數
    check_env_vars()
    
    # 執行測試
    if args.gemini or args.all:
        test_gemini_api()
        
    if args.webhook or args.all:
        test_webhook_endpoint(args.url)
        
    if args.line or args.all:
        test_line_api()

if __name__ == "__main__":
    main()
