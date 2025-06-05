#!/usr/bin/env python3
"""
緊急修復版 - LINE Bot Webhook 服務
用於解決 Render 部署問題
直接整合所有功能於單一文件
"""

import os
import sys
import time
import threading
import logging
import requests
from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

print("="*80)
print("啟動 LINE Bot Webhook 緊急修復服務 - 2025年6月5日")
print("整合版(優化版) - 直接從app.py啟動，避免LINE SDK衝突")
print("添加自動保活機制，防止Render休眠")
print("="*80)

# 初始化Flask應用
app = Flask(__name__)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 載入環境變數
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("環境變數載入成功")
except Exception as e:
    logger.error(f"載入環境變數時發生錯誤: {str(e)}")

# 環境變數
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
RENDER_SERVICE_URL = os.getenv('RENDER_SERVICE_URL')

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    logger.error("缺少LINE API憑證")
    logger.error("請設置環境變數: LINE_CHANNEL_ACCESS_TOKEN和LINE_CHANNEL_SECRET")
    # 安全檢查 - 使用預設值以便測試
    if not os.getenv('RENDER', ''):  # 只在Render環境繼續執行
        LINE_CHANNEL_SECRET = "DUMMY_SECRET"
        LINE_CHANNEL_ACCESS_TOKEN = "DUMMY_TOKEN"
        logger.warning("使用虛擬憑證繼續執行 (僅供開發環境)")

# 自我保活機制
def self_ping_service():
    """定期ping自己以保持服務活躍的後台執行緒"""
    if not RENDER_SERVICE_URL:
        logger.warning("未設定RENDER_SERVICE_URL，自我保活機制未啟用")
        return

    service_url = RENDER_SERVICE_URL
    # 確保URL格式正確
    if not service_url.startswith(('http://', 'https://')):
        service_url = f"https://{service_url}"
    
    health_url = f"{service_url}/health"
    logger.info(f"啟動自我保活機制，每14分鐘ping一次: {health_url}")
    
    while True:
        try:
            logger.info(f"[自我保活] Pinging {health_url}")
            response = requests.get(health_url, timeout=10)
            logger.info(f"[自我保活] 收到回應: {response.status_code}")
        except Exception as e:
            logger.error(f"[自我保活] 錯誤: {e}")
        
        # 休眠14分鐘（Render Free Tier休眠時間為15分鐘）
        time.sleep(14 * 60)

# 在Render環境中啟動自我保活機制
if os.getenv('RENDER', ''):
    ping_thread = threading.Thread(target=self_ping_service, daemon=True)
    ping_thread.start()
    logger.info("自我保活機制已在後台啟動")

# LINE Bot API設置
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET or "dummy_secret_for_initialization")

@app.route("/", methods=['GET'])
def home():
    """首頁"""
    return """
    <html>
    <head><title>緊急修復版LINE Bot</title></head>
    <body>
        <h1>LINE Bot Webhook服務 - 緊急修復版</h1>
        <p>日期: 2025年6月5日</p>
        <p>這是一個緊急修復版LINE Bot，用於解決與LINE SDK範例的衝突問題。</p>
        <p>狀態: 運行中</p>
        <hr>
        <h2>鉛一：測試用LINE Bot</h2>
    </body>
    </html>
    """

@app.route("/health", methods=['GET'])
def health():
    """健康檢查"""
    status = "ok" if LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET else "warning"
    message = "LINE Bot Webhook service is running (Emergency Fix Version)"
    if status == "warning":
        message += " - MISSING CREDENTIALS"
    
    return jsonify({
        "status": status,
        "message": message,
        "timestamp": str(os.popen('date').read().strip()),
        "environment": {
            "LINE_CHANNEL_ACCESS_TOKEN": "configured" if LINE_CHANNEL_ACCESS_TOKEN else "missing",
            "LINE_CHANNEL_SECRET": "configured" if LINE_CHANNEL_SECRET else "missing"
        }
    })

def is_ai_request(message):
    """檢查是否為AI請求"""
    if not message:
        return False
    
    message_lower = message.lower().strip()
    return (message_lower.startswith(('ai:', 'ai：')) or 
            message_lower.startswith(('@ai', '@ai ')) or
            message_lower.startswith('ai ') or
            message_lower == 'ai')

@app.route("/callback", methods=['POST'])
def callback():
    """處理LINE Webhook回調"""
    logger.info("收到webhook回調")
    
    # 獲取X-Line-Signature標頭值
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        logger.error("缺少簽名")
        abort(400)
    
    # 獲取請求體
    body = request.get_data(as_text=True)
    logger.info("請求體: %s", body)
    
    # 處理webhook請求體
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("無效的簽名")
        abort(400)
    except Exception as e:
        logger.error("處理webhook時出錯: %s", e)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """處理文字訊息"""
    logger.info("收到訊息事件: %s", event)
    
    user_id = event.source.user_id
    user_message = event.message.text
    reply_token = event.reply_token
    
    logger.info("用戶 %s 發送訊息: %s", user_id, user_message)
    
    # 檢查是否為AI請求
    if is_ai_request(user_message):
        logger.info("檢測到AI請求")
        try:
            # 回覆訊息
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                
                # 處理AI請求
                ai_response = "我收到了你的AI請求：「{}」\n這是緊急修復版LINE Bot的回應".format(
                    user_message.replace("AI:", "").replace("ai:", "").strip()
                )
                
                # 發送回覆
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=[TextMessage(text=ai_response)]
                    )
                )
                logger.info("已回覆AI請求")
            
        except Exception as e:
            logger.error("回覆訊息時出錯: %s", e)
    else:
        logger.info("非AI請求，不處理")

# 讓gunicorn能夠找到應用
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"在端口 {port} 啟動應用")
    app.run(host='0.0.0.0', port=port)
