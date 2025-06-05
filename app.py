#!/usr/bin/env python3
"""
智能回應版 - LINE Bot Webhook 服務
使用 Gemini API 提供智能 AI 回應
整合所有功能於單一文件
"""

import os
import sys
import time
import datetime
import threading
import logging
import requests
import random
from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

print("="*80)
print(f"啟動 LINE Bot Webhook 智能回應服務 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("整合版(智能版) - 直接從app.py啟動，避免LINE SDK衝突")
print("整合Gemini AI回應，提供智能對話功能")
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
# 獲取Gemini API金鑰 - 注意兩種可能的環境變數名稱
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_KEY')

# 檢查並載入Gemini API
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("Gemini API已成功載入")
    except ImportError:
        logger.warning("未能載入google-generativeai套件，AI回應功能將受限")
        logger.warning("請確認已安裝該套件：pip install google-generativeai>=0.3.1")
else:
    logger.warning("未設置Gemini API金鑰，將使用備用回應系統")

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
    # 使用預設URL如果未設定環境變數
    service_url = RENDER_SERVICE_URL or "https://line-bot-pikj.onrender.com"
    
    # 確保URL格式正確
    if not service_url.startswith(('http://', 'https://')):
        service_url = f"https://{service_url}"
    
    health_url = f"{service_url}/health"
    logger.info(f"啟動自我保活機制，每10分鐘ping一次: {health_url}")
    
    # 等待30秒讓應用完全啟動
    time.sleep(30)
    
    # 初始ping測試
    try:
        logger.info("[自我保活] 初始ping測試")
        response = requests.get(health_url, timeout=5)
        logger.info(f"[自我保活] 初始ping回應: {response.status_code}")
    except Exception as e:
        logger.error(f"[自我保活] 初始ping錯誤: {e}")
    
    # 主要ping循環 - 每10分鐘一次
    while True:
        try:
            logger.info(f"[自我保活] Pinging {health_url}")
            response = requests.get(health_url, timeout=5)
            logger.info(f"[自我保活] 收到回應: {response.status_code}")
        except Exception as e:
            logger.error(f"[自我保活] 錯誤: {e}")
        
        # 休眠10分鐘（Render Free Tier休眠時間為15分鐘）
        time.sleep(10 * 60)

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
    now = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
    return f"""
    <html>
    <head><title>智能回應版LINE Bot</title></head>
    <body>
        <h1>LINE Bot Webhook服務 - 智能回應版</h1>
        <p>目前時間: {now}</p>
        <p>這是一個智能回應版LINE Bot，整合Gemini API提供智能AI回應。</p>
        <p>狀態: 運行中</p>
        <p>Gemini API: {'已啟用' if GEMINI_API_KEY else '未啟用'}</p>
        <hr>
        <h2>鉛一：測試用LINE Bot</h2>
    </body>
    </html>
    """

@app.route("/health", methods=['GET'])
def health():
    """健康檢查"""
    status = "ok" if LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET else "warning"
    message = "LINE Bot Webhook service is running (Smart Response Version)"
    if status == "warning":
        message += " - MISSING CREDENTIALS"
    
    return jsonify({
        "status": status,
        "message": message,
        "version": "2.0.0",
        "timestamp": str(os.popen('date').read().strip()),
        "environment": {
            "LINE_CHANNEL_ACCESS_TOKEN": "configured" if LINE_CHANNEL_ACCESS_TOKEN else "missing",
            "LINE_CHANNEL_SECRET": "configured" if LINE_CHANNEL_SECRET else "missing",
            "GEMINI_API": "configured" if GEMINI_API_KEY else "disabled"
        }
    })

# 預先定義的回應模板
weather_response = """
根據我的了解，我無法實時查詢天氣資訊，但您可以：
1. 使用「台灣氣象局」官方網站查詢最新天氣
2. 下載「氣象局」官方APP隨時掌握最新天氣資訊
3. 查看新聞網站的天氣專區

您也可以告訴我更具體的問題，我會盡力協助您。
"""

time_response = """
現在的時間是：{current_time}

祝您有美好的一天！
""".format(current_time=datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))

