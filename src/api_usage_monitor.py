#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/api_usage_monitor.py
"""
Gemini API 使用監控工具
監控 Gemini API 的使用情況、配額限制和錯誤率
"""

import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 添加主目錄到系統路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("dotenv 未安裝，無法讀取 .env 文件")

class APIUsageMonitor:
    """監控 Gemini API 使用情況"""
    
    def __init__(self, log_file=None, stats_file=None):
        """
        初始化監控器
        
        Args:
            log_file: API調用日誌文件路徑
            stats_file: 統計數據保存路徑
        """
        if not log_file:
            self.log_file = os.path.join(parent_dir, "logs", f"api_usage_{datetime.now().strftime('%Y%m%d')}.log")
        else:
            self.log_file = log_file
            
        if not stats_file:
            self.stats_file = os.path.join(parent_dir, "logs", "api_usage_stats.json")
        else:
            self.stats_file = stats_file
            
        # 確保日誌目錄存在
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # 初始化統計數據
        self.stats = self._load_stats()
        
    def _load_stats(self):
        """載入統計數據"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"載入統計數據失敗: {e}")
        
        # 初始化空統計數據
        return {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "errors": {},
            "models": {},
            "daily_usage": {},
            "hourly_usage": {},
            "quota_limits": {
                "count": 0,
                "last_occurrence": None
            },
            "response_times": [],
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_stats(self):
        """保存統計數據"""
        try:
            self.stats["last_updated"] = datetime.now().isoformat()
            
            # 限制回應時間陣列大小，避免檔案過大
            if "response_times" in self.stats and len(self.stats["response_times"]) > 100:
                self.stats["response_times"] = self.stats["response_times"][-100:]
                
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.warning(f"保存統計數據失敗: {e}")
    
    def get_stats(self):
        """
        獲取API使用統計數據
        
        Returns:
            dict: 統計數據摘要
        """
        # 建立統計數據的摘要版本
        summary = {
            "total_calls": self.stats.get("total_calls", 0),
            "successful_calls": self.stats.get("successful_calls", 0),
            "failed_calls": self.stats.get("failed_calls", 0),
            "error_rate": 0,
            "quota_limits": self.stats.get("quota_limits", {}).get("count", 0),
            "models_used": len(self.stats.get("models", {})),
            "last_updated": self.stats.get("last_updated", ""),
        }
        
        # 計算錯誤率
        if summary["total_calls"] > 0:
            summary["error_rate"] = round((summary["failed_calls"] / summary["total_calls"]) * 100, 2)
        
        # 計算平均響應時間
        response_times = self.stats.get("response_times", [])
        if response_times:
            summary["avg_response_time_ms"] = round(sum(response_times) / len(response_times), 2)
        else:
            summary["avg_response_time_ms"] = 0
            
        # 取得最常用的模型
        models = self.stats.get("models", {})
        if models:
            most_used_model = max(models.items(), key=lambda x: x[1])
            summary["most_used_model"] = {
                "name": most_used_model[0],
                "calls": most_used_model[1]
            }
        
        return summary
    
    def log_api_call(self, model, success, error_code=None, error_message=None, response_time=None):
        """
        記錄API調用
        
        Args:
            model: 使用的模型名稱
            success: 是否成功
            error_code: 錯誤代碼 (如 429, 404)
            error_message: 錯誤訊息
            response_time: 回應時間 (毫秒)
            error_message: 錯誤訊息
            response_time: 回應時間 (毫秒)
        """
        now = datetime.now()
        day = now.strftime('%Y-%m-%d')
        hour = now.strftime('%Y-%m-%d %H:00')
        
        # 更新總調用次數
        self.stats["total_calls"] += 1
        
        if success:
            self.stats["successful_calls"] += 1
        else:
            self.stats["failed_calls"] += 1
            
            # 記錄錯誤信息
            if error_code:
                error_key = f"E{error_code}"
                self.stats["errors"][error_key] = self.stats["errors"].get(error_key, 0) + 1
        
        # 記錄模型使用情況
        if model not in self.stats["models"]:
            self.stats["models"][model] = {"total": 0, "success": 0, "failed": 0}
        
        self.stats["models"][model]["total"] += 1
        if success:
            self.stats["models"][model]["success"] += 1
        else:
            self.stats["models"][model]["failed"] += 1
        
        # 記錄每日使用量
        if day not in self.stats["daily_usage"]:
            self.stats["daily_usage"][day] = {"total": 0, "success": 0, "failed": 0}
        
        self.stats["daily_usage"][day]["total"] += 1
        if success:
            self.stats["daily_usage"][day]["success"] += 1
        else:
            self.stats["daily_usage"][day]["failed"] += 1
            
        # 記錄每小時使用量
        if hour not in self.stats["hourly_usage"]:
            self.stats["hourly_usage"][hour] = {"total": 0, "success": 0, "failed": 0}
        
        self.stats["hourly_usage"][hour]["total"] += 1
        if success:
            self.stats["hourly_usage"][hour]["success"] += 1
        else:
            self.stats["hourly_usage"][hour]["failed"] += 1
            
        # 特殊處理配額限制錯誤 (429)
        if error_code == "429" or (error_message and "429" in str(error_message)):
            self.stats["quota_limits"]["count"] += 1
            self.stats["quota_limits"]["last_occurrence"] = now.isoformat()
            
            # 如果沒有配額限制歷史記錄，則創建
            if "quota_limit_history" not in self.stats:
                self.stats["quota_limit_history"] = []
                
            # 記錄詳細的配額限制事件
            quota_event = {
                "timestamp": now.isoformat(),
                "model": model,
                "message": error_message if error_message else "配額限制"
            }
            self.stats["quota_limit_history"].append(quota_event)
            
            # 限制歷史記錄大小
            if len(self.stats["quota_limit_history"]) > 50:
                self.stats["quota_limit_history"] = self.stats["quota_limit_history"][-50:]
        
        # 記錄回應時間
        if response_time is not None:
            if "response_times" not in self.stats:
                self.stats["response_times"] = []
                
            self.stats["response_times"].append(response_time)
            self.stats["hourly_usage"][hour]["failed"] += 1
        
        # 保存詳細日誌
        log_entry = {
            "timestamp": now.isoformat(),
            "model": model,
            "success": success,
            "response_time_ms": response_time,
        }
        
        if not success:
            log_entry["error_code"] = error_code
            log_entry["error_message"] = error_message
            
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.warning(f"寫入日誌失敗: {e}")
            
        # 保存統計數據
        self._save_stats()
        
    def analyze_usage(self, days=7):
        """分析最近幾天的使用情況"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        print("\n===== Gemini API 使用情況分析 =====")
        print(f"總調用次數: {self.stats['total_calls']}")
        print(f"成功率: {self.stats['successful_calls'] / max(1, self.stats['total_calls']) * 100:.2f}%")
        
        # 錯誤分析
        if self.stats["errors"]:
            print("\n===== 錯誤分佈 =====")
            for error_code, count in sorted(self.stats["errors"].items(), key=lambda x: x[1], reverse=True):
                print(f"{error_code}: {count} 次 ({count / max(1, self.stats['total_calls']) * 100:.2f}%)")
        
        # 模型使用情況
        if self.stats["models"]:
            print("\n===== 模型使用情況 =====")
            for model, data in sorted(self.stats["models"].items(), key=lambda x: x[1]["total"], reverse=True):
                success_rate = data["success"] / max(1, data["total"]) * 100
                print(f"{model}: {data['total']} 次調用, 成功率: {success_rate:.2f}%")
        
        # 最近幾天的使用趨勢
        daily_usage = {k: v for k, v in self.stats["daily_usage"].items() if k >= today}
        if daily_usage:
            print(f"\n===== 最近 {len(daily_usage)} 天的使用趨勢 =====")
            for day, data in sorted(daily_usage.items()):
                success_rate = data["success"] / max(1, data["total"]) * 100
                print(f"{day}: {data['total']} 次調用, 成功率: {success_rate:.2f}%")
        
        return self.stats

