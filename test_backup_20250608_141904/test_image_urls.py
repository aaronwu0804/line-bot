#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/test_image_urls.py
"""
測試 backup_image_service.py 中的圖片 URL 是否仍然可用
"""

import requests
import time

# 來自 backup_image_service.py 的舊 URL
old_urls = [
    "https://imgur.com/tSNCNn5.jpg",  # 早安鮮花
    "https://imgur.com/KraJJvg.jpg",  # 早安日出
    "https://imgur.com/QwS7nt2.jpg",  # 早安風景
    "https://imgur.com/6VaMZAx.jpg",  # 早安咖啡
    "https://imgur.com/KsvvHpU.jpg"   # 早安花朵
]

# 測試每個 URL
print("測試舊的 Imgur URLs...")
for url in old_urls:
    try:
        response = requests.head(url, timeout=10, 
                              headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        status = response.status_code
        print(f"URL: {url} - 狀態碼: {status} {'(可用)' if status == 200 else '(不可用)'}")
    except Exception as e:
        print(f"URL: {url} - 錯誤: {str(e)}")
    time.sleep(1)  # 稍微暫停以避免請求過於頻繁

# 新的可能可用的 Imgur URLs (確定有效的早安圖片)
new_urls = [
    "https://i.imgur.com/MAtdg1L.jpg",  # 早安花束
    "https://i.imgur.com/XkNVhwA.jpg",  # 早安咖啡
    "https://i.imgur.com/6zYq0Y5.jpg",  # 早安風景
    "https://i.imgur.com/lBjGtim.jpg",  # 早晨陽光
    "https://i.imgur.com/r4Xgdvi.jpg"   # 早安文字
]

print("\n測試新的 Imgur URLs...")
for url in new_urls:
    try:
        response = requests.head(url, timeout=10, 
                              headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        status = response.status_code
        print(f"URL: {url} - 狀態碼: {status} {'(可用)' if status == 200 else '(不可用)'}")
    except Exception as e:
        print(f"URL: {url} - 錯誤: {str(e)}")
    time.sleep(1)  # 稍微暫停以避免請求過於頻繁