greeting_response = """
你好！很高興與你交流。
我是一個AI助手，有什麼我可以幫助你的嗎？
"""

self_intro_response = """
我是一個由鉛一開發的AI助手，
目前整合了Gemini API，可以回答各種問題。
很高興能夠為您服務！
"""

help_response = """
👋 您好！我可以提供以下幫助：

1️⃣ 回答知識性問題
2️⃣ 提供簡單資訊查詢
3️⃣ 協助進行文字處理或翻譯
4️⃣ 進行友好的對話交流

使用方式：請在訊息前加上「AI:」或「@AI」前綴，例如：
「AI: 請介紹台灣的夜市文化」

希望能為您提供有用的幫助！
"""

def get_ai_response(message):
    """獲取AI回應"""
    # 提取用戶問題 (移除AI前綴)
    user_question = message
    for prefix in ['ai:', 'ai：', '@ai ', '@ai', 'ai ']:
        if user_question.lower().startswith(prefix):
            user_question = user_question[len(prefix):]
            break
    user_question = user_question.strip()
    
    # 嘗試使用Gemini API (如果可用)
    try:
        if GEMINI_API_KEY and 'genai' in globals():
            # 初始化生成式模型
            model = genai.GenerativeModel('gemini-pro')
            
            # 添加提示詞引導回答風格和語言
            prompt = f"""請以友好、專業、簡潔的方式用繁體中文回答以下問題。
如果問題涉及敏感內容或有害內容，請禮貌拒絕並解釋原因。
問題: {user_question}"""
            
            # 生成回應
            try:
                response = model.generate_content(prompt)
                if response and hasattr(response, 'text') and response.text:
                    return response.text
            except Exception as e:
                logger.error(f"生成Gemini回應時出錯: {str(e)}")
                # 繼續使用備用系統
    except Exception as e:
        logger.error(f"調用Gemini API時出錯: {str(e)}")
    
    # 備用系統：關鍵字回應
    question_lower = user_question.lower()
    
    # 天氣相關問題
    if any(keyword in question_lower for keyword in ['天氣', '下雨', '氣象', '溫度']):
        return weather_response
    
    # 時間相關問題
    if any(keyword in question_lower for keyword in ['時間', '日期', '現在幾點', '今天幾號']):
        return time_response
    
    # 問候相關問題
    if any(keyword in question_lower for keyword in ['你好', '嗨', '哈囉', 'hi', 'hello']):
        return greeting_response
    
    # 自我介紹相關問題
    if any(keyword in question_lower for keyword in ['你是誰', '介紹自己', '自我介紹', '關於你']):
        return self_intro_response
    
    # 尋求幫助相關問題
    if any(keyword in question_lower for keyword in ['幫助', '怎麼用', '如何使用', 'help', '指令']):
        return help_response
    
    # 預設回應
    return f"""您的問題：{user_question}\n\n我已收到您的問題。我會盡力提供有用的回答！"""

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
        logger.info("檢測到AI請求，正在處理...")
        try:
            # 獲取AI回應
            start_time = time.time()
            ai_response = get_ai_response(user_message)
            process_time = time.time() - start_time
            logger.info(f"生成AI回應完成，耗時 {process_time:.2f} 秒")
            
            # 檢查回應是否為空
            if not ai_response:
                ai_response = "抱歉，我目前無法回答這個問題。請稍後再試。"
            
            # 回覆訊息
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                
                # 發送回覆
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=[TextMessage(text=ai_response)]
                    )
                )
                logger.info("已回覆AI請求")
            
        except Exception as e:
            logger.error(f"回覆AI訊息時出錯: {str(e)}")
            try:
                # 嘗試發送錯誤回覆
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    error_message = "抱歉，處理您的請求時發生錯誤，請稍後再試。"
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=reply_token,
                            messages=[TextMessage(text=error_message)]
                        )
                    )
            except Exception as reply_error:
                logger.error(f"發送錯誤回覆時出錯: {str(reply_error)}")
    else:
        logger.info("非AI請求，不處理")

# 讓gunicorn能夠找到應用
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"在端口 {port} 啟動應用")
    app.run(host='0.0.0.0', port=port)
