#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/line_webhook.py
"""
LINE Bot Webhook 處理模組
用於接收和處理 LINE Bot 的訊息
支援與 Gemini AI 對話功能
包含回應緩存和流量限制功能
"""

import os
import sys
import logging
import time
import traceback
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# 設置系統路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 設定日誌
log_path = os.path.join(parent_dir, 'logs', 'line_webhook.log')
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

# 導入 Gemini 服務
try:
    from src.gemini_service import get_gemini_response
except ImportError:
    try:
        from gemini_service import get_gemini_response
    except ImportError:
        logger.error("無法導入 Gemini 服務，請檢查路徑")
        # 定義一個備用函數
        def get_gemini_response(prompt, conversation_history=None):
            return "抱歉，Gemini 服務目前無法使用。請稍後再試。"

# 載入環境變數
load_dotenv()

app = Flask(__name__)

# 設置 LINE Bot API
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# 對話歷史紀錄儲存
# 使用使用者ID作為鍵，儲存該使用者的對話歷史
conversation_histories = {}

@app.route("/webhook", methods=['POST'])
def webhook():
    """LINE Webhook 回調入口點"""
    logger.info("=== webhook 函數開始執行 ===")
    
    try:
        # 獲取 X-Line-Signature 標頭
        signature = request.headers.get('X-Line-Signature')
        if not signature:
            logger.error("缺少 X-Line-Signature 標頭")
            return 'Missing signature', 400
            
        # 獲取請求主體
        body = request.get_data(as_text=True)
        logger.info("接收到 webhook 事件: %s", body)
        logger.info("請求標頭: %s", dict(request.headers))

        # 處理 webhook 請求主體
        try:
            handler.handle(body, signature)
            logger.info("webhook 事件處理成功")
        except InvalidSignatureError:
            logger.error("無效的簽名")
            return 'Invalid signature', 400
        except Exception as e:
            logger.error(f"處理 webhook 事件時發生未預期錯誤: {str(e)}")
            logger.error(traceback.format_exc())
            # 返回 200 以避免 LINE 重試
            return 'Error occurred but acknowledged', 200
            
        logger.info("=== webhook 函數執行完畢 ===")
        return 'OK', 200
    except Exception as e:
        logger.error(f"webhook 函數發生嚴重錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return 'Server error', 500

@app.route("/callback", methods=['POST'])
def callback():
    """與 webhook 兼容的路由，用於支持 LINE 平台的標準路徑"""
    logger.info("接收到 /callback 路徑的請求，轉發到 webhook 處理函數")
    return webhook()

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    """處理文字訊息"""
    try:
        logger.info(f"=== 開始處理文字訊息 ===")
        logger.info(f"收到訊息: {event}")
        
        user_id = event.source.user_id
        user_message = event.message.text
        
        logger.info(f"用戶 {user_id} 傳送訊息: {user_message}")
        
        # 檢查訊息是否為 AI 對話請求
        if is_ai_request(user_message):
            logger.info(f"識別為 AI 請求")
            
            # 取出真實查詢內容（去除前綴）
            query = extract_query(user_message)
            logger.info(f"提取的查詢: {query}")
            
            # 獲取或初始化對話歷史
            conversation_history = conversation_histories.get(user_id, [])
            
            try:
                # 調用 Gemini 服務獲取回應
                logger.info(f"調用 Gemini API")
                ai_response = get_gemini_response(query, conversation_history)
                logger.info(f"Gemini 回應: {ai_response[:100] if len(ai_response) > 100 else ai_response}...")
                
                # 更新對話歷史
                update_conversation_history(user_id, query, ai_response)
                
                # 回覆訊息
                logger.info(f"回覆訊息給用戶")
                reply_to_user(event.reply_token, ai_response)
                
            except Exception as e:
                logger.error(f"處理 AI 回應時發生錯誤: {str(e)}")
                logger.error(traceback.format_exc())
                reply_to_user(event.reply_token, "抱歉，處理您的請求時出現了問題，請稍後再試。")
        else:
            logger.info(f"非 AI 請求，回覆幫助訊息")
            # 非 AI 請求，可以提供說明或其他功能回應
            reply_to_user(event.reply_token, get_help_message())
            
        logger.info(f"=== 文字訊息處理完成 ===")
    except Exception as e:
        logger.error(f"處理訊息過程中發生嚴重錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        try:
            reply_to_user(event.reply_token, "抱歉，系統發生錯誤，請聯絡管理員。")
        except Exception as ex:
            logger.error(f"嘗試發送錯誤消息時也失敗: {str(ex)}")
            logger.error(traceback.format_exc())

def is_ai_request(message):
    """檢查是否為 AI 對話請求
    
    目前的判斷邏輯：訊息以 'AI:' 或 'ai:' 開頭
    """
    return message.lower().startswith(('ai:', 'ai：')) or message.lower().startswith('@ai')

def extract_query(message):
    """從訊息中提取實際查詢內容"""
    message = message.strip()
    
    if message.lower().startswith('ai:'):
        return message[3:].strip()
    elif message.lower().startswith('ai：'):  # 中文冒號
        return message[3:].strip()
    elif message.lower().startswith('@ai'):
        return message[3:].strip()
    return message

def update_conversation_history(user_id, query, response):
    """更新使用者的對話歷史記錄
    
    目前的實作是保留最近 10 輪對話
    """
    MAX_HISTORY = 10
    
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []
    
    # 添加新的對話
    conversation_histories[user_id].append({"role": "user", "parts": [query]})
    conversation_histories[user_id].append({"role": "model", "parts": [response]})
    
    # 如果歷史紀錄太長，移除最舊的對話
    if len(conversation_histories[user_id]) > MAX_HISTORY * 2:  # 一輪對話有兩條紀錄
        conversation_histories[user_id] = conversation_histories[user_id][-MAX_HISTORY*2:]

def reply_to_user(reply_token, message):
    """回覆使用者訊息"""
    if not reply_token:
        logger.error("無法回覆：reply_token 為空")
        return False
    
    if not message:
        logger.error("無法回覆：message 為空")
        return False
        
    try:
        logger.info(f"開始回覆訊息，reply_token: {reply_token[:10] if len(reply_token) > 10 else reply_token}...")
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            
            # 如果消息太長，分段發送
            if len(message) > 5000:
                logger.info(f"訊息過長 ({len(message)} 字符)，進行分段")
                messages = split_long_message(message)
                logger.info(f"分為 {len(messages)} 段，發送第一段")
                
                response = line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=[TextMessage(text=messages[0])]
                    )
                )
                logger.info(f"成功發送第一段回覆")
            else:
                logger.info(f"發送訊息，長度 {len(message)} 字符")
                response = line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=[TextMessage(text=message)]
                    )
                )
                logger.info(f"成功發送回覆")
                
        return True
    except Exception as e:
        logger.error(f"回覆訊息時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def split_long_message(message, max_length=5000):
    """將長訊息分割成多個部分"""
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]

