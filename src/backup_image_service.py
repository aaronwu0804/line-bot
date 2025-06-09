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
    # 僅使用穩定可靠的 Unsplash 圖片（經測試，其他來源如 Pinterest、Pixabay、Imgur 均不可靠）
    backup_urls = [
        # 早安咖啡系列
        "https://images.unsplash.com/photo-1552346989-e069318e20a5?w=800&q=80",     # 清晨咖啡
        "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&q=80",  # 早晨咖啡與報紙
        "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&q=80",  # 精緻咖啡藝術
        "https://images.unsplash.com/photo-1511537190424-bbbab87ac5eb?w=800&q=80",  # 餐桌早餐
        "https://images.unsplash.com/photo-1521123845560-14093637aa7d?w=800&q=80",  # 窗邊咖啡
        
        # 日出與晨光系列
        "https://images.unsplash.com/photo-1470240731273-7821a6eeb6bd?w=800&q=80",  # 早安日出
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&q=80",  # 早安晨光
        "https://images.unsplash.com/photo-1414609245224-afa02bfb3fda?w=800&q=80",  # 湖面日出
        "https://images.unsplash.com/photo-1488866022504-f2584929ca5f?w=800&q=80",  # 山間日出
        "https://images.unsplash.com/photo-1506815444479-bfdb1e96c566?w=800&q=80",  # 田野晨光
        
        # 花草與自然
        "https://images.unsplash.com/photo-1495197359483-d092478c170a?w=800&q=80",  # 早安花朵
        "https://images.unsplash.com/photo-1502977249166-824b3a8a4d6d?w=800&q=80",  # 晨露花朵
        "https://images.unsplash.com/photo-1560717789-0ac7c58ac90a?w=800&q=80",     # 花園晨光
        
        # 早安問候與文字 (在照片中呈現文字元素)
        "https://images.unsplash.com/photo-1518655061710-5ccf392c275a?w=800&q=80",  # 桌上的筆記本與咖啡
        "https://images.unsplash.com/photo-1546483875-ad9014c88eba?w=800&q=80",     # 書桌與清晨光線
        "https://images.unsplash.com/photo-1587613864521-9ef8dfe617cc?w=800&q=80"   # 筆記與咖啡
    ]
    
    selected_url = random.choice(backup_urls)
    logger.info(f"使用備用網絡圖片: {selected_url}")
    return selected_url

def upload_image_to_imgbb(image_path):
    """將本地圖片上傳到 ImgBB 圖床"""
    try:
        import base64
        import requests
        import os
        from dotenv import load_dotenv
        
        # 嘗試從 .env.imgbb 文件加載 API 密鑰
        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env.imgbb')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
        
        # 從環境變數獲取 API 密鑰，如果沒有設置則使用默認值
        api_key = os.getenv("IMGBB_API_KEY", "c0262e9328f9505db61c572f15db9f29")
        
        # 讀取圖片並轉為 base64
        with open(image_path, "rb") as file:
            image_data = base64.b64encode(file.read()).decode('utf-8')
        
        # 上傳到 ImgBB
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": api_key,
            "image": image_data,
            "name": os.path.basename(image_path)
        }
        
        response = requests.post(url, payload)
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                image_url = result["data"]["url"]
                logger.info(f"圖片成功上傳到 ImgBB: {image_url}")
                return image_url
        
        logger.error(f"上傳圖片到 ImgBB 失敗: {response.text}")
        return None
    except Exception as e:
        logger.error(f"上傳圖片時發生錯誤: {str(e)}")
        return None

def get_backup_image():
    """
    獲取備用圖片，優先使用本地圖片，然後嘗試預定義的網絡圖片
    """
    # 先從本地圖庫取圖片
    local_image = get_local_image()
    if local_image:
        # 檢查是否需要上傳到圖床
        if local_image.startswith('/'):
            # 嘗試將本地圖片上傳到圖床
            logger.info(f"嘗試上傳本地圖片到圖床: {local_image}")
            image_url = upload_image_to_imgbb(local_image)
            if image_url:
                logger.info(f"成功將本地圖片上傳到圖床: {image_url}")
                return image_url
            else:
                logger.warning("本地圖片上傳失敗，使用備用網絡圖片")
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
