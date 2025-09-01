#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/test_image_urls_expanded.py
"""
測試各種不同來源的圖片 URL，找出可靠的替換方案
"""

import requests
import time
import datetime

print(f"開始時間: {datetime.datetime.now()}")

def test_url(url, description=''):
    """測試URL並顯示是否可用"""
    try:
        print(f"測試 URL: {url} {description}")
        response = requests.get(url, timeout=10, 
                             headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        status = response.status_code
        print(f"狀態碼: {status} {'✅ 可用' if status == 200 else '❌ 不可用'}")
        if status == 200:
            content_type = response.headers.get('content-type', '')
            print(f"內容類型: {content_type}")
            if 'image' in content_type:
                print(f"✅ 確認為圖片資源")
                return True
            else:
                print(f"❌ 不是圖片資源")
                return False
        return False
    except Exception as e:
        print(f"錯誤: {str(e)}")
        return False

print("\n===== 測試穩定的早安圖片 URL =====")

# 嘗試不同的可靠服務圖片 URL
image_sources = [
    # Unsplash 上的早安圖片 (免費且穩定)
    {
        'url': 'https://images.unsplash.com/photo-1552346989-e069318e20a5',
        'description': '- Unsplash 早安咖啡'
    },
    {
        'url': 'https://images.unsplash.com/photo-1470240731273-7821a6eeb6bd',
        'description': '- Unsplash 日出風景'
    },
    {
        'url': 'https://images.unsplash.com/photo-1500382017468-9049fed747ef',
        'description': '- Unsplash 晨光'
    },
    {
        'url': 'https://images.unsplash.com/photo-1495197359483-d092478c170a',
        'description': '- Unsplash 鮮花'
    },
    {
        'url': 'https://images.unsplash.com/photo-1506784242126-2ed647d576c2',
        'description': '- Unsplash 日出'
    },
    
    # Pexels 上的早安圖片 (免費且穩定)
    {
        'url': 'https://images.pexels.com/photos/186752/pexels-photo-186752.jpeg',
        'description': '- Pexels 日出'
    },
    {
        'url': 'https://images.pexels.com/photos/226682/pexels-photo-226682.jpeg',
        'description': '- Pexels 咖啡'
    },
    
    # Pixabay 上的早安圖片 (免費且穩定)
    {
        'url': 'https://cdn.pixabay.com/photo/2016/11/29/13/37/christmas-1869902_1280.jpg',
        'description': '- Pixabay 早晨咖啡'
    },
    {
        'url': 'https://cdn.pixabay.com/photo/2016/11/22/19/25/adult-1850181_1280.jpg',
        'description': '- Pixabay 早晨伸展'
    },
    
    # Cloudinary 演示賬號圖片 (如果你已經有一個設置好的)
    {
        'url': 'https://res.cloudinary.com/demo/image/upload/v1312461204/sample.jpg',
        'description': '- Cloudinary 樣品圖片'
    },
]

successful_urls = []

# 測試每個 URL
print("測試各種圖片來源...")
for source in image_sources:
    if test_url(source['url'], source['description']):
        successful_urls.append({
            'url': source['url'],
            'description': source['description']
        })
    time.sleep(1)  # 稍微暫停以避免請求過於頻繁

print(f"\n成功找到 {len(successful_urls)} 個有效圖片 URL")
if successful_urls:
    print("\n可用來替換的圖片 URL:")
    for idx, source in enumerate(successful_urls):
        print(f"{idx+1}. {source['url']} {source['description']}")

print(f"\n結束時間: {datetime.datetime.now()}")
