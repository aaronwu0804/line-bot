import os
import time
from test_pinterest import get_pinterest_image
from datetime import datetime
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('duplicate_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_image_duplicates(num_tests=10):
    """測試連續獲取圖片時的重複情況"""
    image_urls = []
    unique_urls = set()
    
    print(f"\n開始測試：連續獲取 {num_tests} 張圖片")
    logger.info(f"開始測試：連續獲取 {num_tests} 張圖片")
    
    for i in range(num_tests):
        logger.info(f"正在獲取第 {i+1} 張圖片...")
        image_url = get_pinterest_image()
        
        if image_url:
            image_urls.append(image_url)
            unique_urls.add(image_url)
            print(f"成功獲取圖片 {i+1}")
            logger.info(f"成功獲取圖片 {i+1}: {image_url}")
        else:
            print(f"第 {i+1} 次獲取圖片失敗")
            logger.error(f"第 {i+1} 次獲取圖片失敗")
            
        # 暫停 2 秒，避免請求過於頻繁
        time.sleep(2)
    
    # 分析結果
    total_images = len(image_urls)
    unique_images = len(unique_urls)
    duplicate_count = total_images - unique_images
    
    logger.info("\n測試結果摘要：")
    logger.info(f"總共獲取圖片數：{total_images}")
    logger.info(f"不重複圖片數：{unique_images}")
    logger.info(f"重複圖片數：{duplicate_count}")
    logger.info(f"重複率：{(duplicate_count/total_images*100):.1f}%")
    
    # 詳細的重複分析
    url_counts = {}
    for url in image_urls:
        url_counts[url] = url_counts.get(url, 0) + 1
    
    duplicates = {url: count for url, count in url_counts.items() if count > 1}
    if duplicates:
        logger.info("\n重複圖片詳情：")
        for url, count in duplicates.items():
            logger.info(f"圖片 URL: {url}")
            logger.info(f"重複次數: {count}\n")

if __name__ == "__main__":
    test_image_duplicates(10)
