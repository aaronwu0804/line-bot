#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試自然語言取消/完成待辦功能
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.peanut_assistant import peanut_assistant

async def test_natural_language_todo():
    """測試自然語言的待辦操作"""
    
    test_user_id = "test_user_004"
    
    print("="*80)
    print("測試自然語言的待辦操作")
    print("="*80)
    
    # 1. 創建一些待辦
    print("\n【步驟 1】創建待辦事項")
    print("="*80)
    
    create_messages = [
        "花生 提醒我明天要開會",
        "花生 別忘了寫報告",
        "花生 幫我記得 Python 學習"
    ]
    
    for msg in create_messages:
        print(f"\n訊息: {msg}")
        result = await peanut_assistant.process_message(test_user_id, msg)
        print(f"回應: {result.get('response', '')[:100]}")
    
    # 2. 查看待辦
    print("\n\n【步驟 2】查看待辦事項")
    print("="*80)
    print("訊息: 花生 待辦事項")
    result = await peanut_assistant.process_message(test_user_id, "花生 待辦事項")
    print(f"回應:\n{result.get('response', '')}")
    
    # 3. 測試自然語言取消
    print("\n\n【步驟 3】測試自然語言取消（用戶場景）")
    print("="*80)
    
    cancel_tests = [
        {
            "message": "花生 明天的開會取消了",
            "expected_keyword": "開會",
            "description": "自然語言：明天的開會取消了"
        },
        {
            "message": "花生 寫報告不用了",
            "expected_keyword": "寫報告",
            "description": "自然語言：寫報告不用了"
        }
    ]
    
    for test in cancel_tests:
        print(f"\n{test['description']}")
        print(f"訊息: {test['message']}")
        result = await peanut_assistant.process_message(test_user_id, test['message'])
        response = result.get('response', '')
        print(f"回應: {response}")
        
        if "已刪除待辦" in response and test['expected_keyword'] in response:
            print("✅ 測試通過")
        else:
            print("❌ 測試失敗")
    
    # 4. 測試自然語言完成
    print("\n\n【步驟 4】測試自然語言完成")
    print("="*80)
    
    complete_tests = [
        {
            "message": "花生 Python 學習完成了",
            "expected_keyword": "Python 學習",
            "description": "自然語言：Python 學習完成了"
        }
    ]
    
    for test in complete_tests:
        print(f"\n{test['description']}")
        print(f"訊息: {test['message']}")
        result = await peanut_assistant.process_message(test_user_id, test['message'])
        response = result.get('response', '')
        print(f"回應: {response}")
        
        if "已標記完成" in response and test['expected_keyword'] in response:
            print("✅ 測試通過")
        else:
            print("❌ 測試失敗")
    
    # 5. 最終檢查
    print("\n\n【步驟 5】最終查看待辦事項")
    print("="*80)
    print("訊息: 花生 待辦事項")
    result = await peanut_assistant.process_message(test_user_id, "花生 待辦事項")
    print(f"回應:\n{result.get('response', '')}")
    
    print("\n" + "="*80)
    print("測試完成！")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_natural_language_todo())
