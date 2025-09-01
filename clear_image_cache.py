#!/usr/bin/env python3
"""
清除圖片生成請求的緩存並驗證修正
"""

import sys
import os
sys.path.append('src')

def clear_image_generation_cache():
    """清除圖片生成相關的緩存"""
    try:
        from response_cache import response_cache
        
        # 要清除的圖片生成相關提示
        image_prompts = [
            "生成圖片，一群小孩在打棒球 是室內棒球場",
            "生成圖片,一群小孩在打棒球 是室內棒球場",
            "生成圖片，一群小孩在打棒球是室內棒球場",
            "生成圖片 一群小孩在打棒球 是室內棒球場",
        ]
        
        print("🧹 清除圖片生成請求相關緩存...")
        cleared_count = 0
        
        for prompt in image_prompts:
            if response_cache.delete(prompt):
                print(f"  ✅ 已清除: {prompt[:30]}...")
                cleared_count += 1
            else:
                print(f"  ⚪ 未找到: {prompt[:30]}...")
        
        print(f"\n📊 清除結果: 共清除 {cleared_count} 個緩存項目")
        
        # 顯示緩存統計
        stats = response_cache.get_stats()
        print(f"📈 緩存統計: {stats['total_files']} 個文件, {stats['total_size_bytes']} 字節")
        
        return cleared_count > 0
        
    except ImportError:
        print("❌ 無法導入 response_cache 模組")
        return False
    except Exception as e:
        print(f"❌ 清除緩存時發生錯誤: {str(e)}")
        return False

def test_image_generation_detection():
    """測試圖片生成檢測"""
    try:
        from line_webhook import is_image_generation_request
        
        print("\n🧪 測試圖片生成檢測功能...")
        
        test_cases = [
            ("生成圖片，一群小孩在打棒球 是室內棒球場", True),
            ("幫我畫一張圖", True),
            ("今天天氣如何？", False),
        ]
        
        all_passed = True
        for message, expected in test_cases:
            result = is_image_generation_request(message)
            status = "✅" if result == expected else "❌"
            print(f"  {status} '{message[:20]}...' -> {result}")
            if result != expected:
                all_passed = False
        
        if all_passed:
            print("✅ 圖片生成檢測功能正常")
        else:
            print("❌ 圖片生成檢測功能有問題")
            
        return all_passed
        
    except ImportError:
        print("❌ 無法導入 line_webhook 模組")
        return False
    except Exception as e:
        print(f"❌ 測試時發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 清除圖片生成緩存並驗證修正")
    print("=" * 50)
    
    # 清除緩存
    cache_cleared = clear_image_generation_cache()
    
    # 測試檢測功能
    detection_works = test_image_generation_detection()
    
    print("\n" + "=" * 50)
    if cache_cleared and detection_works:
        print("🎉 緩存清除和功能測試都成功！")
        print("\n📋 下一步:")
        print("1. 在 LINE 中測試：'花生，生成圖片，一群小孩在打棒球'")
        print("2. 應該收到友善的功能說明，而不是 Gemini 回應")
        print("3. 日誌應該顯示：'檢測到圖片生成請求'")
    else:
        print("⚠️ 部分功能需要檢查")
        if not cache_cleared:
            print("- 緩存清除可能失敗")
        if not detection_works:
            print("- 圖片生成檢測功能有問題")
