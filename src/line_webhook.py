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
    PushMessageRequest,
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

# 對話狀態追蹤
# 使用使用者ID作為鍵，紀錄用戶是否正在進行連續對話及最後互動時間
active_conversations = {}

# 連續對話超時時間（秒）
CONVERSATION_TIMEOUT = 300  # 5分鐘無互動後結束對話

# 對話歷史記錄上限
MAX_HISTORY = 10  # 保留最近10輪對話

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
        
        # 檢查用戶是否處於活躍對話狀態
        current_time = time.time()
        is_active_conversation = check_active_conversation(user_id, current_time)
        
        # 檢查是否要結束對話
        if user_message.lower().strip() in ['結束', '結束對話', '停止', '停止對話', 'exit', 'quit', 'stop']:
            if is_active_conversation:
                # 結束對話
                end_conversation(user_id)
                reply_to_user(event.reply_token, "好的，已結束本次對話。有需要時請隨時呼喚我！")
                return
        
        # 檢查訊息是否為 AI 對話請求 (活躍對話或匹配關鍵詞)
        if is_active_conversation or is_ai_request(user_message):
            # 如果是新的對話或匹配了關鍵詞，將用戶設為活躍對話狀態
            start_conversation(user_id)
            logger.info(f"識別為 AI 請求")
            
            # 檢查是否為圖片生成請求
            if is_image_generation_request(user_message):
                logger.info("檢測到圖片生成請求")
                reply_to_user(event.reply_token, "抱歉，我目前不支援圖片生成功能。\n\n我可以提供的服務包括：\n- 文字對話和問答\n- 每日早安圖片和天氣預報推送\n- 智能問候語生成\n\n如果您有其他文字相關的問題，我很樂意幫助您！")
                return
            
            # 發送「處理中」狀態指示
            processing_message = get_processing_message()
            reply_to_user(event.reply_token, processing_message)
            
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
                
                # 使用 Push Message 發送最終回應
                logger.info(f"發送最終回應給用戶")
                push_message_to_user(user_id, ai_response)
                
            except Exception as e:
                logger.error(f"處理 AI 回應時發生錯誤: {str(e)}")
                logger.error(traceback.format_exc())
                push_message_to_user(user_id, "抱歉，處理您的請求時出現了問題，請稍後再試。")
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

def is_image_generation_request(message):
    """檢查是否為圖片生成請求"""
    if not message:
        return False
    
    message_lower = message.lower().strip()
    
    # 圖片生成相關關鍵字
    image_keywords = [
        '生成圖片', '產生圖片', '製作圖片', '畫圖片', '畫圖',
        '生成圖像', '產生圖像', '製作圖像', 
        'generate image', 'create image', 'make image', 'draw image',
        'generate picture', 'create picture', 'make picture',
        '圖片生成', '圖像生成', '生成一張圖', '畫一張圖',
        '幫我畫', '幫我生成', '生成照片', '製作照片',
        '生成一張', '產生一張', '製作一張'  # 新增更多變化
    ]
    
    for keyword in image_keywords:
        if keyword in message_lower:
            logger.info(f"檢測到圖片生成關鍵字: '{keyword}'")
            return True
    
    return False

