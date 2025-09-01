#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/test_image_urls_simple.py
"""
簡單測試圖片 URL 是否可訪問
"""

import requests
import time

# 測試的圖片 URL 列表
test_urls = [
    # Pinterest 早安文字圖片
    "https://i.pinimg.com/originals/e5/73/7c/e5737c44dd061635766b6682a3e42d69.jpg",  # 早安花朵文字
    "https://i.pinimg.com/originals/11/32/7a/11327a45919c5d5104a4ce9eecae58d4.jpg",  # 水彩風格早安
    "https://i.pinimg.com/originals/69/6a/7e/696a7e415b405bd58b6b8c82e2d8d7ff.jpg",  # 早安咖啡文字
    "https://i.pinimg.com/originals/d1/27/7d/d1277da3e2cca7c5367c408dac59ccb9.jpg",  # 早安花環
    
    # Pixabay 早安文字圖片
    "https://cdn.pixabay.com/photo/2017/11/06/17/05/good-morning-2924423_1280.jpg",  # 木牌早安文字
    "https://cdn.pixabay.com/photo/2019/12/07/04/17/good-morning-4678832_1280.jpg",  # 早安花卉文字
    
    # Imgur 早安圖片 (可能更可靠)
    "https://i.imgur.com/tSNCNn5.jpg",  # 早安鮮花
    "https://i.imgur.com/KraJJvg.jpg",  # 早安日出
    
    # Unsplash 早安場景圖片 (通常很可靠)
    "https://images.unsplash.com/photo-1552346989-e069318e20a5?w=800&q=80",  # 清晨咖啡
    "https://images.unsplash.com/photo-1470240731273-7821a6eeb6bd?w=800&q=80"   # 早安日出
]

print("開始測試圖片 URL...")

# 測試每個 URL
for url in test_urls:
    print(f"\n測試: {url}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        status_code = response.status_code
        content_size = len(response.content) / 1024  # KB
        content_type = response.headers.get('Content-Type', 'unknown')
        
        print(f"  狀態碼: {status_code}")
        print(f"  內容大小: {content_size:.2f} KB")
        print(f"  內容類型: {content_type}")
        
        if status_code == 200 and content_size > 5 and "image" in content_type.lower():
            print(f"  ✅ 可用")
        else:
            print(f"  ❌ 不可用")
            
    except Exception as e:
        print(f"  ❌ 錯誤: {str(e)}")
    
    time.sleep(1)  # 暫停一秒，避免請求過快

print("\n測試完成！")