def test_api_calls():
    """測試 API 調用監控"""
    from random import choice, random
    
    monitor = APIUsageMonitor()
    
    # 模擬一些 API 調用 (更新為 Gemini 2.5 模型)
    models = ["gemini-2.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    errors = [(None, None), ("429", "Rate limit exceeded"), 
              ("404", "Model not found"), ("400", "Invalid request")]
    
    for _ in range(20):
        model = choice(models)
        success = random() > 0.3  # 70% 成功率
        response_time = int(random() * 1000) + 100  # 100-1100ms
        
        error_code, error_message = None, None
        if not success:
            error_code, error_message = choice(errors)
            
        monitor.log_api_call(model, success, error_code, error_message, response_time)
        
    # 分析使用情況
    monitor.analyze_usage()

def test_gemini_api():
    """測試真實的 Gemini API 調用"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("未找到 GEMINI_API_KEY 環境變數")
        return False
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        monitor = APIUsageMonitor()
        models_to_test = ["gemini-2.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-pro"]
        
        # 測試每個模型
        for model_name in models_to_test:
            try:
                logger.info(f"測試模型: {model_name}")
                start_time = time.time()
                
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("請用一句話介紹台灣")
                
                response_time = (time.time() - start_time) * 1000
                success = response and hasattr(response, 'text') and response.text
                
                if success:
                    logger.info(f"模型 {model_name} 測試成功, 回應時間: {response_time:.2f}ms")
                    logger.info(f"回應: {response.text}")
                    monitor.log_api_call(model_name, True, response_time=response_time)
                else:
                    logger.warning(f"模型 {model_name} 回應無效")
                    monitor.log_api_call(model_name, False, "INVALID_RESPONSE", "Response has no text")
                    
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                error_code = "UNKNOWN"
                if "429" in str(e):
                    error_code = "429"
                elif "404" in str(e):
                    error_code = "404"
                elif "400" in str(e):
                    error_code = "400"
                    
                logger.error(f"測試模型 {model_name} 失敗: {e}")
                monitor.log_api_call(model_name, False, error_code, str(e), response_time)
        
        # 分析使用情況
        monitor.analyze_usage()
        return True
        
    except ImportError:
        logger.error("未安裝 google-generativeai 套件")
        return False

def main():
    """主程序"""
    parser = argparse.ArgumentParser(description="Gemini API 使用監控工具")
    parser.add_argument('--simulate', action='store_true', help="模擬 API 調用進行測試")
    parser.add_argument('--test', action='store_true', help="測試真實的 Gemini API 調用")
    parser.add_argument('--analyze', action='store_true', help="分析現有的使用數據")
    
    args = parser.parse_args()
    
    if args.simulate:
        print("模擬 API 調用進行測試...")
        test_api_calls()
    elif args.test:
        print("測試真實的 Gemini API 調用...")
        test_gemini_api()
    elif args.analyze:
        monitor = APIUsageMonitor()
        monitor.analyze_usage()
    else:
        parser.print_help()
        
if __name__ == "__main__":
    main()
