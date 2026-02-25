#!/usr/bin/env python3
"""
意圖分類器模組
根據用戶訊息判斷意圖類型，支援：
- todo: 待辦事項管理
- link: 連結儲存與分析
- save_content: 內容分類儲存
- query: 查詢與推薦
- other: 一般聊天
"""

import os
import json
import logging
import re
from typing import Dict, Optional

# 設定日誌
logger = logging.getLogger(__name__)

# 導入 Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Gemini API 未安裝，意圖分類將使用基於規則的方法")


class IntentClassifier:
    """意圖分類器類別"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化意圖分類器
        
        Args:
            api_key: Gemini API 金鑰
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if self.api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("意圖分類器已使用 Gemini API 初始化")
            except Exception as e:
                logger.error(f"初始化 Gemini API 失敗: {e}")
                self.model = None
    
    def classify_intent(self, message: str) -> Dict:
        """
        分類用戶訊息的意圖
        
        Args:
            message: 用戶訊息
            
        Returns:
            Dict: 包含 intent, subIntent, contentType, queryType, confidence 等欄位
        """
        message = message.strip()
        
        # 優先使用 Gemini API 進行分類
        if self.model:
            try:
                return self._classify_with_gemini(message)
            except Exception as e:
                logger.error(f"使用 Gemini API 分類失敗: {e}")
                logger.info("改用基於規則的分類")
        
        # 使用基於規則的分類作為備援
        return self._classify_with_rules(message)
    
    def _classify_with_gemini(self, message: str) -> Dict:
        """使用 Gemini API 進行意圖分類"""
        
        prompt = f"""你是花生AI小幫手的意圖分類助手。根據用戶訊息的意圖類型，必須嚴格按照 JSON 格式輸出。

分析以下訊息的意圖：

訊息：{message}

意圖類型（5種）：

1. todo - 待辦事項相關（新增/完成/查詢待辦）
   - create: 新增待辦（例如：「我要吃飯、取貨、寫作業」「待辦：買菜」「我明天要開會」「提醒我買菜」「提醒我明天要開會」「今晚11:00看影片」「幫我新增待辦事項」「新增：晚上看影片」）
   - update: 更新狀態（例如：「我寫完作業了！」「作業完成了」「取消吃飯」）
   - query: 查詢待辦（例如：「我上禮拜做了哪些事？」「吃了什麼？」「查看待辦」「明天要幹嘛」）

2. link - 分享連結（包含 http/https 連結）

3. save_content - 儲存內容（用戶想要記錄的信息、事實性資訊、觀察、思考）
   - contentType: insight（靈感）、knowledge（知識）、memory（記憶）、music（音樂）、life（活動）
   - 例如：「今天突然理解了一個人生道理」（insight）、「React Hooks 的用法」（knowledge）、
         「今天跟朋友聊到...」（memory）、「在 solo 陶喆 蝴蝶」（music）、
         「小巨蛋溜冰！」（life）
         「讓 AI 當你的提問教練」（memory），因為一句不是一般聊天的對話，而是我偶然看到想記錄下來的想法、觀察、思考
         - 注意：如果是問句（例如：「這禮拜的社交狀況如何」），不應分類為 save_content

4. query - 查詢類（用戶詢問或請求建議）
   - queryType: feedback（請求回饋/建議）、recommendation（請求推薦）、chat_history（查詢過往對話）
   - 例如：「給我一些生活建議」（feedback）、「推薦一些音樂」（recommendation）、
         「我之前聊過什麼？」（chat_history）
         「我今天在幹嘛？」（chat_history）

5. other - 一般聊天（不明確的對話、想有個人陪伴，無壓力地分享即時感受、想找人聊天）

判斷規則：
- 如果是問句（如何、什麼、哪些、怎樣），通常是 query 而非 save_content
- save_content 是「儲存」意圖，query 是「詢問」意圖
- 如果包含連結，優先分類為 link

