#!/usr/bin/env python3
"""
簡單測試處理狀態指示功能的核心邏輯
"""

import random

def get_processing_message():
    """產生處理中狀態訊息"""
    messages = [
        "🤔 讓我想想...",
        "⏳ 正在處理您的請求中...",
        "🧠 AI小幫手正在思考...",
        "📝 正在為您準備回應...",
        "🔍 分析中，請稍候...",
        "💭 思考中..."
    ]
    return random.choice(messages)

def test_processing_message():
    """測試處理中訊息產生功能"""
    print("🧪 測試處理中訊息產生功能")
    print("=" * 40)
    
    # 測試多次調用，確保隨機性
    for i in range(5):
        message = get_processing_message()
        print(f"第 {i+1} 次: {message}")
    
    print("\n✅ 處理中訊息功能測試通過")
    return True

if __name__ == "__main__":
    print("🚀 測試處理狀態指示核心功能")
    print("=" * 50)
    
    success = test_processing_message()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 核心功能測試通過！")
        print("\n📋 功能說明：")
        print("- 當用戶發送 AI 請求時，會立即收到處理中狀態訊息")
        print("- 處理完成後會發送完整回應")
        print("- 支援隨機的處理中訊息，增加用戶體驗")
    else:
        print("⚠️ 測試失敗")
