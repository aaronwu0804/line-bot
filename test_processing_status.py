#!/usr/bin/env python3
"""
測試 LINE Bot 處理狀態指示功能
"""

import sys
import os

# 添加 src 目錄到路徑
sys.path.append('src')

def test_processing_message():
    """測試處理中訊息產生功能"""
    try:
        from line_webhook import get_processing_message
        
        print("🧪 測試處理中訊息產生功能")
        print("=" * 40)
        
        # 測試多次調用，確保隨機性
        for i in range(5):
            message = get_processing_message()
            print(f"第 {i+1} 次: {message}")
        
        print("\n✅ 處理中訊息功能測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

def test_ai_request_detection():
    """測試 AI 請求檢測功能"""
    try:
        from line_webhook import is_ai_request, extract_query
        
        print("\n🧪 測試 AI 請求檢測功能")
        print("=" * 40)
        
        test_cases = [
            ("小幫手，今天天氣如何？", True, "今天天氣如何？"),
            ("花生，推薦一本書", True, "推薦一本書"),
            ("AI: 什麼是人工智慧？", True, "什麼是人工智慧？"),
            ("@ai 幫我翻譯", True, "幫我翻譯"),
            ("你好", False, "你好"),
            ("!小幫手 測試", True, "測試"),
            ("。花生，問題", True, "問題"),
        ]
        
        all_passed = True
        for message, expected_is_ai, expected_query in test_cases:
            is_ai = is_ai_request(message)
            query = extract_query(message)
            
            status = "✅" if is_ai == expected_is_ai else "❌"
            print(f"{status} '{message}' -> AI請求: {is_ai}, 查詢: '{query}'")
            
            if is_ai != expected_is_ai or (is_ai and query != expected_query):
                all_passed = False
        
        if all_passed:
            print("\n✅ AI 請求檢測功能測試通過")
        else:
            print("\n❌ AI 請求檢測功能測試有問題")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 開始測試 LINE Bot 處理狀態指示功能")
    print("=" * 50)
    
    success = True
    
    # 測試處理中訊息
    success &= test_processing_message()
    
    # 測試 AI 請求檢測
    success &= test_ai_request_detection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有測試通過！處理狀態指示功能已準備就緒")
    else:
        print("⚠️ 部分測試失敗，請檢查程式碼")