輸出 JSON（不能有其他文字）：
{{
  "intent": "todo|link|save_content|query|other",
  "subIntent": "create|update|query",
  "contentType": "insight|knowledge|memory|music|life",
  "queryType": "feedback|recommendation|chat_history",
  "confidence": 0.0-1.0
}}"""

        response = self.model.generate_content(prompt)
        result_text = response.text.strip()
        
        # 移除可能的 markdown 代碼塊標記
        result_text = result_text.replace('```json', '').replace('```', '').strip()
        
        # 解析 JSON
        try:
            result = json.loads(result_text)
            logger.info(f"意圖分類結果: {result}")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"解析 Gemini 回應失敗: {e}, 回應內容: {result_text}")
            # 使用基於規則的分類作為備援
            return self._classify_with_rules(message)
    
    def _classify_with_rules(self, message: str) -> Dict:
        """使用基於規則的方法進行意圖分類"""
        
        # 預設結果
        result = {
            "intent": "other",
            "subIntent": None,
            "contentType": None,
            "queryType": None,
            "confidence": 0.7
        }
        
        message_lower = message.lower()
        
        # 檢查是否包含連結
        if re.search(r'https?://', message):
            result["intent"] = "link"
            result["confidence"] = 0.95
            return result
        
        # 檢查待辦事項相關關鍵字（順序很重要：先檢查更具體的查詢和更新，再檢查創建）
        todo_query_keywords = ['查看待辦', '我做了哪些', '待辦事項', '有什麼待辦', '今天要幹嘛', '明天要幹嘛', '查詢待辦', '顯示待辦', '我的待辦', '顯示任務', '查看任務']
        todo_update_keywords = ['完成了', '做完了', '已經做完', '取消待辦', '刪除待辦', '完成待辦', '已完成', '標記完成', '完成任務']
        todo_create_keywords = ['提醒我', '我要', '我明天要', '我今天要', '新增待辦', '幫我記', '記得', '別忘了', '添加任務', '新增任務']
        
        # 優先檢查查詢（避免「待辦事項」被誤判為創建）
        for keyword in todo_query_keywords:
            if keyword in message:
                result["intent"] = "todo"
                result["subIntent"] = "query"
                result["confidence"] = 0.9
                return result
        
        # 檢查更新
        for keyword in todo_update_keywords:
            if keyword in message:
                result["intent"] = "todo"
                result["subIntent"] = "update"
                result["confidence"] = 0.85
                return result
        
        # 最後檢查創建
        for keyword in todo_create_keywords:
            if keyword in message:
                result["intent"] = "todo"
                result["subIntent"] = "create"  # 修正：應該是 create 而非 query
                result["confidence"] = 0.85
                return result
        
        # 檢查查詢類關鍵字
        query_keywords = ['推薦', '建議', '如何', '什麼', '哪些', '怎樣', '為什麼', '可以告訴我', '我想知道']
        recommendation_keywords = ['推薦', '介紹一些', '有什麼好的']
        feedback_keywords = ['建議', '意見', '看法', '想法']
        history_keywords = ['之前', '以前', '過去', '上次', '聊過什麼']
        # 知識查詢關鍵字（加入單字查詢，優先度較高）
        knowledge_query_keywords = ['我學了什麼', '我的知識', '查看知識', '有什麼知識', '我學過', '查詢知識', '顯示知識', '之前學到', '我記了什麼', '查看筆記', '我學了什麼東西']
        # 內容查詢關鍵字
        content_query_keywords = ['我的靈感', '我的音樂', '我的記憶', '查看內容', '顯示內容']
        # 單字查詢（必須是完整訊息且很短）
        single_word_queries = ['知識', '待辦', '靈感', '筆記']
        
        # 優先檢查單字查詢（訊息很短且匹配）
        if len(message) <= 3:
            if '知識' in message or '筆記' in message:
                result["intent"] = "query"
                result["queryType"] = "knowledge"
                result["confidence"] = 0.95
                return result
            elif '待辦' in message:
                result["intent"] = "todo"
                result["subIntent"] = "query"
                result["confidence"] = 0.95
                return result
            elif '靈感' in message:
                result["intent"] = "query"
                result["queryType"] = "content"
                result["confidence"] = 0.95
                return result
        
        # 檢查知識和內容查詢
        for keyword in knowledge_query_keywords:
            if keyword in message:
                result["intent"] = "query"
                result["queryType"] = "knowledge"
                result["confidence"] = 0.9
                return result
        
        for keyword in content_query_keywords:
            if keyword in message:
                result["intent"] = "query"
                result["queryType"] = "content"
                result["confidence"] = 0.9
                return result
        
        is_query = any(keyword in message for keyword in query_keywords)
        
        if is_query:
            result["intent"] = "query"
            
            # 判斷查詢子類型
            if any(keyword in message for keyword in recommendation_keywords):
                result["queryType"] = "recommendation"
            elif any(keyword in message for keyword in feedback_keywords):
                result["queryType"] = "feedback"
            elif any(keyword in message for keyword in history_keywords):
                result["queryType"] = "chat_history"
            else:
                result["queryType"] = "feedback"
            
            result["confidence"] = 0.8
            return result
        
        # 檢查儲存內容類關鍵字
        insight_keywords = ['突然理解', '領悟', '發現', '原來', '我覺得', '人生道理', '恍然大悟']
        knowledge_keywords = ['學到', '知識', '技術', '方法', '概念', '學習', '學會', '掌握']
        music_keywords = ['聽', '音樂', 'solo', '唱歌', '播放']
        life_keywords = ['溜冰', '運動', '去了', '參加', '活動', '做了']
        
        # 如果不是問句，且包含特定關鍵字，可能是儲存內容
        if not message.endswith('?') and not message.endswith('？'):
            if any(keyword in message for keyword in insight_keywords):
                result["intent"] = "save_content"
                result["contentType"] = "insight"
                result["confidence"] = 0.75
                return result
            elif any(keyword in message for keyword in knowledge_keywords):
                result["intent"] = "save_content"
                result["contentType"] = "knowledge"
                result["confidence"] = 0.75
                return result
            elif any(keyword in message for keyword in music_keywords):
                result["intent"] = "save_content"
                result["contentType"] = "music"
                result["confidence"] = 0.75
                return result
            elif any(keyword in message for keyword in life_keywords):
                result["intent"] = "save_content"
                result["contentType"] = "life"
                result["confidence"] = 0.75
                return result
        
        # 預設為一般聊天
        logger.info(f"訊息被分類為一般聊天: {message}")
        return result


# 建立全域實例
intent_classifier = IntentClassifier()


# 測試函數
if __name__ == "__main__":
    # 測試範例
    test_messages = [
        "我明天要開會",
        "作業完成了",
        "查看待辦",
        "https://example.com/article",
        "今天突然理解了一個人生道理",
        "推薦一些音樂",
        "你好嗎？",
        "我之前聊過什麼？"
    ]
    
    for msg in test_messages:
        result = intent_classifier.classify_intent(msg)
        print(f"訊息: {msg}")
        print(f"結果: {result}")
        print("-" * 50)
