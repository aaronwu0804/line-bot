#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試用戶回報的待辦創建問題
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.peanut_assistant import peanut_assistant

async def test_user_todo_issue():
    """測試用戶回報的待辦創建問題"""
    
    test_user_id = "test_user_005"
    
    print("="*80)
    print("測試用戶回報的待辦創建問題")
    print("="*80)
    
    test_cases = [
        {
            "name": "測試 1: 提醒 + 日期格式",
            "message": "花生 提醒 2/27 要去大巨蛋看棒球賽",
            "expected": "新增待辦"
        },
        {
            "name": "測試 2: 新增事項 + 日期格式",
            "message": "花生 新增事項 2/27 要去大巨蛋看棒球賽",
            "expected": "新增待辦"
        },
        {
            "name": "測試 3: 提醒我（原有功能）",
            "message": "花生 提醒我明天要開會",
            "expected": "新增待辦"
        },
        {
            "name": "測試 4: 新增（單字）",
            "message": "花生 新增 3/1 交報告",
            "expected": "新增待辦"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"{test_case['name']}")
        print(f"{'='*80}")
        print(f"訊息: {test_case['message']}")
        print(f"預期: {test_case['expected']}")
        
        try:
            result = await peanut_assistant.process_message(test_user_id, test_case['message'])
            
            response = result.get('response', '無回應')
            print(f"\n實際回應:\n{response}")
            
            # 檢查是否成功
            if "新增待辦" in response or "已新增待辦" in response:
                print("✅ 測試通過")
            else:
                print("❌ 測試失敗")
            
        except Exception as e:
            print(f"\n❌ 處理失敗: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 查看所有待辦
    print(f"\n{'='*80}")
    print("查看所有待辦事項")
    print(f"{'='*80}")
    print("訊息: 花生 待辦事項")
    
    try:
        result = await peanut_assistant.process_message(test_user_id, "花生 待辦事項")
        print(f"\n回應:\n{result.get('response', '')}")
    except Exception as e:
        print(f"\n❌ 處理失敗: {str(e)}")
    
    print(f"\n{'='*80}")
    print("測試完成！")
    print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(test_user_todo_issue())
