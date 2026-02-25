#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試知識查詢和待辦完成功能
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.peanut_assistant import peanut_assistant

async def test_new_features():
    """測試新增的知識查詢和待辦完成功能"""
    
    test_user_id = "test_user_002"
    
    print("="*80)
    print("測試知識查詢和待辦完成功能")
    print("="*80)
    
    # 先儲存一些知識
    print("\n【步驟 1】儲存知識")
    print("="*80)
    
    knowledge_messages = [
        "花生 今天學到了 Docker 容器技術",
        "花生 學會了 Kubernetes 部署方法",
        "花生 掌握了 CI/CD 流程"
    ]
    
    for msg in knowledge_messages:
        print(f"\n訊息: {msg}")
        result = await peanut_assistant.process_message(test_user_id, msg)
        print(f"回應: {result.get('response', '')[:100]}")
    
    # 查詢知識
    print("\n\n【步驟 2】查詢知識")
    print("="*80)
    
    query_messages = [
        "花生 我學了什麼",
        "花生 查看知識",
        "花生 我的知識"
    ]
    
    for msg in query_messages:
        print(f"\n訊息: {msg}")
        result = await peanut_assistant.process_message(test_user_id, msg)
        print(f"回應:\n{result.get('response', '')}")
        print("-" * 40)
    
    # 創建待辦事項
    print("\n\n【步驟 3】創建待辦事項")
    print("="*80)
    
    todo_messages = [
        "花生 提醒我明天要開會",
        "花生 別忘了寫報告",
        "花生 幫我記得 Python 學習"
    ]
    
    for msg in todo_messages:
        print(f"\n訊息: {msg}")
        result = await peanut_assistant.process_message(test_user_id, msg)
        print(f"回應: {result.get('response', '')[:100]}")
    
    # 查詢待辦
    print("\n\n【步驟 4】查詢待辦")
    print("="*80)
    print("\n訊息: 花生 待辦事項")
    result = await peanut_assistant.process_message(test_user_id, "花生 待辦事項")
    print(f"回應:\n{result.get('response', '')}")
    
    # 標記完成 - 測試多種格式
    print("\n\n【步驟 5】標記待辦完成（測試不同格式）")
    print("="*80)
    
    complete_messages = [
        "花生 開會完成了",
        "花生 完成了寫報告",
        "花生 標記完成 Python 學習"
    ]
    
    for msg in complete_messages:
        print(f"\n訊息: {msg}")
        result = await peanut_assistant.process_message(test_user_id, msg)
        print(f"回應: {result.get('response', '')}")
        print("-" * 40)
    
    # 再次查詢待辦
    print("\n\n【步驟 6】再次查詢待辦（應該看到已完成的項目）")
    print("="*80)
    print("\n訊息: 花生 待辦事項")
    result = await peanut_assistant.process_message(test_user_id, "花生 待辦事項")
    print(f"回應:\n{result.get('response', '')}")
    
    print("\n" + "="*80)
    print("測試完成！")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_new_features())
