#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/download_direct_image.py
"""
直接下載圖片用於測試
"""

import os
import logging
import requests
import random
from datetime import datetime

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 確保 images 目錄存在
images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images')
if not os.path.exists(images_dir):
    os.makedirs(images_dir)
    logger.info(f"創建圖片目錄: {images_dir}")

# 使用精選的免費圖庫圖片
images = [
    "https://images.pexels.com/photos/1323550/pexels-photo-1323550.jpeg",  # 海灘日出
    "https://images.pexels.com/photos/1366957/pexels-photo-1366957.jpeg",  # 森林晨光
    "https://images.pexels.com/photos/1287075/pexels-photo-1287075.jpeg",  # 山景日出
    "https://images.pexels.com/photos/1591447/pexels-photo-1591447.jpeg",  # 湖泊清晨
    "https://images.pexels.com/photos/3363362/pexels-photo-3363362.jpeg",  # 咖啡清晨
]

# 選擇一張圖片
image_url = random.choice(images)
logger.info(f"選擇了圖片 URL: {image_url}")

try:
    # 下載圖片
    logger.info(f"開始下載圖片...")
    response = requests.get(image_url, timeout=15)
    logger.info(f"HTTP 狀態碼: {response.status_code}")
    logger.info(f"回應標頭: {response.headers}")
    
    if response.status_code == 200:
        # 保存圖片
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"morning_image_{timestamp}.jpg"
        filepath = os.path.join(images_dir, filename)
        
        logger.info(f"圖片大小: {len(response.content)} 字節")
        logger.info(f"保存圖片到: {filepath}")
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"圖片下載並保存成功: {filepath}")
        
        # 獲取文件大小
        file_size = os.path.getsize(filepath)
        logger.info(f"保存的文件大小: {file_size} 字節")
    else:
        logger.error(f"下載圖片失敗，狀態碼: {response.status_code}")
except Exception as e:
    logger.error(f"發生錯誤: {str(e)}", exc_info=True)
