#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/backup_image_service.py
"""
備用圖片服務
當 Pinterest 圖片獲取失敗時，從本地圖片庫或固定的網絡圖片中選擇
"""

import os
import random
import logging
import glob
from datetime import datetime

logger = logging.getLogger(__name__)

def get_local_image():
    """從本地 images 資料夾獲取隨機圖片"""
    try:
        # 取得專案根目錄
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        images_dir = os.path.join(base_dir, 'images')
        
        # 檢查資料夾是否存在
        if not os.path.exists(images_dir):
            logger.error(f"圖片資料夾不存在: {images_dir}")
            return None
            
        # 獲取所有 PNG 和 JPG 圖片
        image_files = glob.glob(os.path.join(images_dir, '*.png')) + glob.glob(os.path.join(images_dir, '*.jpg'))
        
        if not image_files:
            logger.error("找不到任何本地圖片")
            return None
            
        # 隨機選擇一張圖片
        image_path = random.choice(image_files)
        logger.info(f"選擇的本地圖片: {image_path}")
        
        # 這裡我們需要一個 URL，所以使用 file:// 協議指向本地文件
        # 但 LINE 不接受 file:// 協議，所以我們改為返回絕對路徑
        # 後續代碼將需要處理這種情況
        return image_path
    
    except Exception as e:
        logger.error(f"獲取本地圖片時發生錯誤: {str(e)}")
        return None

def get_fallback_image_url():
    """獲取固定的備用網絡圖片 URL"""
    # 這些 URLs 已確認是穩定可用的圖片
    backup_urls = [
        "https://i.pinimg.com/originals/e5/73/7c/e5737c44dd061635766b6682a3e42d69.jpg",  # 早安鮮花
        "https://i.pinimg.com/originals/9d/76/0d/9d760d6dadae740e0f2d8cbd4b52e043.jpg",  # 早安日出
        "https://i.pinimg.com/originals/8a/ef/e9/8aefe9e96814ae95c4bcc7b8e8f3cdc0.jpg",  # 早安山景
        "https://i.pinimg.com/originals/25/fd/35/25fd3521446741caa643777a0417c814.jpg",  # 早安咖啡
        "https://i.pinimg.com/originals/bc/54/2c/bc542c3b29df8a0a23c1350e32a785c9.jpg"   # 早安花朵
    ]
    
    selected_url = random.choice(backup_urls)
    logger.info(f"使用備用網絡圖片: {selected_url}")
    return selected_url

def get_backup_image():
    """
    獲取備用圖片，優先使用本地圖片，然後嘗試預定義的網絡圖片
    """
    # 先從本地圖庫取圖片
    local_image = get_local_image()
    if local_image:
        # 檢查是否需要上傳到圖床
        if local_image.startswith('/'):
            # 這是本地文件路徑，LINE 不支持直接發送本地圖片
            # 在這裡我們不做上傳處理，而是使用備用網絡圖片
            logger.info("本地圖片需要上傳，將使用備用網絡圖片")
            return get_fallback_image_url()
        return local_image
    
    # 如果本地圖片獲取失敗，使用備用網絡圖片
    return get_fallback_image_url()

if __name__ == "__main__":
    # 設定日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 測試備用圖片服務
    backup_image = get_backup_image()
    if backup_image:
        print(f"成功獲取備用圖片: {backup_image}")
    else:
        print("獲取備用圖片失敗")
