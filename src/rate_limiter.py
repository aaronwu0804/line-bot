#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/rate_limiter.py
"""
流量控制模組
用於處理 API 請求的限流和重試，以避免超過 API 配額限制
"""

import time
import logging
import threading
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    API 流量限制器
    用於控制向 API 發送請求的頻率，避免觸發配額限制
    
    支持:
    - 每分鐘請求數限制
    - 每日請求數限制
    - 重試機制
    """
    
    def __init__(self, requests_per_minute=10, requests_per_day=60, retry_after=5):
        """
        初始化流量限制器
        
        參數:
            requests_per_minute: 每分鐘最大請求數
            requests_per_day: 每日最大請求數
            retry_after: 重試前等待的秒數
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
        self.retry_after = retry_after
        
        # 請求歷史記錄
        self.minute_requests = deque(maxlen=requests_per_minute)
        self.daily_requests = deque(maxlen=requests_per_day)
        
        # 計數器和鎖
        self._lock = threading.Lock()
        self._daily_count = 0
        self._minute_count = 0
        self._reset_time = datetime.now() + timedelta(days=1)
        
    def _clean_old_requests(self):
        """清理過期的請求歷史"""
        now = datetime.now()
        
        # 清理一分鐘前的請求
        while self.minute_requests and (now - self.minute_requests[0]).total_seconds() > 60:
            self.minute_requests.popleft()
            self._minute_count -= 1
            
        # 清理一天前的請求
        while self.daily_requests and (now - self.daily_requests[0]).total_seconds() > 86400:
            self.daily_requests.popleft()
            self._daily_count -= 1
            
        # 檢查是否需要重置每日計數器
        if now >= self._reset_time:
            logger.info("重置每日 API 請求計數器")
            self._daily_count = 0
            self.daily_requests.clear()
            # 設定下一個重置時間
            self._reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    def wait_if_needed(self):
        """
        檢查是否需要等待，並在必要時等待
        
        返回:
            True 如果可以繼續請求
            False 如果已達到每日限制
        """
        with self._lock:
            self._clean_old_requests()
            
            # 檢查每日請求限制
            if self._daily_count >= self.requests_per_day:
                logger.warning(f"已達到每日請求限制 ({self.requests_per_day})，請求被拒絕")
                return False
                
            # 檢查每分鐘請求限制
            while self._minute_count >= self.requests_per_minute:
                oldest = self.minute_requests[0]
                now = datetime.now()
                # 計算需要等待的時間
                time_passed = (now - oldest).total_seconds()
                if time_passed < 60:
                    wait_time = 61 - time_passed  # 多等 1 秒以確保安全
                    logger.info(f"已達到每分鐘請求限制，等待 {wait_time:.1f} 秒")
                    # 釋放鎖，等待後重新獲取
                    self._lock.release()
                    time.sleep(wait_time)
                    self._lock.acquire()
                    self._clean_old_requests()
                else:
                    # 如果最舊的請求已經超過一分鐘，應該已經被 _clean_old_requests 清理
                    # 但以防萬一，我們再次檢查
                    self._clean_old_requests()
                    break
            
            # 記錄新請求
            now = datetime.now()
            self.minute_requests.append(now)
            self.daily_requests.append(now)
            self._minute_count += 1
            self._daily_count += 1
            
            logger.info(f"API 請求計數: 每分鐘 {self._minute_count}/{self.requests_per_minute}, 每日 {self._daily_count}/{self.requests_per_day}")
            
            return True
    
    def execute_with_rate_limit(self, func, *args, max_retries=3, **kwargs):
        """
        執行函數，並在必要時進行重試和限流
        
        參數:
            func: 要執行的函數
            *args, **kwargs: 傳給函數的參數
            max_retries: 最大重試次數
        
        返回:
            函數的執行結果
        """
        retry_count = 0
        last_error = None
        
        while retry_count <= max_retries:
            if not self.wait_if_needed():
                return None, "已達到每日 API 請求限制，請明天再試"
            
            try:
                result = func(*args, **kwargs)
                return result, None
            except Exception as e:
                last_error = e
                logger.error(f"API 呼叫失敗 (嘗試 {retry_count + 1}/{max_retries + 1}): {str(e)}")
                
                if "429" in str(e) and "quota" in str(e).lower():
                    # 配額限制錯誤，等待後重試
                    retry_delay = self.retry_after
                    # 嘗試從錯誤中提取建議的等待時間
                    try:
                        import re
                        match = re.search(r'retry_delay\s*{\s*seconds:\s*(\d+)\s*}', str(e))
                        if match:
                            retry_delay = int(match.group(1))
                    except:
                        pass
                    
                    logger.info(f"遇到配額限制，等待 {retry_delay} 秒後重試...")
                    time.sleep(retry_delay)
                    retry_count += 1
                else:
                    # 非配額限制錯誤，直接返回錯誤
                    return None, str(e)
        
        # 如果所有重試都失敗，返回最後一個錯誤
        return None, f"在 {max_retries + 1} 次嘗試後仍然失敗: {str(last_error)}"

# 全域流量限制器實例 - 調整限制以適應實際使用情況
gemini_limiter = RateLimiter(
    requests_per_minute=2,   # 降低每分鐘請求數限制
    requests_per_day=30,     # 降低每日請求數限制
    retry_after=60          # 增加重試間隔
)
