#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/test_image_urls_reliability.py
"""
測試圖片 URL 的可靠性，檢查哪些圖片 URL 能夠被正常訪問
"""

import requests
import time
import random
import json
from datetime import datetime

# 測試的圖片 URL 列表
test_urls = [
    # Pinterest 早安文字圖片
    "https://i.pinimg.com/originals/e5/73/7c/e5737c44dd061635766b6682a3e42d69.jpg",  # 早安花朵文字
    "https://i.pinimg.com/originals/11/32/7a/11327a45919c5d5104a4ce9eecae58d4.jpg",  # 水彩風格早安
    "https://i.pinimg.com/originals/69/6a/7e/696a7e415b405bd58b6b8c82e2d8d7ff.jpg",  # 早安咖啡文字
    "https://i.pinimg.com/originals/aa/47/60/aa4760f6bee12654d39f576ceadfaa4c.jpg",  # 早安花朵與文字
    "https://i.pinimg.com/originals/64/f8/f2/64f8f2cd3fa0affd248a5d140260f490.jpg",  # 早安陽光問候
    "https://i.pinimg.com/originals/65/d6/ca/65d6ca8877a01c7d2d31e9d43733f20f.jpg",  # 早安芭蕉葉
    "https://i.pinimg.com/originals/d1/27/7d/d1277da3e2cca7c5367c408dac59ccb9.jpg",  # 早安花環
    "https://i.pinimg.com/originals/df/9a/88/df9a88ffa207c8f176cc654505838e66.jpg",  # 早安咖啡方塊文字
    "https://i.pinimg.com/originals/20/c4/32/20c4329c822b4ec5d6d5fe0604c8ed68.jpg",  # 早安樹葉文字
    
    # Pixabay 早安文字圖片
    "https://cdn.pixabay.com/photo/2017/11/06/17/05/good-morning-2924423_1280.jpg",  # 木牌早安文字
    "https://cdn.pixabay.com/photo/2019/12/07/04/17/good-morning-4678832_1280.jpg",  # 早安花卉文字
    "https://cdn.pixabay.com/photo/2018/02/13/22/02/good-morning-3151909_1280.jpg",  # 早安玫瑰
    "https://cdn.pixabay.com/photo/2016/03/09/16/16/woman-1246844_1280.jpg",    # 早安咖啡女孩
    
    # 添加一些新的可能更可靠的 URL
    "https://i.imgur.com/tSNCNn5.jpg",  # 早安鮮花 (Imgur)
    "https://i.imgur.com/KraJJvg.jpg",  # 早安日出 (Imgur)
    "https://i.imgur.com/QwS7nt2.jpg",  # 早安風景 (Imgur)
    
    # Unsplash 早安場景圖片
    "https://images.unsplash.com/photo-1552346989-e069318e20a5?w=800&q=80",  # 清晨咖啡
    "https://images.unsplash.com/photo-1470240731273-7821a6eeb6bd?w=800&q=80",  # 早安日出
    "https://images.unsplash.com/photo-1495197359483-d092478c170a?w=800&q=80",  # 早安花朵
    "https://images.unsplash.com/photo-1414609245224-afa02bfb3fda?w=800&q=80"   # 湖面日出
]

# 測試每個 URL 是否可用
def test_url(url):
    print(f"\n測試 URL: {url}")
    try:
        # 添加隨機的查詢參數以避免緩存
        timestamp = int(time.time() * 1000)
        random_param = random.randint(1000, 9999)
        if "?" in url:
            test_url = f"{url}&_t={timestamp}&_r={random_param}"
        else:
            test_url = f"{url}?_t={timestamp}&_r={random_param}"
            
        # 添加 User-Agent 以模擬瀏覽器請求
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(test_url, headers=headers, timeout=10)
        status_code = response.status_code
        content_size = len(response.content)
        content_type = response.headers.get('Content-Type', 'unknown')
        
        result = {
            "url": url,
            "status_code": status_code,
            "content_size": content_size,
            "content_type": content_type,
            "is_valid": status_code == 200 and content_size > 1000 and "image" in content_type.lower(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if result["is_valid"]:
            print(f"✅ 可用 - 狀態碼: {status_code}, 內容大小: {content_size/1024:.2f} KB, 類型: {content_type}")
        else:
            print(f"❌ 不可用 - 狀態碼: {status_code}, 內容大小: {content_size/1024:.2f} KB, 類型: {content_type}")
            
        return result
    
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        return {
            "url": url,
            "status_code": -1,
            "content_size": -1,
            "content_type": "error",
            "is_valid": False,
            "error": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# 主函數
def main():
    print(f"開始測試 {len(test_urls)} 個圖片 URL...\n")
    
    results = []
    valid_urls = []
    
    for url in test_urls:
        result = test_url(url)
        results.append(result)
        
        if result["is_valid"]:
            valid_urls.append(url)
        
        # 暫停一下，避免請求過於頻繁
        time.sleep(1)
    
    # 輸出統計結果
    valid_count = len(valid_urls)
    print(f"\n\n測試完成! {valid_count}/{len(test_urls)} 個 URL 可用。")
    
    if valid_count > 0:
        print("\n可用的 URL 列表:")
        for url in valid_urls:
            print(f"✅ {url}")
    
    # 保存測試結果
    result_file = "image_urls_test_result.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n測試結果已保存到: {result_file}")
    
    # 返回可用的 URL
    return valid_urls

if __name__ == "__main__":
    valid_urls = main()
