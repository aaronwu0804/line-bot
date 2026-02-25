#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試花生助手修正後的功能
"""

import asyncio
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.peanut_assistant import peanut_assistant

async def test_messages():
    """測試用戶提供的三個測試案例"""
    
    test_user_id = "test_user_001"
    
    print("="*80)
    print("開始測試花生助手修正後的功能")
    print("="*80)
    
    test_cases = [
        {
            "name": "測試 1: 知識儲存",
            "message": "花生 今天學到了 Python 的 asyncio 用法",
            "expected_intent": "save_content",
            "expected_type": "knowledge"
        },
        {
            "name": "測試 2: 待辦事項查詢",
            "message": "花生 待辦事項",
            "expected_intent": "todo",
            "expected_sub_intent": "query"
        },
        {
            "name": "測試 3: 一般對話",
            "message": "花生，你好",
            "expected_intent": "other"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"{test_case['name']}")
        print(f"{'='*80}")
        print(f"原始訊息: {test_case['message']}")
        
        try:
            result = await peanut_assistant.process_message(test_user_id, test_case['message'])
            
            print(f"\n✅ 處理成功！")
            print(f"回應: {result.get('response', '無回應')}")
            print(f"需要 AI 回應: {result.get('needs_ai_response', False)}")
            
            if 'intent' in result:
                print(f"意圖分類: {result['intent']}")
                
            if 'confidence' in result:
                print(f"信心度: {result['confidence']}")
                
            if result.get('context'):
                print(f"上下文: {result['context'][:100]}...")
                
        except Exception as e:
            print(f"\n❌ 處理失敗: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("測試完成！")
    print(f"{'='*80}")
    
    # 測試待辦事項創建
    print("\n\n額外測試：創建待辦事項")
    print("="*80)
    
    todo_create_message = "花生 提醒我明天要開會"
    print(f"訊息: {todo_create_message}")
    
    try:
        result = await peanut_assistant.process_message(test_user_id, todo_create_message)
        print(f"\n✅ 處理成功！")
        print(f"回應: {result.get('response', '無回應')}")
    except Exception as e:
        print(f"\n❌ 處理失敗: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 再次查詢待辦事項
    print("\n\n再次查詢待辦事項")
    print("="*80)
    
    todo_query_message = "花生 我的待辦"
    print(f"訊息: {todo_query_message}")
    
    try:
        result = await peanut_assistant.process_message(test_user_id, todo_query_message)
        print(f"\n✅ 處理成功！")
        print(f"回應: {result.get('response', '無回應')}")
    except Exception as e:
        print(f"\n❌ 處理失敗: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 執行測試
    asyncio.run(test_messages())
