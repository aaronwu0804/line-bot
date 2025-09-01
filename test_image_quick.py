#!/usr/bin/env python3
# 簡單測試腳本

print("測試輸出")

# 載入 test_pinterest 模塊
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.test_pinterest import get_direct_image
    
    print("模塊載入成功")
    
    # 獲取圖片 URL
    url = get_direct_image()
    print(f"獲取到的圖片 URL: {url}")
    
except Exception as e:
    print(f"出錯: {str(e)}")
