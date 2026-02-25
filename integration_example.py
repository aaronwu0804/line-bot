#!/usr/bin/env python3
"""
整合範例 - 展示如何在 app.py 中整合花生助手的新功能

這個檔案展示了如何修改現有的 app.py 來使用新的智能功能
"""

# ========================
# 步驟 1: 匯入新模組
# ========================

import asyncio
from src.peanut_assistant import peanut_assistant
from src.intent_classifier import intent_classifier

# ========================
# 步驟 2: 修改訊息處理函數
# ========================

# 原有的 handle_message 函數

# @handler.add(MessageEvent, message=TextMessageContent)
# def handle_message(event):
#     """處理文字訊息"""
#     user_message = event.message.text
#     user_id = event.source.user_id
#     reply_token = event.reply_token
    
#     # 檢查是否為 AI 請求
#     if is_ai_request(user_message):
#         # 原有的處理邏輯...
#         pass

# ========================
# 新的訊息處理函數（整合花生助手）
# ========================

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """處理文字訊息（整合花生助手版本）"""
    user_message = event.message.text
    user_id = event.source.user_id
    reply_token = event.reply_token
    
    logger.info(f"收到訊息: user_id={user_id}, message={user_message}")
    
    # 檢查是否為「使用說明」請求
    if user_message.strip() in ['使用說明', '說明', 'help', '幫助', '功能']:
        usage_guide = peanut_assistant.get_usage_guide()
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=usage_guide)]
                )
            )
        return
    
    # 檢查是否為 AI 請求
    if is_ai_request(user_message):
        try:
            # 先回覆「正在處理」訊息
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=[TextMessage(text="🤔 讓我想想...")]
                    )
                )
            
            # 使用花生助手處理訊息
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                peanut_assistant.process_message(user_id, user_message)
            )
            
            # 檢查是否需要 AI 回應
            if result.get("needs_ai_response"):
                # 使用原有的 AI 回應系統，但加入記憶上下文
                context = result.get("context", "")
                query = extract_query(user_message)
                
                # 取得對話歷史
                conversation_history = conversation_histories.get(user_id, [])
                
                # 如果有記憶上下文，添加到系統提示中
                if context:
                    system_prompt = f"""你是花生 AI 小幫手。以下是用戶的相關記憶和資訊：

{context}

請根據這些資訊，以及用戶的問題，提供個人化的回應。
回答要友善、有幫助，並展現出你記得用戶分享的資訊。"""
                    
                    # 使用帶上下文的 AI 回應
                    ai_response = get_ai_response_with_context(
                        query, 
                        conversation_history,
                        system_prompt
                    )
                else:
                    # 使用原有的 AI 回應
                    ai_response = get_ai_response(query, conversation_history)
                
                # 推送 AI 回應
                push_message_to_user(user_id, ai_response)
                
                # 更新對話歷史
                update_conversation_history(user_id, query, ai_response)
                
            else:
                # 直接推送花生助手的回應
                response = result.get("response", "")
                if response:
                    push_message_to_user(user_id, response)
            
        except Exception as e:
            logger.error(f"處理訊息時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            push_message_to_user(user_id, "抱歉，處理您的訊息時發生了錯誤，請稍後再試。")
    
    else:
        # 非 AI 請求，回覆使用說明
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=get_help_message())]
                )
            )

# ========================
# 步驟 3: 新增帶上下文的 AI 回應函數
# ========================

