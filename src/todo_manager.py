#!/usr/bin/env python3
"""
待辦事項管理模組
支援新增、查詢、更新和刪除待辦事項
"""

import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class TodoManager:
    """待辦事項管理器"""
    
    def __init__(self, storage_dir: str = ".cache/todos"):
        """
        初始化待辦事項管理器
        
        Args:
            storage_dir: 待辦事項儲存目錄
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        logger.info(f"待辦事項管理器已初始化，儲存目錄: {storage_dir}")
    
    def _get_user_file(self, user_id: str) -> str:
        """獲取用戶待辦事項檔案路徑"""
        return os.path.join(self.storage_dir, f"{user_id}_todos.json")
    
    def _load_todos(self, user_id: str) -> List[Dict]:
        """載入用戶的待辦事項"""
        file_path = self._get_user_file(user_id)
        
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入待辦事項失敗: {e}")
            return []
    
    def _save_todos(self, user_id: str, todos: List[Dict]) -> bool:
        """儲存用戶的待辦事項"""
        file_path = self._get_user_file(user_id)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(todos, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"儲存待辦事項失敗: {e}")
            return False
    
    def create_todo(self, user_id: str, content: str, due_date: Optional[str] = None) -> Dict:
        """
        新增待辦事項
        
        Args:
            user_id: 用戶 ID
            content: 待辦事項內容
            due_date: 截止日期（可選）
            
        Returns:
            Dict: 新增結果
        """
        todos = self._load_todos(user_id)
        
        # 解析可能的時間資訊
        parsed_due_date = self._parse_due_date(content, due_date)
        
        new_todo = {
            "id": f"todo_{len(todos) + 1}_{datetime.now().timestamp()}",
            "content": content,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "due_date": parsed_due_date,
            "completed_at": None
        }
        
        todos.append(new_todo)
        
        if self._save_todos(user_id, todos):
            logger.info(f"待辦事項新增成功: user_id={user_id}, content='{content}'")
            return {"success": True, "todo": new_todo}
        else:
            return {"success": False, "error": "儲存失敗"}
    
    def _parse_due_date(self, content: str, due_date: Optional[str] = None) -> Optional[str]:
        """
        從內容中解析截止日期
        
        Args:
            content: 待辦事項內容
            due_date: 明確的截止日期
            
        Returns:
            Optional[str]: 解析後的截止日期 ISO 格式
        """
        if due_date:
            return due_date
        
        # 嘗試從內容中提取時間資訊
        content_lower = content.lower()
        
        # 今天
        if '今天' in content or '今日' in content:
            return datetime.now().date().isoformat()
        
        # 明天
        if '明天' in content or '明日' in content:
            return (datetime.now() + timedelta(days=1)).date().isoformat()
        
        # 後天
        if '後天' in content:
            return (datetime.now() + timedelta(days=2)).date().isoformat()
        
        # 本週
        if '本週' in content or '這週' in content:
            # 設定為本週日
            days_until_sunday = (6 - datetime.now().weekday()) % 7
            return (datetime.now() + timedelta(days=days_until_sunday)).date().isoformat()
        
        # 下週
        if '下週' in content or '下周' in content:
            # 設定為下週一
            days_until_next_monday = (7 - datetime.now().weekday()) % 7 + 7
            return (datetime.now() + timedelta(days=days_until_next_monday)).date().isoformat()
        
        # 嘗試匹配特定日期格式（例如：1/15、01/15、2026/1/15）
        date_pattern = r'(\d{1,4})[/-](\d{1,2})[/-]?(\d{1,2})?'
        match = re.search(date_pattern, content)
        
        if match:
            try:
                if match.group(3):  # 完整日期
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))
                    
                    # 如果年份只有兩位數，假設是 20xx
                    if year < 100:
                        year += 2000
                else:  # 月/日格式
                    month = int(match.group(1))
                    day = int(match.group(2))
                    year = datetime.now().year
                
                parsed_date = datetime(year, month, day).date().isoformat()
                return parsed_date
            except ValueError:
                pass
        
        return None
    
    def update_todo(self, user_id: str, todo_id: Optional[str] = None, 
                   content_keyword: Optional[str] = None, status: str = "completed") -> Dict:
        """
        更新待辦事項狀態
        
        Args:
            user_id: 用戶 ID
            todo_id: 待辦事項 ID（可選）
            content_keyword: 內容關鍵字（用於查找待辦事項，可選）
            status: 新狀態
            
        Returns:
            Dict: 更新結果
        """
        todos = self._load_todos(user_id)
        
        updated_count = 0
        
        for todo in todos:
            # 根據 ID 或關鍵字查找待辦事項
            match = False
            
            if todo_id and todo["id"] == todo_id:
                match = True
            elif content_keyword and content_keyword in todo["content"]:
                match = True
            
            if match and todo["status"] == "pending":
                todo["status"] = status
                if status == "completed":
                    todo["completed_at"] = datetime.now().isoformat()
                updated_count += 1
        
        if updated_count > 0:
            if self._save_todos(user_id, todos):
                logger.info(f"待辦事項更新成功: user_id={user_id}, updated={updated_count}")
                return {"success": True, "updated_count": updated_count}
            else:
                return {"success": False, "error": "儲存失敗"}
        else:
            return {"success": False, "error": "找不到匹配的待辦事項"}
    
    def query_todos(self, user_id: str, status: Optional[str] = None, 
                   days: Optional[int] = None) -> Dict:
        """
        查詢待辦事項
        
        Args:
            user_id: 用戶 ID
            status: 過濾狀態（pending/completed）
            days: 查詢最近 N 天的待辦事項
            
        Returns:
            Dict: 查詢結果
        """
        todos = self._load_todos(user_id)
        
        # 過濾條件
        filtered_todos = todos
        
        if status:
            filtered_todos = [t for t in filtered_todos if t["status"] == status]
        
        if days:
            cutoff_date = (datetime.now() - timedelta(days=days)).date()
            filtered_todos = [
                t for t in filtered_todos
                if datetime.fromisoformat(t["created_at"]).date() >= cutoff_date
            ]
        
        logger.info(f"待辦事項查詢完成: user_id={user_id}, found={len(filtered_todos)}")
        return {"success": True, "todos": filtered_todos, "count": len(filtered_todos)}
    
    def delete_todo(self, user_id: str, todo_id: Optional[str] = None, 
                    content_keyword: Optional[str] = None) -> Dict:
        """
        刪除待辦事項
        
        Args:
            user_id: 用戶 ID
            todo_id: 待辦事項 ID（可選）
            content_keyword: 內容關鍵字（可選，用於模糊匹配）
            
        Returns:
            Dict: 刪除結果，包含 deleted_count
        """
        todos = self._load_todos(user_id)
        original_count = len(todos)
        
        if todo_id:
            # 根據 ID 刪除
            filtered_todos = [t for t in todos if t["id"] != todo_id]
        elif content_keyword:
            # 根據關鍵字刪除（只刪除待完成的）
            filtered_todos = [
                t for t in todos 
                if not (t["status"] == "pending" and content_keyword in t["content"])
            ]
        else:
            return {"success": False, "error": "必須提供 todo_id 或 content_keyword"}
        
        deleted_count = original_count - len(filtered_todos)
        
        if deleted_count > 0:
            if self._save_todos(user_id, filtered_todos):
                logger.info(f"待辦事項刪除成功: user_id={user_id}, deleted_count={deleted_count}")
                return {"success": True, "deleted_count": deleted_count}
            else:
                return {"success": False, "error": "儲存失敗"}
        else:
            return {"success": False, "error": "找不到指定的待辦事項", "deleted_count": 0}
    
    def format_todos_for_display(self, todos: List[Dict]) -> str:
        """
        格式化待辦事項為顯示文字
        
        Args:
            todos: 待辦事項列表
            
        Returns:
            str: 格式化的文字
        """
        if not todos:
            return "目前沒有待辦事項"
        
        lines = ["📋 您的待辦事項：\n"]
        
        # 分類顯示
        pending_todos = [t for t in todos if t["status"] == "pending"]
        completed_todos = [t for t in todos if t["status"] == "completed"]
        
        if pending_todos:
            lines.append("⏳ 待完成：")
            for i, todo in enumerate(pending_todos, 1):
                content = todo["content"]
                due_date = todo.get("due_date")
                
                if due_date:
                    try:
                        due_date_obj = datetime.fromisoformat(due_date).date()
                        today = datetime.now().date()
                        
                        if due_date_obj == today:
                            due_str = "今天"
                        elif due_date_obj == today + timedelta(days=1):
                            due_str = "明天"
                        else:
                            due_str = due_date_obj.strftime("%m/%d")
                        
                        lines.append(f"{i}. {content} (截止：{due_str})")
                    except:
                        lines.append(f"{i}. {content}")
                else:
                    lines.append(f"{i}. {content}")
            lines.append("")
        
        if completed_todos:
            lines.append("✅ 已完成：")
            for i, todo in enumerate(completed_todos, 1):
                content = todo["content"]
                completed_at = todo.get("completed_at")
                
                if completed_at:
                    try:
                        completed_date = datetime.fromisoformat(completed_at).strftime("%m/%d")
                        lines.append(f"{i}. {content} ({completed_date})")
                    except:
                        lines.append(f"{i}. {content}")
                else:
                    lines.append(f"{i}. {content}")
        
        return "\n".join(lines)


# 建立全域實例
todo_manager = TodoManager()


# 測試函數
if __name__ == "__main__":
    # 測試待辦事項管理器
    test_user_id = "test_user_123"
    
    # 新增待辦事項
    result = todo_manager.create_todo(test_user_id, "明天要開會")
    print(f"新增待辦: {result}")
    
    result = todo_manager.create_todo(test_user_id, "買菜")
    print(f"新增待辦: {result}")
    
    # 查詢待辦事項
    result = todo_manager.query_todos(test_user_id, status="pending")
    print(f"查詢待辦: {result}")
    
    # 格式化顯示
    if result["success"]:
        formatted = todo_manager.format_todos_for_display(result["todos"])
        print(formatted)
    
    # 更新待辦事項
    result = todo_manager.update_todo(test_user_id, content_keyword="開會", status="completed")
    print(f"更新待辦: {result}")
    
    # 再次查詢
    result = todo_manager.query_todos(test_user_id)
    print(f"查詢所有待辦: {result}")
    
    if result["success"]:
        formatted = todo_manager.format_todos_for_display(result["todos"])
        print(formatted)
