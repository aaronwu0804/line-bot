#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試待辦去重功能
"""

import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.peanut_assistant import peanut_assistant

async def test_duplicate_prevention():
    """測試待辦去重功能"""
    
    test_user_id = "test_user_007"
    
    print("="*80)
    print("測試待辦去重功能")
    print("="*80)
    
    # 測試 1: 創建第一個待辦
    print("\n【測試 1】創建第一個待辦")
    print("="*80)
    msg1 = "花生 加入待辦 2/27 要去大巨蛋看棒球賽"
    print(f"訊息: {msg1}")
    
    result1 = await peanut_assistant.process_message(test_user_id, msg1)
    print(f"回應:\n{result1.get('response', '')}")
    
    # 測試 2: 立即創建相同的待辦（應該被去重）
    print("\n\n【測試 2】立即創建相同的待辦（應該被去重）")
    print("="*80)
    msg2 = "花生 加入待辦 2/27 要去大巨蛋看棒球賽"
    print(f"訊息: {msg2}")
    print("預期: 應該檢測到重複，不創建新的")
    
    result2 = await peanut_assistant.process_message(test_user_id, msg2)
    response2 = result2.get('response', '')
    print(f"回應:\n{response2}")
    
    if "已新增" in response2:
        print("✅ 測試通過 - 檢測到重複，未創建新待辦")
    else:
        print("❌ 測試失敗 - 應該要檢測到重複")
    
    # 測試 3: 創建不同的待辦
    print("\n\n【測試 3】創建不同的待辦")
    print("="*80)
    msg3 = "花生 提醒 3/6 去宜蘭夏令營"
    print(f"訊息: {msg3}")
    
    result3 = await peanut_assistant.process_message(test_user_id, msg3)
    print(f"回應:\n{result3.get('response', '')}")
    
    # 測試 4: 查看待辦清單
    print("\n\n【測試 4】查看待辦清單（應該只有 2 個，不是 3 個）")
    print("="*80)
    
    result4 = await peanut_assistant.process_message(test_user_id, "花生 待辦事項")
    response4 = result4.get('response', '')
    print(f"回應:\n{response4}")
    
    # 計算待辦數量
    import re
    pending_todos = re.findall(r'^\d+\.', response4, re.MULTILINE)
    todo_count = len(pending_todos)
    
    if todo_count == 2:
        print(f"✅ 測試通過 - 只有 2 個待辦（去重成功）")
    else:
        print(f"❌ 測試失敗 - 有 {todo_count} 個待辦（預期 2 個）")
    
    print("\n" + "="*80)
    print("測試完成！")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_duplicate_prevention())
