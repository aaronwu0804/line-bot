#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/test_pinterest_download.py
"""
測試 Pinterest 圖片下載和本地圖片處理
"""

import os
import sys
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 確保可以導入其他模塊
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # 優先從 src 目錄導入
    try:
        from src.test_pinterest import get_pinterest_image
        logger.info("從 src 目錄成功導入 get_pinterest_image")
    except ImportError:
        from test_pinterest import get_pinterest_image
        logger.info("直接導入 get_pinterest_image")
    
    # 導入備用圖片服務
    try:
        from src.backup_image_service import get_backup_image, upload_image_to_imgbb
        logger.info("從 src 目錄成功導入備用圖片服務")
    except ImportError:
        from backup_image_service import get_backup_image, upload_image_to_imgbb
        logger.info("直接導入備用圖片服務")
    
    def test_pinterest_download():
        """測試 Pinterest 圖片下載"""
        logger.info("=== 測試 Pinterest 圖片下載 ===")
        local_path = get_pinterest_image()
        
        if local_path and os.path.isfile(local_path):
            logger.info(f"成功下載 Pinterest 圖片到本地: {local_path}")
            logger.info(f"檔案大小: {os.path.getsize(local_path) / 1024:.2f} KB")
            
            # 測試上傳到圖床
            logger.info("嘗試將本地圖片上傳到圖床...")
            image_url = upload_image_to_imgbb(local_path)
            
            if image_url:
                logger.info(f"成功將圖片上傳到圖床: {image_url}")
                return True
            else:
                logger.error("上傳圖片失敗")
                return False
        else:
            logger.error(f"Pinterest 圖片下載失敗或返回值不是有效的本地檔案路徑: {local_path}")
            return False

    def test_backup_image():
        """測試備用圖片服務"""
        logger.info("=== 測試備用圖片服務 ===")
        backup_image = get_backup_image()
        
        if backup_image:
            logger.info(f"成功獲取備用圖片: {backup_image}")
            return True
        else:
            logger.error("獲取備用圖片失敗")
            return False
            
    if __name__ == "__main__":
        logger.info("開始圖片測試...")
        
        # 測試 Pinterest 下載
        if test_pinterest_download():
            logger.info("Pinterest 圖片下載測試成功！")
        else:
            logger.error("Pinterest 圖片下載測試失敗！")
        
        print("\n" + "="*50 + "\n")
        
        # 測試備用圖片服務
        if test_backup_image():
            logger.info("備用圖片服務測試成功！")
        else:
            logger.error("備用圖片服務測試失敗！")
        
except ImportError as e:
    logger.error(f"導入模塊失敗: {str(e)}")
    sys.exit(1)
except Exception as e:
    logger.error(f"測試過程中發生錯誤: {str(e)}")
    sys.exit(1)
