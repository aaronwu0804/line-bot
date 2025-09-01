#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LINE Bot 關鍵字位置檢測測試工具
================================================

此工具測試 is_ai_request 函數對於不同位置的關鍵字的行為。
用於確認只有訊息開頭或開頭附近的關鍵字才能觸發AI回應。
"""

import os
import sys
import logging
import importlib.util
from datetime import datetime

# 配置日誌
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"keyword_position_test_{datetime.now().strftime('%Y%m%d%H%M%S')}.log")

# 配置 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("keyword_position_test")

def load_function_from_file(file_path, function_name):
    """從檔案載入函數"""
    try:
        # 創建模組名稱
        module_name = os.path.basename(file_path).replace('.py', '')
        
        # 設置 spec
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            logger.error(f"無法從 {file_path} 載入模組")
            return None
        
        # 創建模組
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        
        # 執行模組
        spec.loader.exec_module(module)
        
        # 獲取函數
        if hasattr(module, function_name):
            return getattr(module, function_name)
        else:
            logger.error(f"在 {file_path} 中未找到函數 {function_name}")
            return None
    except Exception as e:
        logger.error(f"載入函數時出錯: {str(e)}")
        return None

def test_is_ai_request():
    """測試不同位置的關鍵字是否觸發 AI 回應"""
    # 從 app.py 載入函數
    app_path = "/Users/al02451008/Documents/code/morning-post/app.py"
    is_ai_request_app = load_function_from_file(app_path, "is_ai_request")
    
    # 從 line_webhook.py 載入函數
    webhook_path = "/Users/al02451008/Documents/code/morning-post/src/line_webhook.py"
    is_ai_request_webhook = load_function_from_file(webhook_path, "is_ai_request")
    
    if not is_ai_request_app or not is_ai_request_webhook:
        logger.error("無法載入函數，測試終止")
        return
    
    # 定義測試案例
    test_cases = [
        # 1. 開頭關鍵字 (應該觸發)
        {"message": "小幫手你好", "expected": True, "desc": "開頭關鍵字"},
        {"message": "花生請告訴我", "expected": True, "desc": "開頭關鍵字"},
        {"message": "AI: 請問", "expected": True, "desc": "開頭關鍵字"},
        {"message": "ai：你好", "expected": True, "desc": "開頭關鍵字"},
        {"message": "@AI 幫我", "expected": True, "desc": "開頭關鍵字"},
        
        # 2. 開頭附近關鍵字 (應該觸發)
        {"message": "！小幫手你好", "expected": True, "desc": "開頭附近關鍵字 (1個字符)"},
        {"message": "，花生請回答", "expected": True, "desc": "開頭附近關鍵字 (1個字符)"},
        {"message": "hi小幫手幫我", "expected": True, "desc": "開頭附近關鍵字 (2個字符)"},
        {"message": "嗨花生告訴我", "expected": True, "desc": "開頭附近關鍵字 (2個字符)"},
        {"message": "你好小幫手，請問", "expected": True, "desc": "開頭附近關鍵字 (3個字符)"},
        
        # 3. 中間或結尾的關鍵字 (不應該觸發)
        {"message": "請問這個小幫手怎麼用", "expected": False, "desc": "中間關鍵字"},
        {"message": "我想了解一下花生的功能", "expected": False, "desc": "中間關鍵字"},
        {"message": "我想要一個小幫手", "expected": False, "desc": "結尾關鍵字"},
        {"message": "可以給我花生嗎", "expected": False, "desc": "結尾關鍵字"},
        {"message": "好像小幫手可以回答這個", "expected": False, "desc": "中間關鍵字"},
        
        # 4. 超過3個字符的位置 (不應該觸發)
        {"message": "你好啊，小幫手幫我", "expected": False, "desc": "開頭超過3個字符"},
        {"message": "請問一下花生可以回答嗎", "expected": False, "desc": "開頭超過3個字符"},
        {"message": "最近天氣如何，小幫手", "expected": False, "desc": "中間關鍵字"}
    ]
    
    # 執行測試
    print("=" * 60)
    print("開始測試 app.py 中的 is_ai_request 函數")
    print("=" * 60)
    
    app_success = 0
    for idx, case in enumerate(test_cases):
        result = is_ai_request_app(case["message"])
        success = result == case["expected"]
        status = "✅ 通過" if success else "❌ 失敗"
        
        if success:
            app_success += 1
        
        print(f"{idx+1}. {status} - {case['desc']}: '{case['message']}' -> 預期: {case['expected']}, 實際: {result}")
    
    print(f"\n結果: {app_success}/{len(test_cases)} 測試通過 ({app_success/len(test_cases)*100:.0f}%)\n")
    
    print("=" * 60)
    print("開始測試 line_webhook.py 中的 is_ai_request 函數")
    print("=" * 60)
    
    webhook_success = 0
    for idx, case in enumerate(test_cases):
        result = is_ai_request_webhook(case["message"])
        success = result == case["expected"]
        status = "✅ 通過" if success else "❌ 失敗"
        
        if success:
            webhook_success += 1
        
        print(f"{idx+1}. {status} - {case['desc']}: '{case['message']}' -> 預期: {case['expected']}, 實際: {result}")
    
    print(f"\n結果: {webhook_success}/{len(test_cases)} 測試通過 ({webhook_success/len(test_cases)*100:.0f}%)")
    
    # 總結果
    print("\n" + "=" * 60)
    print(f"總結: app.py: {app_success}/{len(test_cases)}, line_webhook.py: {webhook_success}/{len(test_cases)}")
    print("=" * 60)
    
    # 寫入日誌
    logger.info(f"測試結果 - app.py: {app_success}/{len(test_cases)}, line_webhook.py: {webhook_success}/{len(test_cases)}")

if __name__ == "__main__":
    print("""
    #########################################################
    #                                                       #
    #        LINE Bot 關鍵字位置檢測測試工具                  #
    #                                                       #
    #########################################################
    """)
    
    test_is_ai_request()