def get_ai_response_with_context(query, conversation_history=None, system_prompt=None):
    """
    獲取 AI 回應（帶自訂系統提示）
    
    Args:
        query: 用戶查詢
        conversation_history: 對話歷史
        system_prompt: 自訂系統提示（包含記憶上下文）
    
    Returns:
        str: AI 回應
    """
    try:
        # 使用自訂系統提示或預設提示
        if not system_prompt:
            system_prompt = """你是一個友善、有幫助的 AI 助理「花生」。
請用繁體中文回答問題，語氣要溫暖、自然，就像和朋友聊天一樣。
如果不確定答案，請誠實說明，不要編造資訊。"""
        
        # 建立對話內容
        messages = [{"role": "system", "content": system_prompt}]
        
        # 加入對話歷史
        if conversation_history:
            for item in conversation_history[-5:]:  # 只保留最近 5 輪對話
                messages.append({"role": "user", "content": item.get("query", "")})
                messages.append({"role": "assistant", "content": item.get("response", "")})
        
        # 加入當前查詢
        messages.append({"role": "user", "content": query})
        
        # 呼叫 Gemini API
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # 轉換訊息格式
        gemini_messages = []
        for msg in messages:
            if msg["role"] == "system":
                # Gemini 將 system prompt 合併到第一個 user message
                continue
            elif msg["role"] == "user":
                gemini_messages.append({
                    "role": "user",
                    "parts": [msg["content"]]
                })
            elif msg["role"] == "assistant":
                gemini_messages.append({
                    "role": "model",
                    "parts": [msg["content"]]
                })
        
        # 如果有 system prompt，加到第一個 user message
        if system_prompt and gemini_messages:
            gemini_messages[0]["parts"][0] = f"{system_prompt}\n\n{gemini_messages[0]['parts'][0]}"
        
        # 生成回應
        chat = model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
        response = chat.send_message(gemini_messages[-1]["parts"][0])
        
        return response.text.strip()
    
    except Exception as e:
        logger.error(f"AI 回應生成失敗: {e}")
        return "抱歉，AI 回應生成失敗，請稍後再試。"

# ========================
# 步驟 4: 更新使用說明訊息
# ========================

def get_help_message():
    """產生使用說明訊息（更新版）"""
    return peanut_assistant.get_usage_guide()

# ========================
# 使用範例
# ========================

"""
範例對話流程：

用戶: "花生，我明天要開會"
↓
1. is_ai_request() 判斷為 AI 請求 ✓
2. peanut_assistant.process_message() 處理
3. intent_classifier 分類為 "todo-create"
4. todo_manager 新增待辦事項
5. 回應: "✅ 已新增待辦事項：我明天要開會 (截止：2026-02-25)"

---

用戶: "今天學到了 Python 的 asyncio"
↓
1. is_ai_request() 判斷為 AI 請求 ✓
2. peanut_assistant.process_message() 處理
3. intent_classifier 分類為 "save_content-knowledge"
4. content_manager 儲存內容
5. memory_manager 儲存到長期記憶
6. 回應: "✅ 已儲存到 📚 知識\\n\\n內容：今天學到了 Python 的 asyncio"

---

用戶: "推薦一些好書給我"
↓
1. is_ai_request() 判斷為 AI 請求 ✓
2. peanut_assistant.process_message() 處理
3. intent_classifier 分類為 "query-recommendation"
4. memory_manager 搜尋相關記憶
5. 找到用戶之前分享的閱讀偏好
6. 使用帶上下文的 AI 回應
7. 回應: "根據你之前提到的喜好...我推薦以下書籍..."

---

用戶: "查看待辦"
↓
1. is_ai_request() 判斷為 AI 請求 ✓
2. peanut_assistant.process_message() 處理
3. intent_classifier 分類為 "todo-query"
4. todo_manager 查詢待辦事項
5. 格式化顯示
6. 回應: "📋 您的待辦事項：\\n⏳ 待完成：\\n1. 我明天要開會 (截止：明天)"
"""

# ========================
# 注意事項
# ========================

"""
1. 記得在 app.py 開頭匯入必要的模組：
   from src.peanut_assistant import peanut_assistant
   import asyncio

2. 確保已安裝所有依賴：
   pip install -r requirements.txt

3. 設定必要的環境變數：
   LINE_CHANNEL_ACCESS_TOKEN
   LINE_CHANNEL_SECRET
   GEMINI_API_KEY
   MEM0_API_KEY（可選）

4. 測試功能：
   python test_peanut_features.py

5. 本地測試：
   python app.py

6. 部署到 Render 時會自動使用這些新功能
"""
