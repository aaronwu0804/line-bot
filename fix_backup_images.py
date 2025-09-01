#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/fix_backup_images.py
"""
修復備用圖片服務，使用穩定可靠的圖片 URL
"""
import os
import requests
import logging
import time
import sys

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 新的穩定圖片 URL 列表
new_image_urls = [
    # Unsplash 上的早安圖片 (免費且穩定)
    "https://images.unsplash.com/photo-1552346989-e069318e20a5?w=800&q=80",  # 早安咖啡
    "https://images.unsplash.com/photo-1470240731273-7821a6eeb6bd?w=800&q=80",  # 日出風景
    "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&q=80",  # 晨光
    "https://images.unsplash.com/photo-1495197359483-d092478c170a?w=800&q=80",  # 鮮花
    "https://images.unsplash.com/photo-1506784242126-2ed647d576c2?w=800&q=80",  # 日出
    
    # Pexels 上的早安圖片 (免費且穩定)
    "https://images.pexels.com/photos/186752/pexels-photo-186752.jpeg?w=800&h=600&auto=compress",  # 日出
    "https://images.pexels.com/photos/226682/pexels-photo-226682.jpeg?w=800&h=600&auto=compress",  # 咖啡
    
    # Pixabay 上的早安圖片 (免費且穩定)
    "https://cdn.pixabay.com/photo/2016/11/29/13/37/christmas-1869902_1280.jpg",  # 早晨咖啡
    "https://cdn.pixabay.com/photo/2016/11/22/19/25/adult-1850181_1280.jpg",  # 早晨伸展
    "https://cdn.pixabay.com/photo/2016/11/18/14/05/brick-wall-1834784_1280.jpg"   # 咖啡
]

def test_urls():
    """測試每個URL並顯示結果"""
    working_urls = []
    
    for url in new_image_urls:
        try:
            logger.info(f"測試 URL: {url}")
            response = requests.get(url, timeout=10, 
                                 headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
            status = response.status_code
            
            if status == 200:
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    logger.info(f"✅ URL 可用 ({content_type})")
                    working_urls.append(url)
                else:
                    logger.warning(f"❌ 不是圖片資源 ({content_type})")
            else:
                logger.warning(f"❌ 狀態碼: {status}")
        except Exception as e:
            logger.error(f"錯誤: {str(e)}")
        
        time.sleep(0.5)  # 稍微暫停以避免請求過於頻繁
    
    return working_urls

def update_backup_image_service(working_urls):
    """更新 backup_image_service.py 文件中的 URL"""
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src/backup_image_service.py')
    
    if not os.path.exists(file_path):
        logger.error(f"檔案不存在: {file_path}")
        return False
    
    # 讀取原始文件內容
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 備份原始檔案
    backup_path = f"{file_path}.bak.{int(time.time())}"
    with open(backup_path, 'w', encoding='utf-8') as file:
        file.write(content)
    logger.info(f"已備份原始文件至: {backup_path}")
    
    # 準備新的 URL 代碼區塊
    url_block = '    backup_urls = [\n'
    for i, url in enumerate(working_urls[:5]):  # 只使用前 5 個有效的 URL
        description = ""
        if "coffee" in url or "咖啡" in url:
            description = "早安咖啡"
        elif "sun" in url or "sunrise" in url or "日出" in url:
            description = "早安日出"
        elif "flower" in url or "鮮花" in url:
            description = "早安花朵"
        elif "morning" in url or "晨光" in url:
            description = "早安晨光"
        else:
            description = "早安風景"
        
        url_block += f'        "{url}",  # {description}'
        if i < len(working_urls[:5]) - 1:
            url_block += '\n'
    url_block += '\n    ]'
    
    # 在內容中找到並替換 backup_urls 數組
    import re
    pattern = r'backup_urls = \[\s*.*?\s*\]'
    new_content = re.sub(pattern, url_block, content, flags=re.DOTALL)
    
    # 寫入更新後的內容
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    logger.info(f"已成功更新 {file_path}")
    return True

def main():
    logger.info("開始測試和更新備用圖片 URL")
    
    # 測試 URL
    working_urls = test_urls()
    logger.info(f"找到 {len(working_urls)} 個可用的圖片 URL")
    
    if not working_urls:
        logger.error("沒有找到可用的圖片 URL，無法更新")
        return 1
    
    # 更新備用圖片服務
    if update_backup_image_service(working_urls):
        logger.info("成功更新備用圖片服務")
    else:
        logger.error("更新備用圖片服務失敗")
        return 1
    
    logger.info("完成！備用圖片服務已更新")
    return 0

if __name__ == "__main__":
    sys.exit(main())