def is_ai_request(message):
    """檢查是否為 AI 對話請求 (最終版: 僅檢測訊息開頭或帶允許前導字符的關鍵字)
    
    判斷邏輯：
    1. 訊息以 'AI:', 'ai:', '@ai' 開頭
    2. 訊息以 '小幫手', '花生' 關鍵字開頭或帶有允許的前導字符
    3. 對於正在進行中的對話，第二句之後不需要關鍵字
    """
    if not message:
        return False
    
    # 添加詳細日誌以診斷問題
    logger.info(f"檢測訊息是否為AI請求: '{message}'")
    
    # 嘗試處理可能的特殊字符或編碼問題
    normalized_message = message
    try:
        # 先嘗試規範化字符
        import unicodedata
        normalized_message = unicodedata.normalize('NFKC', message)
        if normalized_message != message:
            logger.info(f"已規範化訊息: '{normalized_message}'")
    except Exception as e:
        logger.error(f"規範化訊息時出錯: {str(e)}")
    
    # 去除前後空格，便於檢查句首關鍵字
    trimmed_message = normalized_message.strip()
    message_lower = trimmed_message.lower()
    
    # 1. 檢查常見的AI前綴 (必須在句首)
    if (message_lower.startswith(('ai:', 'ai：')) or 
        message_lower.startswith(('@ai', '@ai ')) or 
        message_lower.startswith('ai ') or 
        message_lower == 'ai'):
        logger.info("識別為AI請求: 前綴匹配")
        return True
    
    # 2. 檢查中文關鍵字是否在句首或帶有允許的前導字符
    keywords = ['小幫手', '花生']
    
    # 允許的前導字符列表
    allowed_prefixes = ['!', '！', ',', '，', '。', '.', '?', '？', ' ', '　', ':', '：', '@', '#', '$', '%', '、', '~', '～']
    
    for keyword in keywords:
        # 檢查關鍵字是否在句首
        if trimmed_message.startswith(keyword):
            logger.info(f"識別為AI請求: 檢測到句首關鍵字 '{keyword}'")
            return True
        
        # 檢查是否有允許的前導字符後接關鍵字
        if len(trimmed_message) > 1:
            # 處理只有一個前導字符的情況
            first_char = trimmed_message[0]
            if first_char in allowed_prefixes and trimmed_message[1:].startswith(keyword):
                logger.info(f"識別為AI請求: 檢測到帶前導字符的關鍵字 '{keyword}', 前導字符: '{first_char}'")
                return True
            
            # 處理有前導字符和空格的情況 (如 ". 小幫手")
            if len(trimmed_message) > 2 and first_char in allowed_prefixes:
                # 特殊處理點號+空格情況 
                if first_char == '.' and trimmed_message[1] == ' ' and trimmed_message[2:].startswith(keyword):
                    logger.info(f"識別為AI請求: 檢測到特殊點號和空格前導的關鍵字 '{keyword}'")
                    return True
                
                # 正常處理其他前導字符+空格情況
                if trimmed_message[1] == ' ' and trimmed_message[2:].startswith(keyword):
                    logger.info(f"識別為AI請求: 檢測到帶前導字符和空格的關鍵字 '{keyword}', 前導字符: '{first_char} '")
                    return True
    
    # 3. 進行字符級別的檢查 (花生)
    flower_char = '花'
    life_char = '生'
    
    # 直接在句首的「花生」
    if trimmed_message.startswith(flower_char) and len(trimmed_message) > 1:
        if trimmed_message[1] == life_char:
            logger.info(f"識別為AI請求: 通過字符級別檢測到句首 '花生' 關鍵字")
            return True
    
    # 允許的前導字符後的「花生」
    if len(trimmed_message) > 2 and trimmed_message[0] in allowed_prefixes:
        # 一個前導字符的情況
        if trimmed_message[1] == flower_char and trimmed_message[2] == life_char:
            logger.info(f"識別為AI請求: 通過字符級別檢測到帶前導字符的 '花生' 關鍵字")
            return True
            
        # 前導字符+空格的情況 (如 ". 花生")
        elif trimmed_message[1] == ' ' and len(trimmed_message) > 3:
            if trimmed_message[2] == flower_char and trimmed_message[3] == life_char:
                logger.info(f"識別為AI請求: 通過字符級別檢測到帶前導字符和空格的 '花生' 關鍵字")
                return True
    
    # 所有檢查都未通過
    logger.info("非AI請求: 未檢測到句首或帶允許前導字符的觸發關鍵字")
    return False

def extract_query(message):
    """從訊息中提取實際查詢內容 (最終版: 適配句首關鍵字檢測)"""
    message = message.strip()
    
    # 1. 處理明確的前綴
    if message.lower().startswith('ai:'):
        return message[3:].strip()
    elif message.lower().startswith('ai：'):  # 中文冒號
        return message[3:].strip()
    elif message.lower().startswith('@ai'):
        return message[3:].strip()
    elif message.lower().startswith('ai '):
        return message[3:].strip()
    
    # 2. 處理「小幫手」和「花生」關鍵字 (只考慮句首或帶允許的前導字符)
    keywords = ['小幫手', '花生']
    allowed_prefixes = ['!', '！', ',', '，', '。', '.', '?', '？', ' ', '　', ':', '：', '@', '#', '$', '%', '、', '~', '～']
    
    for keyword in keywords:
        # 如果關鍵字在開頭，移除它
        if message.startswith(keyword):
            return message[len(keyword):].strip()
        
        # 處理有前導字符的情況
        if len(message) > 1:
            first_char = message[0]
            # 單個前導字符
            if first_char in allowed_prefixes and message[1:].startswith(keyword):
                return message[1 + len(keyword):].strip()
            
            # 前導字符+空格的情況 (如 ". 小幫手")
            if len(message) > 2 and first_char in allowed_prefixes and message[1] == ' ':
                if message[2:].startswith(keyword):
                    return message[2 + len(keyword):].strip()
    
    # 3. 處理「花生」字符級別檢測
    flower_char = '花'
    life_char = '生'
    
    # 直接在句首的「花生」
    if message.startswith(flower_char) and len(message) > 1:
        if message[1] == life_char:
            return message[2:].strip()
    
    # 允許的前導字符後的「花生」
    if len(message) > 2 and message[0] in allowed_prefixes:
        # 一個前導字符的情況
        if message[1] == flower_char and message[2] == life_char:
            return message[3:].strip()
        
        # 前導字符+空格的情況
        elif message[1] == ' ' and len(message) > 3:
            if message[2] == flower_char and message[3] == life_char:
                return message[4:].strip()
    
    # 如果沒有找到關鍵字或無法提取，則使用整個訊息
    return message

