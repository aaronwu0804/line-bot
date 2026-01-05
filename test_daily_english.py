#!/usr/bin/env python3
"""
測試每日英語功能
"""

import sys
import os

# 添加專案路徑
sys.path.insert(0, os.path.dirname(__file__))

from src.daily_english_service import get_daily_word, format_daily_english_message, get_word_audio_url

def test_daily_english():
    """測試每日英語功能"""
    print("="*60)
    print("測試每日英語功能")
    print("="*60)
    
    try:
        # 測試獲取單字
        print("\n1. 測試獲取今日單字...")
        word_data = get_daily_word()
        print(f"✓ 成功獲取單字: {word_data['word']}")
        print(f"  詞性: {word_data['pos']}")
        print(f"  意思: {word_data['meaning']}")
        
        # 測試格式化訊息
        print("\n2. 測試格式化訊息...")
        message = format_daily_english_message(word_data)
        print("✓ 成功格式化訊息:")
        print("-"*60)
        print(message)
        print("-"*60)
        
        # 測試語音URL
        print("\n3. 測試語音URL...")
        audio_url = get_word_audio_url(word_data['word'])
        print(f"✓ 成功獲取語音URL: {audio_url}")
        
        print("\n" + "="*60)
        print("✅ 所有測試通過!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_daily_english()
