#!/usr/bin/env python3
"""
Mem0 記憶管理模組
提供長期記憶儲存、檢索和管理功能
使用 Mem0 API 進行智能記憶管理
"""

import os
import logging
import json
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Mem0 API 設定
MEM0_API_KEY = os.getenv('MEM0_API_KEY')
MEM0_API_URL = "https://api.mem0.ai/v1"


class Mem0Manager:
    """Mem0 記憶管理器"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Mem0 管理器
        
        Args:
            api_key: Mem0 API 金鑰
        """
        self.api_key = api_key or MEM0_API_KEY
        self.api_url = MEM0_API_URL
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            logger.warning("Mem0 API 金鑰未設定，記憶功能將被禁用")
        else:
            logger.info("Mem0 記憶管理器已初始化")
    
    async def add_memory(self, user_id: str, content: str, metadata: Optional[Dict] = None) -> Dict:
        """
        新增記憶
        
        Args:
            user_id: 用戶 ID
            content: 要儲存的內容
            metadata: 額外的元數據（可選）
            
        Returns:
            Dict: 新增記憶的結果
        """
        if not self.enabled:
            logger.warning("Mem0 未啟用，無法新增記憶")
            return {"success": False, "error": "Mem0 API 未啟用"}
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [{"role": "user", "content": content}],
                "user_id": user_id,
                "output_format": "v1.1"
            }
            
            if metadata:
                payload["metadata"] = metadata
            
            response = requests.post(
                f"{self.api_url}/memories/",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                logger.info(f"成功新增記憶: user_id={user_id}")
                return {"success": True, "data": result}
            else:
                logger.error(f"新增記憶失敗: status={response.status_code}, response={response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        
        except Exception as e:
            logger.error(f"新增記憶時發生錯誤: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_memory(self, user_id: str, query: str, limit: int = 5) -> Dict:
        """
        搜尋記憶
        
        Args:
            user_id: 用戶 ID
            query: 搜尋查詢
            limit: 返回結果數量限制
            
        Returns:
            Dict: 搜尋結果
        """
        if not self.enabled:
            logger.warning("Mem0 未啟用，無法搜尋記憶")
            return {"success": False, "error": "Mem0 API 未啟用", "memories": []}
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": query,
                "user_id": user_id,
                "limit": limit
            }
            
            response = requests.post(
                f"{self.api_url}/memories/search/",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                memories = result.get("results", [])
                logger.info(f"搜尋記憶成功: user_id={user_id}, found={len(memories)}")
                return {"success": True, "memories": memories}
            else:
                logger.error(f"搜尋記憶失敗: status={response.status_code}, response={response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}", "memories": []}
        
        except Exception as e:
            logger.error(f"搜尋記憶時發生錯誤: {e}")
            return {"success": False, "error": str(e), "memories": []}
    
    async def get_all_memories(self, user_id: str) -> Dict:
        """
        獲取用戶的所有記憶
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            Dict: 所有記憶
        """
        if not self.enabled:
            logger.warning("Mem0 未啟用，無法獲取記憶")
            return {"success": False, "error": "Mem0 API 未啟用", "memories": []}
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Token {self.api_key}"
            }
            
            response = requests.get(
                f"{self.api_url}/memories/",
                headers=headers,
                params={"user_id": user_id},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                memories = result.get("results", [])
                logger.info(f"獲取所有記憶成功: user_id={user_id}, count={len(memories)}")
                return {"success": True, "memories": memories}
            else:
                logger.error(f"獲取記憶失敗: status={response.status_code}, response={response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}", "memories": []}
        
        except Exception as e:
            logger.error(f"獲取記憶時發生錯誤: {e}")
            return {"success": False, "error": str(e), "memories": []}
    
    async def delete_memory(self, memory_id: str) -> Dict:
        """
        刪除指定記憶
        
        Args:
            memory_id: 記憶 ID
            
        Returns:
            Dict: 刪除結果
        """
        if not self.enabled:
            logger.warning("Mem0 未啟用，無法刪除記憶")
            return {"success": False, "error": "Mem0 API 未啟用"}
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Token {self.api_key}"
            }
            
            response = requests.delete(
                f"{self.api_url}/memories/{memory_id}/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 204:
                logger.info(f"成功刪除記憶: memory_id={memory_id}")
                return {"success": True}
            else:
                logger.error(f"刪除記憶失敗: status={response.status_code}, response={response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        
        except Exception as e:
            logger.error(f"刪除記憶時發生錯誤: {e}")
            return {"success": False, "error": str(e)}
    
    def format_memories_for_context(self, memories: List[Dict]) -> str:
        """
        將記憶格式化為上下文字串，用於 AI 回應
        
        Args:
            memories: 記憶列表
            
        Returns:
            str: 格式化後的記憶上下文
        """
        if not memories:
            return ""
        
        context_parts = ["以下是用戶的相關記憶："]
        
        for i, memory in enumerate(memories, 1):
            memory_text = memory.get("memory", "")
            if memory_text:
                context_parts.append(f"{i}. {memory_text}")
        
        return "\n".join(context_parts)


# 建立全域實例
mem0_manager = Mem0Manager()


# 本地備援記憶管理（當 Mem0 API 不可用時使用）
class LocalMemoryManager:
    """本地記憶管理器（備援）"""
    
    def __init__(self, storage_dir: str = ".cache/memories"):
        """
        初始化本地記憶管理器
        
        Args:
            storage_dir: 記憶儲存目錄
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        logger.info(f"本地記憶管理器已初始化，儲存目錄: {storage_dir}")
    
    def _get_user_file(self, user_id: str) -> str:
        """獲取用戶記憶檔案路徑"""
        return os.path.join(self.storage_dir, f"{user_id}.json")
    
    def _load_memories(self, user_id: str) -> List[Dict]:
        """載入用戶的記憶"""
        file_path = self._get_user_file(user_id)
        
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入記憶失敗: {e}")
            return []
    
    def _save_memories(self, user_id: str, memories: List[Dict]) -> bool:
        """儲存用戶的記憶"""
        file_path = self._get_user_file(user_id)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(memories, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"儲存記憶失敗: {e}")
            return False
    
    def add_memory(self, user_id: str, content: str, metadata: Optional[Dict] = None) -> Dict:
        """新增記憶"""
        memories = self._load_memories(user_id)
        
        new_memory = {
            "id": f"mem_{len(memories) + 1}_{datetime.now().timestamp()}",
            "memory": content,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        memories.append(new_memory)
        
        if self._save_memories(user_id, memories):
            logger.info(f"本地記憶新增成功: user_id={user_id}")
            return {"success": True, "data": new_memory}
        else:
            return {"success": False, "error": "儲存失敗"}
    
    def search_memory(self, user_id: str, query: str, limit: int = 5) -> Dict:
        """搜尋記憶（簡單的關鍵字匹配）"""
        memories = self._load_memories(user_id)
        
        # 簡單的關鍵字搜尋
        query_lower = query.lower()
        matching_memories = []
        
        for memory in memories:
            memory_text = memory.get("memory", "").lower()
            if query_lower in memory_text:
                matching_memories.append(memory)
        
        # 限制結果數量
        matching_memories = matching_memories[:limit]
        
        logger.info(f"本地記憶搜尋完成: user_id={user_id}, found={len(matching_memories)}")
        return {"success": True, "memories": matching_memories}
    
    def get_all_memories(self, user_id: str) -> Dict:
        """獲取所有記憶"""
        memories = self._load_memories(user_id)
        return {"success": True, "memories": memories}


# 建立本地記憶管理器實例
local_memory_manager = LocalMemoryManager()


# 測試函數
if __name__ == "__main__":
    # 測試本地記憶管理器
    test_user_id = "test_user_123"
    
    # 新增記憶
    result = local_memory_manager.add_memory(
        test_user_id,
        "我喜歡在台大總圖看書",
        {"type": "preference"}
    )
    print(f"新增記憶: {result}")
    
    # 搜尋記憶
    result = local_memory_manager.search_memory(test_user_id, "台大")
    print(f"搜尋記憶: {result}")
    
    # 獲取所有記憶
    result = local_memory_manager.get_all_memories(test_user_id)
    print(f"所有記憶: {result}")
