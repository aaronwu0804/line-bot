#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試連結處理（連結分析功能已移除）
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.peanut_assistant import peanut_assistant

async def test_link_handling():
    """測試連結處理 - 連結應該被視為一般聊天"""
    
    test_user_id = "test_user_008"
    
    print("="*80)
    print("測試連結處理（連結分析功能已移除）")
    print("="*80)
    
    test_cases = [
        {
            "name": "測試 1: 發送連結",
            "message": "花生 https://2026baseball.landpress.line.me/eventpage/",
            "expected": "不應該出現「分析連結失敗」"
        },
        {
            "name": "測試 2: 發送連結加文字",
            "message": "花生 看看這個活動 https://example.com",
            "expected": "應該當作一般對話處理"
        },
        {
            "name": "測試 3: 一般對話",
            "message": "花生 你好",
            "expected": "需要 AI 回應"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*80}")
        print(f"{test_case['name']}")
        print(f"{'='*80}")
        print(f"訊息: {test_case['message']}")
        print(f"預期: {test_case['expected']}")
        
        try:
            result = await peanut_assistant.process_message(test_user_id, test_case['message'])
            
            response = result.get('response', '無回應')
            needs_ai = result.get('needs_ai_response', False)
            
            print(f"\n實際回應: {response}")
            print(f"需要 AI 回應: {needs_ai}")
            
            # 檢查結果
            if "分析連結失敗" in response:
                print("❌ 測試失敗 - 仍然嘗試分析連結")
            elif needs_ai:
                print("✅ 測試通過 - 連結被視為一般對話")
            else:
                print("⚠️  回應不需要 AI（可能被其他功能處理）")
            
        except Exception as e:
            print(f"\n❌ 處理失敗: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("測試完成！")
    print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(test_link_handling())
