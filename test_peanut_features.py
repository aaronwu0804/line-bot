#!/usr/bin/env python3
"""
花生 AI 小幫手功能測試腳本
測試所有新增功能是否正常運作
"""

import sys
import os
import asyncio

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.intent_classifier import intent_classifier
from src.memory_manager import local_memory_manager
from src.todo_manager import todo_manager
from src.content_manager import content_manager
from src.link_analyzer import link_analyzer, link_storage
from src.peanut_assistant import peanut_assistant

def print_section(title):
    """列印區塊標題"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_intent_classifier():
    """測試意圖分類器"""
    print_section("測試意圖分類器")
    
    test_cases = [
        ("我明天要開會", "todo-create"),
        ("作業完成了", "todo-update"),
        ("查看待辦", "todo-query"),
        ("https://example.com/article", "link"),
        ("今天突然理解了一個道理", "save_content"),
        ("推薦一些音樂", "query"),
        ("你好嗎？", "other"),
    ]
    
    for message, expected in test_cases:
        result = intent_classifier.classify_intent(message)
        intent = result.get("intent")
        sub_intent = result.get("subIntent")
        confidence = result.get("confidence", 0)
        
        status = "✅" if intent in expected else "❌"
        print(f"{status} 訊息: '{message}'")
        print(f"   意圖: {intent} (子意圖: {sub_intent}), 信心度: {confidence:.2f}")

def test_todo_manager():
    """測試待辦事項管理器"""
    print_section("測試待辦事項管理器")
    
    test_user_id = "test_user_123"
    
    # 新增待辦事項
    print("\n1️⃣  新增待辦事項:")
    result = todo_manager.create_todo(test_user_id, "明天下午3點開會")
    if result.get("success"):
        print("   ✅ 新增成功")
        print(f"   內容: {result['todo']['content']}")
        print(f"   截止日期: {result['todo'].get('due_date', '未設定')}")
    
    result = todo_manager.create_todo(test_user_id, "買菜")
    if result.get("success"):
        print("   ✅ 新增成功")
        print(f"   內容: {result['todo']['content']}")
    
    # 查詢待辦事項
    print("\n2️⃣  查詢待辦事項:")
    result = todo_manager.query_todos(test_user_id, status="pending")
    if result.get("success"):
        print(f"   ✅ 找到 {result['count']} 個待辦事項")
        formatted = todo_manager.format_todos_for_display(result["todos"])
        print(formatted)
    
    # 更新待辦事項
    print("\n3️⃣  完成待辦事項:")
    result = todo_manager.update_todo(test_user_id, content_keyword="買菜", status="completed")
    if result.get("success"):
        print(f"   ✅ 已更新 {result['updated_count']} 個待辦事項")
    
    # 再次查詢
    print("\n4️⃣  查詢所有待辦事項:")
    result = todo_manager.query_todos(test_user_id)
    if result.get("success"):
        formatted = todo_manager.format_todos_for_display(result["todos"])
        print(formatted)

def test_content_manager():
    """測試內容管理器"""
    print_section("測試內容管理器")
    
    test_user_id = "test_user_123"
    
    # 儲存不同類型的內容
    print("\n1️⃣  儲存內容:")
    
    contents = [
        ("今天突然理解了慢即是快的道理", "insight"),
        ("學習了 React Hooks 的用法", "knowledge"),
        ("今天跟朋友討論了人生規劃", "memory"),
        ("在 solo 陶喆的蝴蝶", "music"),
        ("去小巨蛋溜冰", "life"),
    ]
    
    for content, content_type in contents:
        result = content_manager.save_content(test_user_id, content, content_type)
        if result.get("success"):
            type_name = content_manager.CONTENT_TYPES.get(content_type)
            print(f"   ✅ 已儲存到 {type_name}: {content[:30]}...")
    
    # 查詢內容
    print("\n2️⃣  查詢所有內容:")
    result = content_manager.query_contents(test_user_id)
    if result.get("success"):
        print(f"   ✅ 找到 {result['count']} 個內容")
        formatted = content_manager.format_contents_for_display(result["contents"])
        print(formatted)
    
    # 獲取統計資訊
    print("\n3️⃣  統計資訊:")
    result = content_manager.get_statistics(test_user_id)
    if result.get("success"):
        stats = result["statistics"]
        print(f"   總數: {stats['total']}")
        for content_type, count in stats.get("by_type", {}).items():
            type_name = content_manager.CONTENT_TYPES.get(content_type)
            print(f"   {type_name}: {count}")

def test_memory_manager():
    """測試記憶管理器"""
    print_section("測試記憶管理器（本地版）")
    
    test_user_id = "test_user_123"
    
    # 新增記憶
    print("\n1️⃣  新增記憶:")
    memories = [
        "我喜歡在台大總圖看書",
        "我妹妹在台大念書",
        "我最喜歡的歌手是陶喆",
    ]
    
    for memory in memories:
        result = local_memory_manager.add_memory(test_user_id, memory)
        if result.get("success"):
            print(f"   ✅ 已新增: {memory}")
    
    # 搜尋記憶
    print("\n2️⃣  搜尋記憶:")
    result = local_memory_manager.search_memory(test_user_id, "台大")
    if result.get("success"):
        print(f"   ✅ 找到 {len(result['memories'])} 個相關記憶")
        for mem in result["memories"]:
            print(f"   - {mem.get('memory', '')}")
    
    # 獲取所有記憶
    print("\n3️⃣  所有記憶:")
    result = local_memory_manager.get_all_memories(test_user_id)
    if result.get("success"):
        print(f"   ✅ 總共 {len(result['memories'])} 個記憶")

def test_link_storage():
    """測試連結儲存"""
    print_section("測試連結儲存")
    
    test_user_id = "test_user_123"
    
    # 儲存連結
    print("\n1️⃣  儲存連結:")
    urls = [
        ("https://techblog.lycorp.co.jp/zh-hant/Boo-Boo-LINE-AI-Assistant", "Booboo 小幽技術文章"),
        ("https://www.google.com", "Google 搜尋"),
    ]
    
    for url, title in urls:
        result = link_storage.save_link(test_user_id, url, title=title)
        if result.get("success"):
            print(f"   ✅ 已儲存: {title}")
    
    # 查詢連結
    print("\n2️⃣  查詢連結:")
    result = link_storage.query_links(test_user_id)
    if result.get("success"):
        print(f"   ✅ 找到 {result['count']} 個連結")
        for link in result["links"]:
            print(f"   - {link.get('title', '')}: {link.get('url', '')}")

async def test_peanut_assistant():
    """測試花生助手整合服務"""
    print_section("測試花生助手整合服務")
    
    test_user_id = "test_user_123"
    
    # 測試待辦事項
    print("\n1️⃣  測試待辦事項:")
    result = await peanut_assistant.process_message(test_user_id, "我後天要參加研討會")
    print(f"{result.get('response', '')}")
    
    # 測試內容儲存
    print("\n2️⃣  測試內容儲存:")
    result = await peanut_assistant.process_message(test_user_id, "今天學到了 Python 的 asyncio 用法")
    print(f"{result.get('response', '')}")
    
    # 測試查詢
    print("\n3️⃣  測試查詢:")
    result = await peanut_assistant.process_message(test_user_id, "查看待辦")
    print(f"{result.get('response', '')}")
    
    # 獲取使用指南
    print("\n4️⃣  使用指南:")
    guide = peanut_assistant.get_usage_guide()
    print(guide)

async def main():
    """主測試函數"""
    print("\n🌟 花生 AI 小幫手功能測試")
    print("測試時間:", os.popen('date').read().strip())
    
    try:
        # 測試各個模組
        test_intent_classifier()
        test_todo_manager()
        test_content_manager()
        test_memory_manager()
        test_link_storage()
        
        # 測試整合服務
        await test_peanut_assistant()
        
        print_section("測試完成")
        print("✅ 所有功能測試完成！")
        print("\n請查看上方輸出，確認各項功能是否正常運作。")
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