def get_help_message():
    """產生使用說明訊息"""
    return (
        "👋 歡迎使用智能早安助理！\n\n"
        "📅 我會在每個工作日早上 7:00 和週末早上 8:00 自動發送早安問候和天氣預報。\n\n"
        "💬 我還可以幫您回答各種問題！使用方式如下：\n"
        "- 輸入「AI: 您的問題」(例如：AI: 推薦幾本好書)\n"
        "- 或輸入「@AI 您的問題」(例如：@AI 今天的天氣如何？)\n\n"
        "💡 我具備上下文理解功能，可連續對話，讓您的交流更加自然流暢！\n"
    )

def clear_user_history(user_id):
    """清除特定用戶的對話歷史"""
    if user_id in conversation_histories:
        del conversation_histories[user_id]
        return True
    return False

@app.route("/health", methods=['GET'])
def health_check():
    """健康檢查 API 端點，用於防止 Render 服務休眠"""
    return jsonify({"status": "ok", "message": "LINE Bot Webhook service is running"})

@app.route("/", methods=['GET'])
def home():
    """首頁，顯示簡單的服務資訊"""
    return jsonify({
        "service": "LINE Bot Webhook with Gemini AI",
        "version": "1.0.0",
        "status": "running"
    })

if __name__ == "__main__":
    # 本機測試用，實際部署時應使用 WSGI 伺服器
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
