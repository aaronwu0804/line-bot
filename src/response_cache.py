#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/response_cache.py
"""
回應緩存模組
用於緩存 AI 回應，減少 API 調用次數
"""

import os
import json
import time
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class ResponseCache:
    """
    AI 回應緩存類
    緩存來自 AI 模型的回應，以減少 API 調用
    """
    
    def __init__(self, cache_dir=None, cache_ttl=86400):
        """
        初始化緩存
        
        參數:
            cache_dir: 緩存目錄，不指定時使用默認目錄
            cache_ttl: 緩存有效期，單位秒，默認 1 天
        """
        if not cache_dir:
            # 默認在當前工作目錄或專案根目錄的 .cache 子目錄
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cache_dir = os.path.join(root_dir, '.cache')
            
        self.cache_dir = Path(cache_dir)
        self.cache_ttl = cache_ttl
        self._ensure_cache_dir()
        
    def _ensure_cache_dir(self):
        """確保緩存目錄存在"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"緩存目錄: {self.cache_dir}")
        except Exception as e:
            logger.error(f"創建緩存目錄失敗: {str(e)}")
            
    def _get_cache_key(self, prompt):
        """生成緩存鍵"""
        # 使用 SHA-256 雜湊生成緩存鍵
        hash_obj = hashlib.sha256(prompt.encode('utf-8'))
        return hash_obj.hexdigest()
        
    def _get_cache_file(self, cache_key):
        """獲取緩存文件路徑"""
        return self.cache_dir / f"{cache_key}.json"
        
    def get(self, prompt):
        """
        從緩存獲取回應
        
        參數:
            prompt: 提示文本
            
        返回:
            緩存的回應，如果不存在或已過期則返回 None
        """
        cache_key = self._get_cache_key(prompt)
        cache_file = self._get_cache_file(cache_key)
        
        if not cache_file.exists():
            return None
            
        try:
            # 檢查緩存是否過期
            if cache_file.stat().st_mtime < time.time() - self.cache_ttl:
                logger.info(f"緩存已過期: {cache_key}")
                return None
                
            # 讀取緩存
            with cache_file.open('r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            logger.info(f"從緩存獲取回應: {cache_key}")
            return cache_data.get('response')
            
        except Exception as e:
            logger.error(f"讀取緩存失敗: {str(e)}")
            return None
            
    def set(self, prompt, response, ttl=None):
        """
        將回應保存到緩存
        
        參數:
            prompt: 提示文本
            response: 回應文本
            ttl: 緩存有效期（秒），如不指定則使用默認值
            
        返回:
            是否成功保存
        """
        try:
            cache_key = self._get_cache_key(prompt)
            cache_file = self._get_cache_file(cache_key)
            
            # 準備緩存數據
            cache_data = {
                'prompt': prompt,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'ttl': ttl or self.cache_ttl
            }
            
            # 保存緩存
            with cache_file.open('w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"回應已保存到緩存: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"保存緩存失敗: {str(e)}")
            return False
            
    def delete(self, prompt):
        """
        從緩存中刪除特定回應
        
        參數:
            prompt: 提示文本
        
        返回:
            是否成功刪除
        """
        try:
            cache_key = self._get_cache_key(prompt)
            cache_file = self._get_cache_file(cache_key)
            
            if cache_file.exists():
                cache_file.unlink()
                logger.info(f"從緩存中刪除: {cache_key}")
                return True
            return False
        except Exception as e:
            logger.error(f"刪除緩存失敗: {str(e)}")
            return False
            
    def clear_expired(self):
        """清理過期緩存"""
        try:
            count = 0
            now = time.time()
            
            for cache_file in self.cache_dir.glob('*.json'):
                # 檢查文件是否有特殊 TTL
                cache_ttl = self.cache_ttl
                try:
                    with cache_file.open('r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                        if 'ttl' in cache_data and isinstance(cache_data['ttl'], (int, float)):
                            cache_ttl = cache_data['ttl']
                except:
                    pass  # 如果無法讀取，使用默認 TTL

                # 檢查是否過期
                if cache_file.stat().st_mtime < now - cache_ttl:
                    cache_file.unlink()
                    count += 1
                    
            if count > 0:
                logger.info(f"已清理 {count} 個過期緩存")
                
            return count
        except Exception as e:
            logger.error(f"清理緩存時發生錯誤: {str(e)}")
            return 0
            
    def get_stats(self):
        """
        獲取緩存統計資訊
        
        返回:
            dict: 緩存統計資訊
        """
        try:
            stats = {
                "total_files": 0,
                "total_size_bytes": 0,
                "newest_file": None,
                "oldest_file": None,
                "avg_size_bytes": 0
            }
            
            cache_files = list(self.cache_dir.glob('*.json'))
            stats["total_files"] = len(cache_files)
            
            if not cache_files:
                return stats
                
            # 計算總大小
            total_size = 0
            newest_time = 0
            oldest_time = float('inf')
            newest_file = None
            oldest_file = None
            
            for cache_file in cache_files:
                file_size = cache_file.stat().st_size
                total_size += file_size
                
                mtime = cache_file.stat().st_mtime
                if mtime > newest_time:
                    newest_time = mtime
                    newest_file = cache_file.name
                    
                if mtime < oldest_time:
                    oldest_time = mtime
                    oldest_file = cache_file.name
            
            stats["total_size_bytes"] = total_size
            if stats["total_files"] > 0:
                stats["avg_size_bytes"] = total_size / stats["total_files"]
                
            stats["newest_file"] = newest_file
            stats["oldest_file"] = oldest_file
            stats["cache_ttl"] = self.cache_ttl
                
            return stats
        except Exception as e:
            logger.error(f"獲取緩存統計資訊時發生錯誤: {str(e)}")
            return {"error": str(e)}
            
    def clear_all(self):
        """
        清除所有緩存
        
        返回:
            int: 清除的緩存文件數量
        """
        try:
            count = 0
            for cache_file in self.cache_dir.glob('*.json'):
                cache_file.unlink()
                count += 1
                
            if count > 0:
                logger.info(f"已清除所有緩存，共 {count} 個文件")
            return count
        except Exception as e:
            logger.error(f"清除所有緩存時發生錯誤: {str(e)}")
            return 0

# 全局緩存對象
response_cache = ResponseCache(cache_ttl=7*86400)  # 設定緩存有效期為 7 天
