#!/usr/bin/env python3
"""
應急修複腳本 - 用於從LINE SDK範例混亂中恢復
此腳本提供了一個最小化的LINE Bot實現
"""

import os
import sys
import logging
from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# 初始化Flask應用
app = Flask(__name__)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 環境變數
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    logger.error("缺少LINE API憑證")
    logger.error("請設置環境變數: LINE_CHANNEL_ACCESS_TOKEN和LINE_CHANNEL_SECRET")
    # 對於開發環境，設置一些虛擬值以便腳本能夠啟動
    if os.getenv('FLASK_ENV') == 'development' or os.getenv('ENV') == 'development':
        logger.warning("開發環境檢測: 設置虛擬的LINE API憑證")
        LINE_CHANNEL_ACCESS_TOKEN = "DUMMY_ACCESS_TOKEN"
        LINE_CHANNEL_SECRET = "DUMMY_SECRET"

# LINE Bot API設置
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

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
    </body>
    </html>
    """

@app.route("/health", methods=['GET'])
def health():
    """健康檢查"""
    return jsonify({
        "status": "ok",
        "message": "LINE Bot Webhook service is running (Emergency Fix Version)",
        "timestamp": str(os.popen('date').read().strip())
    })

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
    is_ai_request = user_message.lower().startswith(('ai:', 'ai：', '@ai', 'ai ')) or user_message.lower() == 'ai'
    
    if is_ai_request:
        # 擷取真實查詢內容
        if user_message.lower().startswith('ai:'):
            query = user_message[3:].strip()
        elif user_message.lower().startswith('ai：'):
            query = user_message[3:].strip()
        elif user_message.lower().startswith('@ai'):
            query = user_message[3:].strip()
        elif user_message.lower().startswith('ai '):
            query = user_message[3:].strip()
        elif user_message.lower() == 'ai':
            query = "您好，有什麼我能幫您的嗎？"
        else:
            query = user_message
        
        # 發送簡單回應
        reply = f"我收到了您的AI請求: {query}\n(這是一個緊急修復版本，完整的AI功能即將恢復)"
    else:
        # 非AI請求的回應
        reply = (
            "您好！我是LINE Bot。使用方式:\n"
            "1. 輸入「AI: 您的問題」來使用AI聊天功能\n"
            "2. 輸入「!清空」來清除對話歷史\n"
            "目前運行的是緊急修復版，完整功能即將恢復。"
        )
    
    # 回覆訊息
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=reply)]
                )
            )
            logger.info("已發送回覆")
    except Exception as e:
        logger.error("發送回覆時出錯: %s", e)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logger.info("在端口 %s 上啟動緊急修復版LINE Bot", port)
    app.run(host='0.0.0.0', port=port)
