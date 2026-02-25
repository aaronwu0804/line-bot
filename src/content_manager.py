#!/usr/bin/env python3
"""
內容儲存管理模組
支援不同類型內容的分類儲存：insight(靈感)、knowledge(知識)、memory(記憶)、music(音樂)、life(活動)
"""

import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ContentManager:
    """內容儲存管理器"""
    
    # 內容類型定義
    CONTENT_TYPES = {
        "insight": "💡 靈感",
        "knowledge": "📚 知識",
        "memory": "💭 記憶", 
        "music": "🎵 音樂",
        "life": "🎯 活動"
    }
    
    def __init__(self, storage_dir: str = ".cache/contents"):
        """
        初始化內容管理器
        
        Args:
            storage_dir: 內容儲存目錄
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        logger.info(f"內容管理器已初始化，儲存目錄: {storage_dir}")
    
    def _get_user_file(self, user_id: str) -> str:
        """獲取用戶內容檔案路徑"""
        return os.path.join(self.storage_dir, f"{user_id}_contents.json")
    
    def _load_contents(self, user_id: str) -> List[Dict]:
        """載入用戶的內容"""
        file_path = self._get_user_file(user_id)
        
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入內容失敗: {e}")
            return []
    
    def _save_contents(self, user_id: str, contents: List[Dict]) -> bool:
        """儲存用戶的內容"""
        file_path = self._get_user_file(user_id)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(contents, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"儲存內容失敗: {e}")
            return False
    
    def save_content(self, user_id: str, content: str, content_type: str, 
                    tags: Optional[List[str]] = None, metadata: Optional[Dict] = None) -> Dict:
        """
        儲存內容
        
        Args:
            user_id: 用戶 ID
            content: 內容文字
            content_type: 內容類型 (insight/knowledge/memory/music/life)
            tags: 標籤列表（可選）
            metadata: 額外的元數據（可選）
            
        Returns:
            Dict: 儲存結果
        """
        # 驗證內容類型
        if content_type not in self.CONTENT_TYPES:
            logger.warning(f"無效的內容類型: {content_type}，使用預設類型 'memory'")
            content_type = "memory"
        
        contents = self._load_contents(user_id)
        
        new_content = {
            "id": f"content_{len(contents) + 1}_{datetime.now().timestamp()}",
            "content": content,
            "type": content_type,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        contents.append(new_content)
        
        if self._save_contents(user_id, contents):
            logger.info(f"內容儲存成功: user_id={user_id}, type={content_type}")
            return {"success": True, "content": new_content}
        else:
            return {"success": False, "error": "儲存失敗"}
    
    def query_contents(self, user_id: str, content_type: Optional[str] = None,
                      keyword: Optional[str] = None, limit: int = 10) -> Dict:
        """
        查詢內容
        
        Args:
            user_id: 用戶 ID
            content_type: 過濾內容類型（可選）
            keyword: 搜尋關鍵字（可選）
            limit: 返回結果數量限制
            
        Returns:
            Dict: 查詢結果
        """
        contents = self._load_contents(user_id)
        
        # 過濾條件
        filtered_contents = contents
        
        if content_type:
            filtered_contents = [c for c in filtered_contents if c["type"] == content_type]
        
        if keyword:
            keyword_lower = keyword.lower()
            filtered_contents = [
                c for c in filtered_contents
                if keyword_lower in c["content"].lower() or
                   keyword_lower in " ".join(c.get("tags", [])).lower()
            ]
        
        # 按時間排序（最新的在前）
        filtered_contents.sort(key=lambda x: x["created_at"], reverse=True)
        
        # 限制數量
        filtered_contents = filtered_contents[:limit]
        
        logger.info(f"內容查詢完成: user_id={user_id}, found={len(filtered_contents)}")
        return {"success": True, "contents": filtered_contents, "count": len(filtered_contents)}
    
    def delete_content(self, user_id: str, content_id: str) -> Dict:
        """
        刪除內容
        
        Args:
            user_id: 用戶 ID
            content_id: 內容 ID
            
        Returns:
            Dict: 刪除結果
        """
        contents = self._load_contents(user_id)
        
        # 過濾掉要刪除的項目
        filtered_contents = [c for c in contents if c["id"] != content_id]
        
        if len(filtered_contents) < len(contents):
            if self._save_contents(user_id, filtered_contents):
                logger.info(f"內容刪除成功: user_id={user_id}, content_id={content_id}")
                return {"success": True}
            else:
                return {"success": False, "error": "儲存失敗"}
        else:
            return {"success": False, "error": "找不到指定的內容"}
    
    def get_statistics(self, user_id: str) -> Dict:
        """
        獲取用戶的內容統計資訊
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            Dict: 統計資訊
        """
        contents = self._load_contents(user_id)
        
        stats = {
            "total": len(contents),
            "by_type": {}
        }
        
        # 統計各類型數量
        for content_type in self.CONTENT_TYPES:
            count = len([c for c in contents if c["type"] == content_type])
            if count > 0:
                stats["by_type"][content_type] = count
        
        return {"success": True, "statistics": stats}
    
    def format_contents_for_display(self, contents: List[Dict]) -> str:
        """
        格式化內容為顯示文字
        
        Args:
            contents: 內容列表
            
        Returns:
            str: 格式化的文字
        """
        if not contents:
            return "目前沒有儲存的內容"
        
        lines = ["📝 您儲存的內容：\n"]
        
        # 按類型分組
        grouped_contents = {}
        for content in contents:
            content_type = content["type"]
            if content_type not in grouped_contents:
                grouped_contents[content_type] = []
            grouped_contents[content_type].append(content)
        
        # 格式化顯示
        for content_type, items in grouped_contents.items():
            type_name = self.CONTENT_TYPES.get(content_type, content_type)
            lines.append(f"\n{type_name}：")
            
            for i, item in enumerate(items, 1):
                content_text = item["content"]
                created_at = item.get("created_at", "")
                
                # 截斷過長的內容
                if len(content_text) > 50:
                    content_text = content_text[:50] + "..."
                
                # 格式化日期
                try:
                    date_str = datetime.fromisoformat(created_at).strftime("%m/%d")
                    lines.append(f"{i}. {content_text} ({date_str})")
                except:
                    lines.append(f"{i}. {content_text}")
        
        return "\n".join(lines)


# 建立全域實例
content_manager = ContentManager()


# 測試函數
if __name__ == "__main__":
    # 測試內容管理器
    test_user_id = "test_user_123"
    
    # 儲存不同類型的內容
    result = content_manager.save_content(
        test_user_id,
        "今天突然理解了一個人生道理：慢即是快",
        "insight"
    )
    print(f"儲存靈感: {result}")
    
    result = content_manager.save_content(
        test_user_id,
        "學習了 React Hooks 的用法",
        "knowledge", 
        tags=["React", "前端"]
    )
    print(f"儲存知識: {result}")
    
    result = content_manager.save_content(
        test_user_id,
        "在 solo 陶喆的蝴蝶",
        "music"
    )
    print(f"儲存音樂: {result}")
    
    # 查詢內容
    result = content_manager.query_contents(test_user_id)
    print(f"\n查詢所有內容: {result}")
    
    if result["success"]:
        formatted = content_manager.format_contents_for_display(result["contents"])
        print(f"\n{formatted}")
    
    # 獲取統計資訊
    result = content_manager.get_statistics(test_user_id)
    print(f"\n統計資訊: {result}")
