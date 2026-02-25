#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試用戶回報的問題場景
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.peanut_assistant import peanut_assistant

async def test_user_scenarios():
    """測試用戶回報的實際場景"""
    
    test_user_id = "test_user_003"
    
    print("="*80)
    print("測試用戶回報的問題場景")
    print("="*80)
    
    test_cases = [
        {
            "name": "測試 1: 儲存知識（應該成功）",
            "message": "花生 今天學到了 Python 的 asyncio 用法",
            "expected": "儲存到知識"
        },
        {
            "name": "測試 2: 創建待辦（之前失敗）",
            "message": "花生 提醒我明天要開會",
            "expected": "新增待辦事項"
        },
        {
            "name": "測試 3: 查詢待辦（之前失敗）",
            "message": "花生 待辦事項",
            "expected": "您的待辦事項"
        },
        {
            "name": "測試 4: 查詢我的待辦（之前失敗）",
            "message": "花生 我的待辦",
            "expected": "待辦事項"
        },
        {
            "name": "測試 5: 查詢知識（長句）",
            "message": "花生 我學了什麼東西",
            "expected": "您儲存的知識"
        },
        {
            "name": "測試 6: 查詢知識（單字，之前誤判為儲存）",
            "message": "花生 知識",
            "expected": "應該查詢知識，不是儲存"
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
            
            # 檢查是否符合預期
            if i == 1 and "儲存到" in response and "知識" in response:
                print("✅ 測試通過")
            elif i == 2 and "新增待辦" in response:
                print("✅ 測試通過")
            elif i in [3, 4] and ("待辦事項" in response or "提醒我明天要開會" in response):
                print("✅ 測試通過")
            elif i == 5 and "知識" in response and "Python" in response:
                print("✅ 測試通過")
            elif i == 6:
                if "儲存到" not in response and ("知識" in response or "沒有" in response):
                    print("✅ 測試通過（正確識別為查詢）")
                else:
                    print("❌ 測試失敗（被誤判為儲存）")
            
        except Exception as e:
            print(f"\n❌ 處理失敗: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("測試完成！")
    print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(test_user_scenarios())
