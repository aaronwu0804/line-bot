#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/test_pinterest.py
"""
直接下載圖片模組（取代原 Pinterest 爬蟲）
使用可靠的圖床服務直接獲取圖片，避免網站爬蟲問題
"""

import os
import random
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_direct_image():
    """直接從可靠圖庫獲取高品質圖片"""
    # 使用精選的免費圖庫圖片 - 僅使用 Unsplash 圖片，因為它們更可靠
    images = [
        # 早安咖啡系列
        "https://images.unsplash.com/photo-1552346989-e069318e20a5?w=800&q=80",     # 清晨咖啡
        "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&q=80",  # 早晨咖啡與報紙
        "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&q=80",  # 精緻咖啡藝術
        "https://images.unsplash.com/photo-1511537190424-bbbab87ac5eb?w=800&q=80",  # 餐桌早餐
        "https://images.unsplash.com/photo-1521123845560-14093637aa7d?w=800&q=80",  # 窗邊咖啡
        "https://images.unsplash.com/photo-1510431198538-e9682f25eb0e?w=800&q=80",  # 早晨咖啡與點心
        "https://images.unsplash.com/photo-1487622750296-6360190669a1?w=800&q=80",  # 陽光下的咖啡
        
        # 日出與晨光系列
        "https://images.unsplash.com/photo-1470240731273-7821a6eeb6bd?w=800&q=80",  # 早安日出
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&q=80",  # 早安晨光
        "https://images.unsplash.com/photo-1414609245224-afa02bfb3fda?w=800&q=80",  # 湖面日出
        "https://images.unsplash.com/photo-1488866022504-f2584929ca5f?w=800&q=80",  # 山間日出
        "https://images.unsplash.com/photo-1506815444479-bfdb1e96c566?w=800&q=80",  # 田野晨光
        "https://images.unsplash.com/photo-1502481851512-e87b74b15e07?w=800&q=80",  # 山頂日出
        "https://images.unsplash.com/photo-1525298633419-35e9575361b4?w=800&q=80",  # 溫馨晨光
        
        # 花草與自然
        "https://images.unsplash.com/photo-1495197359483-d092478c170a?w=800&q=80",  # 早安花朵
        "https://images.unsplash.com/photo-1502977249166-824b3a8a4d6d?w=800&q=80",  # 晨露花朵
        "https://images.unsplash.com/photo-1560717789-0ac7c58ac90a?w=800&q=80",     # 花園晨光
        "https://images.unsplash.com/photo-1556702571-3e11dd2b1a92?w=800&q=80",     # 清新花束
        "https://images.unsplash.com/photo-1445333684355-418ca938fb7c?w=800&q=80",  # 晨霧森林
        
        # 帶有早安問候語的圖片（Unsplash 上的文字元素或閱讀場景）
        "https://images.unsplash.com/photo-1518655061710-5ccf392c275a?w=800&q=80",  # 桌上的筆記本與咖啡
        "https://images.unsplash.com/photo-1546483875-ad9014c88eba?w=800&q=80",     # 書桌與清晨光線
        "https://images.unsplash.com/photo-1587613864521-9ef8dfe617cc?w=800&q=80",  # 筆記與咖啡
        "https://images.unsplash.com/photo-1512274559473-e5244f0348c3?w=800&q=80",  # 早晨閱讀
        "https://images.unsplash.com/photo-1520889905494-a7e1ee909e16?w=800&q=80",  # 文字與花朵
        
        # 添加更多早晨相關的美麗圖片
        "https://images.unsplash.com/photo-1477332552946-cfb384aeaf1c?w=800&q=80",  # 清晨窗戶
        "https://images.unsplash.com/photo-1466198567099-190890d6d6d2?w=800&q=80",  # 書與咖啡
        "https://images.unsplash.com/photo-1529148482759-b35b25c5f217?w=800&q=80",  # 霧氣森林
        "https://images.unsplash.com/photo-1504204267155-aaad8e81290d?w=800&q=80"   # 早安陽光
    ]
    
    # 選擇一張圖片
    image_url = random.choice(images)
    logger.info(f"選擇了圖片 URL: {image_url}")
    return image_url

def get_pinterest_image():
    """
    獲取早安圖片
    
    此函數是為了保持與原有代碼相容，實際上是直接下載圖片，不再使用 Pinterest
    
    Returns:
        str: 圖片的 URL
    """
    try:
        # 1. 嘗試直接從可靠圖庫獲取圖片 URL
        image_url = get_direct_image()
        logger.info(f"成功獲取早安圖片 URL: {image_url}")
        
        # 2. 可選：如果需要下載到本地儲存
        if os.environ.get("SAVE_IMAGES_LOCALLY", "false").lower() == "true":
            # 確保 images 目錄存在
            images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images')
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
                logger.info(f"創建圖片目錄: {images_dir}")
            
            # 下載圖片
            logger.info(f"開始下載圖片...")
            try:
                response = requests.get(image_url, timeout=15)
                
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
                    
                    # 如果需要上傳到圖床，可以在這裡調用上傳功能
                    
                    return filepath
                else:
                    logger.error(f"下載圖片失敗，狀態碼: {response.status_code}")
            except Exception as e:
                logger.error(f"下載圖片時發生錯誤: {str(e)}")

        # 如果不下載到本地或下載失敗，直接返回 URL
        return image_url
        
    except Exception as e:
        logger.error(f"獲取早安圖片失敗: {str(e)}", exc_info=True)
        return None

# 獨立運行時的測試代碼
if __name__ == "__main__":
    # 設定日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    logger.info("=== 測試早安圖片獲取 ===")
    result = get_pinterest_image()
    
    if result:
        if os.path.isfile(result):
            logger.info(f"成功下載圖片到本地: {result}")
            logger.info(f"檔案大小: {os.path.getsize(result) / 1024:.2f} KB")
        else:
            logger.info(f"成功獲取圖片 URL: {result}")
    else:
        logger.error("獲取早安圖片失敗")
