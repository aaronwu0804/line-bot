#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試待辦創建關鍵字移除
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.peanut_assistant import peanut_assistant

async def test_keyword_removal():
    """測試待辦創建時關鍵字移除"""
    
    test_user_id = "test_user_006"
    
    print("="*80)
    print("測試待辦創建關鍵字移除")
    print("="*80)
    
    test_cases = [
        {
            "name": "測試 1: 加入待辦",
            "message": "花生 加入待辦 2/27 要去大巨蛋看棒球賽",
            "expected_content": "2/27 要去大巨蛋看棒球賽"
        },
        {
            "name": "測試 2: 提醒",
            "message": "花生 提醒 3/6 去宜蘭夏令營",
            "expected_content": "3/6 去宜蘭夏令營"
        },
        {
            "name": "測試 3: 新增事項",
            "message": "花生 新增事項 3/8 去竹南法會",
            "expected_content": "3/8 去竹南法會"
        },
        {
            "name": "測試 4: 提醒我",
            "message": "花生 提醒我明天要開會",
            "expected_content": "明天要開會"
        },
        {
            "name": "測試 5: 新增（單字）",
            "message": "花生 新增 買菜",
            "expected_content": "買菜"
        },
        {
            "name": "測試 6: 空內容（應該失敗）",
            "message": "花生 加入待辦",
            "expected_content": None
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*80}")
        print(f"{test_case['name']}")
        print(f"{'='*80}")
        print(f"訊息: {test_case['message']}")
        print(f"預期內容: {test_case['expected_content']}")
        
        try:
            result = await peanut_assistant.process_message(test_user_id, test_case['message'])
            
            response = result.get('response', '無回應')
            print(f"\n實際回應:\n{response}")
            
            # 檢查是否符合預期
            if test_case['expected_content']:
                if test_case['expected_content'] in response and "已新增待辦" in response:
                    # 確認不包含關鍵字
                    has_keyword = any(kw in response for kw in ['加入待辦', '新增事項', '新增任務'])
                    if not has_keyword or test_case['expected_content'] == "明天要開會":  # "提醒我"是特例
                        print("✅ 測試通過 - 關鍵字已正確移除")
                    else:
                        print(f"❌ 測試失敗 - 回應中仍包含關鍵字")
                else:
                    print("❌ 測試失敗 - 內容不符合預期")
            else:
                # 預期失敗
                if "請告訴我" in response or "範例" in response:
                    print("✅ 測試通過 - 正確處理空內容")
                else:
                    print("❌ 測試失敗 - 應該要提示用戶")
            
        except Exception as e:
            print(f"\n❌ 處理失敗: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 查看所有待辦
    print(f"\n{'='*80}")
    print("查看所有待辦事項（確認內容正確）")
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
    asyncio.run(test_keyword_removal())