def update_conversation_history(user_id, query, response):
    """更新使用者的對話歷史記錄
    
    保留最近的對話歷史，數量由 MAX_HISTORY 常數決定
    """
    # MAX_HISTORY 已在全域定義
    
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []
    
    # 添加新的對話
    conversation_histories[user_id].append({"role": "user", "parts": [query]})
    conversation_histories[user_id].append({"role": "model", "parts": [response]})
    
    # 如果歷史紀錄太長，移除最舊的對話
    if len(conversation_histories[user_id]) > MAX_HISTORY * 2:  # 一輪對話有兩條紀錄
        conversation_histories[user_id] = conversation_histories[user_id][-MAX_HISTORY*2:]
        
    # 更新對話狀態 (設定最新活動時間)
    start_conversation(user_id)

def get_processing_message():
    """產生處理中狀態訊息"""
    import random
    messages = [
        "🤔 讓我想想...",
        "⏳ 正在處理您的請求中...",
        "🧠 AI小幫手正在思考...",
        "📝 正在為您準備回應...",
        "🔍 分析中，請稍候...",
        "💭 思考中..."
    ]
    return random.choice(messages)

def push_message_to_user(user_id, message):
    """使用 Push Message API 發送訊息給用戶"""
    if not user_id:
        logger.error("無法推送訊息：user_id 為空")
        return False
    
    if not message:
        logger.error("無法推送訊息：message 為空")
        return False
        
    try:
        logger.info(f"開始推送訊息給用戶 {user_id}")
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            
            # 如果消息太長，分段發送
            if len(message) > 5000:
                logger.info(f"訊息過長 ({len(message)} 字符)，進行分段")
                messages = split_long_message(message)
                
                # 發送第一段
                response = line_bot_api.push_message(
                    PushMessageRequest(
                        to=user_id,
                        messages=[TextMessage(text=messages[0])]
                    )
                )
                logger.info(f"成功推送第一段訊息")
                
                # 發送剩餘段落
                for i, msg in enumerate(messages[1:], 1):
                    time.sleep(0.5)  # 避免發送太快
                    line_bot_api.push_message(
                        PushMessageRequest(
                            to=user_id,
                            messages=[TextMessage(text=msg)]
                        )
                    )
                    logger.info(f"成功推送第 {i+1} 段訊息")
            else:
                logger.info(f"推送訊息，長度 {len(message)} 字符")
                response = line_bot_api.push_message(
                    PushMessageRequest(
                        to=user_id,
                        messages=[TextMessage(text=message)]
                    )
                )
                logger.info(f"成功推送訊息")
                
        return True
    except Exception as e:
        logger.error(f"推送訊息時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return False

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
        "- 或輸入「@AI 您的問題」(例如：@AI 今天的天氣如何？)\n"
        "- 或喊「小幫手」(例如：小幫手，介紹台灣夜市文化)\n"
        "- 或喊「花生」(例如：花生，幫我查一下這個字怎麼念)\n\n"
        "🔄 我具備上下文理解功能，一旦開始對話後，您可以直接提問，無需再加上前綴！\n\n"
        "⏱️ 當您發送問題時，我會先回覆處理狀態，讓您知道我正在思考中\n"
        "📨 處理完成後會立即發送詳細回答\n\n"
        "⏰ 對話將在5分鐘無互動後自動結束，或您可以輸入「結束對話」來主動結束\n\n"
        "🌟 AI小幫手花生祝您使用愉快！\n"
    )

def clear_user_history(user_id):
    """清除特定用戶的對話歷史"""
    if user_id in conversation_histories:
        del conversation_histories[user_id]
        return True
    return False

def check_active_conversation(user_id, current_time):
    """檢查用戶是否處於活躍對話狀態"""
    if user_id in active_conversations:
        last_activity_time = active_conversations[user_id]
        # 檢查是否超時
        if current_time - last_activity_time <= CONVERSATION_TIMEOUT:
            logger.info(f"用戶 {user_id} 處於活躍對話狀態，剩餘時間: {CONVERSATION_TIMEOUT - (current_time - last_activity_time):.1f} 秒")
            return True
        else:
            # 超時自動結束對話
            logger.info(f"用戶 {user_id} 對話已超時，自動結束")
            end_conversation(user_id)
            return False
    return False

def start_conversation(user_id):
    """將用戶標記為活躍對話狀態"""
    active_conversations[user_id] = time.time()
    logger.info(f"用戶 {user_id} 開始/繼續對話")

def end_conversation(user_id):
    """結束用戶的對話狀態"""
    if user_id in active_conversations:
        del active_conversations[user_id]
        logger.info(f"用戶 {user_id} 結束對話")
    # 可選：根據需求決定是否要清除對話歷史
    # clear_user_history(user_id)

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
