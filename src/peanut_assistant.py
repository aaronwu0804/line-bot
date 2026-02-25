#!/usr/bin/env python3
"""
整合服務模組 - 花生 AI 小幫手
整合所有功能：意圖分類、記憶管理、待辦事項、內容儲存
"""

import logging
from typing import Dict, Optional
import asyncio
from datetime import datetime

# 導入各個管理器
from .intent_classifier import intent_classifier
from .memory_manager import mem0_manager, local_memory_manager
from .todo_manager import todo_manager
from .content_manager import content_manager
# 連結分析功能已移除

logger = logging.getLogger(__name__)


class PeanutAssistant:
    """花生 AI 小幫手整合服務"""
    
    def __init__(self):
        """初始化花生助手"""
        self.intent_classifier = intent_classifier
        self.mem0_manager = mem0_manager
        self.local_memory = local_memory_manager
        self.todo_manager = todo_manager
        self.content_manager = content_manager
        # 連結分析功能已移除
        
        logger.info("花生 AI 小幫手整合服務已初始化")
    
    async def process_message(self, user_id: str, message: str) -> Dict:
        """
        處理用戶訊息
        
        Args:
            user_id: 用戶 ID
            message: 用戶訊息（應該已去除前綴）
            
        Returns:
            Dict: 處理結果，包含回應訊息
        """
        try:
            # 移除可能的前綴（以防萬一）
            clean_message = self._clean_message(message)
            logger.info(f"處理訊息: 原始='{message}', 清理後='{clean_message}'")
            
            # 1. 意圖分類
            intent_result = self.intent_classifier.classify_intent(clean_message)
            intent = intent_result.get("intent")
            sub_intent = intent_result.get("subIntent")
            content_type = intent_result.get("contentType")
            query_type = intent_result.get("queryType")
            
            logger.info(f"意圖分類: intent={intent}, sub_intent={sub_intent}, confidence={intent_result.get('confidence')}")
            
            # 2. 根據意圖執行對應操作
            if intent == "todo":
                return await self._handle_todo(user_id, clean_message, sub_intent)
            
            elif intent == "save_content":
                return await self._handle_save_content(user_id, clean_message, content_type)
            
            elif intent == "query":
                return await self._handle_query(user_id, clean_message, query_type)
            
            else:  # other - 一般聊天（包含連結）
                return await self._handle_chat(user_id, clean_message)
        
        except Exception as e:
            logger.error(f"處理訊息時發生錯誤: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "抱歉，處理您的訊息時發生了錯誤，請稍後再試。"
            }
    
    def _clean_message(self, message: str) -> str:
        """清理訊息，移除前綴"""
        message = message.strip()
        
        # 移除常見前綴
        prefixes = ['ai:', 'ai：', '@ai ', '@ai', 'ai ', '小幫手', '花生', '小幫手，', '花生，']
        
        for prefix in prefixes:
            if message.lower().startswith(prefix):
                message = message[len(prefix):].strip()
                break
        
        # 移除開頭的逗號、句號等
        while message and message[0] in '，,。. 　':
            message = message[1:].strip()
        
        return message
    
    async def _handle_todo(self, user_id: str, message: str, sub_intent: Optional[str]) -> Dict:
        """處理待辦事項相關請求"""
        
        if sub_intent == "create":
            # 新增待辦事項 - 先移除創建關鍵字
            create_keywords = ['提醒我', '提醒', '我要', '我明天要', '我今天要', '新增待辦', '新增事項', '新增任務', '新增', '幫我記', '記得', '別忘了', '添加任務', '添加事項', '加入待辦']
            
            todo_content = message
            # 移除創建關鍵字
            for keyword in create_keywords:
                if todo_content.startswith(keyword):
                    todo_content = todo_content[len(keyword):].strip()
                    break
            
            # 如果移除後內容為空，提示用戶
            if not todo_content:
                return {"success": False, "response": "請告訴我要新增什麼待辦事項\n\n範例：\n• 花生 提醒 2/27 去看球賽\n• 花生 新增 明天開會\n• 花生 加入待辦 寫報告"}
            
            result = self.todo_manager.create_todo(user_id, todo_content)
            
            if result.get("success"):
                todo = result["todo"]
                response = f"✅ 已新增待辦事項：\n{todo['content']}"
                
                if todo.get("due_date"):
                    response += f"\n截止日期：{todo['due_date']}"
                
                # 也儲存到記憶中
                if self.mem0_manager.enabled:
                    await self.mem0_manager.add_memory(
                        user_id,
                        f"待辦事項：{todo['content']}",
                        {"type": "todo", "status": "pending"}
                    )
            else:
                response = "❌ 新增待辦事項失敗，請稍後再試。"
            
            return {"success": result.get("success"), "response": response}
        
        elif sub_intent == "update":
            # 更新待辦事項（支援完成或刪除）
            # 完成關鍵字和取消/刪除關鍵字
            complete_keywords = ["完成了", "做完了", "已經做完", "完成待辦", "完成任務", "標記完成", "已完成", "已經完成"]
            cancel_keywords = ["取消了", "不用了", "不做了", "刪掉", "移除", "取消待辦", "刪除待辦", "取消"]
            
            todo_keyword = None
            is_cancel = False
            
            # 先檢查是否為取消操作
            for kw in cancel_keywords:
                if kw in message:
                    is_cancel = True
                    # 提取待辦內容（移除時間詞和取消詞）
                    cleaned = message
                    # 移除時間詞
                    for time_word in ["明天的", "今天的", "下週的", "明天", "今天", "下週"]:
                        cleaned = cleaned.replace(time_word, "")
                    # 移除取消詞
                    cleaned = cleaned.replace(kw, "").strip()
                    if cleaned:
                        todo_keyword = cleaned
                        break
            
            # 如果不是取消，檢查完成關鍵字
            if not is_cancel:
                for kw in complete_keywords:
                    if kw in message:
                        # 提取待辦內容
                        parts = message.split(kw)
                        if len(parts) > 0 and parts[0].strip():
                            todo_keyword = parts[0].strip()
                            # 移除時間詞
                            for time_word in ["明天的", "今天的", "下週的"]:
                                todo_keyword = todo_keyword.replace(time_word, "").strip()
                            break
                        elif len(parts) > 1 and parts[1].strip():
                            todo_keyword = parts[1].strip()
                            break
            
            # 執行更新或刪除
            if todo_keyword:
                if is_cancel:
                    # 刪除待辦
                    result = self.todo_manager.delete_todo(user_id, content_keyword=todo_keyword)
                    if result.get("success") and result.get("deleted_count", 0) > 0:
                        response = f"✅ 已刪除待辦：{todo_keyword}\n共刪除 {result.get('deleted_count', 1)} 個待辦事項"
                    else:
                        response = f"❌ 找不到包含「{todo_keyword}」的待辦事項\n\n提示：使用關鍵字，例如：\n• 明天的開會取消了\n• 寫報告不用了\n• 刪掉 Python 學習"
                else:
                    # 標記完成
                    result = self.todo_manager.update_todo(user_id, content_keyword=todo_keyword, status="completed")
                    if result.get("success") and result.get("updated_count", 0) > 0:
                        response = f"✅ 已標記完成：{todo_keyword}\n共更新 {result.get('updated_count', 1)} 個待辦事項"
                    else:
                        response = f"❌ 找不到包含「{todo_keyword}」的待辦事項\n\n提示：使用關鍵字，例如：\n• 開會完成了\n• 寫報告做完了\n• 明天的會議已經開完了"
            else:
                response = "請告訴我要更新哪個待辦事項\n\n範例：\n• 開會完成了（標記完成）\n• 明天的會議取消了（刪除）\n• 寫報告不用了（刪除）"
            
            return {"success": result.get("success") if todo_keyword else False, "response": response}
        
        elif sub_intent == "query":
            # 查詢待辦事項（同時顯示待完成和最近已完成的）
            pending_result = self.todo_manager.query_todos(user_id, status="pending")
            completed_result = self.todo_manager.query_todos(user_id, status="completed")
            
            has_pending = pending_result.get("success") and pending_result.get("todos")
            has_completed = completed_result.get("success") and completed_result.get("todos")
            
            if has_pending or has_completed:
                response_parts = []
                
                # 顯示待完成的
                if has_pending:
                    formatted_pending = self.todo_manager.format_todos_for_display(
                        pending_result["todos"]
                    )
                    response_parts.append(formatted_pending)
                
                # 顯示最近已完成的（最多顯示 5 個）
                if has_completed:
                    recent_completed = completed_result["todos"][:5]
                    if recent_completed:
                        response_parts.append("\n✅ 最近已完成：")
                        for i, todo in enumerate(recent_completed, 1):
                            completed_at = todo.get("completed_at", "")
                            try:
                                date_str = datetime.fromisoformat(completed_at).strftime("%m/%d")
                            except:
                                date_str = ""
                            response_parts.append(f"{i}. {todo['content']} (完成於：{date_str})")
                
                response = "\n".join(response_parts)
            else:
                response = "目前沒有待辦事項"
            
            return {"success": True, "response": response}
        
        else:
            # 預設顯示所有待辦事項
            result = self.todo_manager.query_todos(user_id)
            formatted = self.todo_manager.format_todos_for_display(result["todos"])
            return {"success": True, "response": formatted}
    
    # 連結分析功能已移除
    
    async def _handle_save_content(self, user_id: str, message: str, content_type: Optional[str]) -> Dict:
        """處理內容儲存"""
        
        # 預設類型為 memory
        if not content_type:
            content_type = "memory"
        
        # 儲存內容
        result = self.content_manager.save_content(user_id, message, content_type)
        
        if result.get("success"):
            type_name = self.content_manager.CONTENT_TYPES.get(content_type, content_type)
            response = f"✅ 已儲存到 {type_name}\n\n內容：{message}"
            
            # 也儲存到長期記憶
            if self.mem0_manager.enabled:
                await self.mem0_manager.add_memory(
                    user_id,
                    message,
                    {"type": content_type}
                )
            else:
                # 使用本地記憶管理器
                self.local_memory.add_memory(user_id, message, {"type": content_type})
        else:
            response = "❌ 儲存內容失敗"
        
        return {"success": result.get("success"), "response": response}
    
    async def _handle_query(self, user_id: str, message: str, query_type: Optional[str]) -> Dict:
        """處理查詢請求"""
        
        # 處理知識查詢
        if query_type == "knowledge":
            result = self.content_manager.query_contents(user_id, content_type="knowledge")
            if result.get("success") and result.get("contents"):
                formatted = self.content_manager.format_contents_for_display(
                    result["contents"], 
                    title="📚 您儲存的知識"
                )
                return {"success": True, "response": formatted}
            else:
                return {"success": True, "response": "您還沒有儲存任何知識喔！"}
        
        # 處理內容查詢
        elif query_type == "content":
            # 判斷要查詢哪種類型
            content_type = None
            if "靈感" in message:
                content_type = "insight"
            elif "音樂" in message:
                content_type = "music"
            elif "記憶" in message or "生活" in message:
                content_type = "life"
            
            result = self.content_manager.query_contents(user_id, content_type=content_type)
            if result.get("success") and result.get("contents"):
                type_emoji = {
                    "insight": "💡",
                    "knowledge": "📚",
                    "music": "🎵",
                    "life": "🌟",
                    "memory": "💭"
                }
                title = f"{type_emoji.get(content_type, '📝')} 您的{content_type or '所有'}內容"
                formatted = self.content_manager.format_contents_for_display(
                    result["contents"], 
                    title=title
                )
                return {"success": True, "response": formatted}
            else:
                return {"success": True, "response": "目前沒有相關內容喔！"}
        
        # 其他查詢類型：搜尋相關記憶
        memories = []
        
        if self.mem0_manager.enabled:
            memory_result = await self.mem0_manager.search_memory(user_id, message)
            if memory_result.get("success"):
                memories = memory_result.get("memories", [])
        else:
            # 使用本地記憶管理器
            memory_result = self.local_memory.search_memory(user_id, message)
            if memory_result.get("success"):
                memories = memory_result.get("memories", [])
        
        # 構建上下文
        context = ""
        if memories:
            if self.mem0_manager.enabled:
                context = self.mem0_manager.format_memories_for_context(memories)
            else:
                context = "\n".join([f"- {m.get('memory', '')}" for m in memories])
        
        # 使用 Gemini API 生成回應（這裡應該調用現有的 AI 回應功能）
        response = f"🤔 讓我想想...\n\n"
        
        if context:
            response += f"根據我的記憶：\n{context}\n\n"
        
        response += "（這裡會整合 Gemini API 生成智能回應）"
        
        return {"success": True, "response": response, "needs_ai_response": True, "context": context}
    
    async def _handle_chat(self, user_id: str, message: str) -> Dict:
        """處理一般聊天"""
        
        # 搜尋相關記憶作為上下文
        memories = []
        
        if self.mem0_manager.enabled:
            memory_result = await self.mem0_manager.search_memory(user_id, message, limit=3)
            if memory_result.get("success"):
                memories = memory_result.get("memories", [])
        
        # 構建上下文
        context = ""
        if memories:
            context = self.mem0_manager.format_memories_for_context(memories)
        
        return {
            "success": True,
            "response": "（一般聊天，將由 Gemini API 處理）",
            "needs_ai_response": True,
            "context": context
        }
    
    def get_usage_guide(self) -> str:
        """獲取使用指南"""
        return """👋 歡迎使用花生 AI 小幫手！

我現在擁有更多智能功能：

📋 待辦事項管理
• 新增待辦：「我明天要開會」「提醒我買菜」
• 完成待辦：「開會完成了」
• 查看待辦：「查看待辦」「今天要幹嘛」

💾 內容分類儲存
• 靈感記錄：「今天突然理解了一個道理...」
• 知識儲存：「學習了 React Hooks 的用法」
• 音樂記錄：「在 solo 陶喆的蝴蝶」
• 活動記錄：「去小巨蛋溜冰！」

🔗 連結分析
• 分享連結給我，我會自動分析內容並儲存
• 支援網頁內容摘要和重點提取

🧠 長期記憶
• 我會記住你分享的所有內容
• 可以隨時查詢過往的對話和記錄

💬 智能對話
• 一般聊天、請求建議、查詢資訊
• 我會根據你的記憶提供個人化回應

🔄 連續對話
• 開始對話後，可以直接提問，無需再加前綴

使用「AI:」、「@AI」、「小幫手」或「花生」來呼叫我！

🌟 花生祝您使用愉快！"""


# 建立全域實例
peanut_assistant = PeanutAssistant()


# 測試函數
if __name__ == "__main__":
    import asyncio
    
    async def test():
        test_user_id = "test_user_123"
        
        # 測試待辦事項
        result = await peanut_assistant.process_message(test_user_id, "我明天要開會")
        print(f"待辦事項: {result}")
        
        # 測試內容儲存
        result = await peanut_assistant.process_message(test_user_id, "今天突然理解了慢即是快的道理")
        print(f"內容儲存: {result}")
        
        # 測試查詢
        result = await peanut_assistant.process_message(test_user_id, "推薦一些好書")
        print(f"查詢: {result}")
    
    asyncio.run(test())
