#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/image_cleaner.py
"""
圖片自動清理工具
定期清理 images 目錄中的舊圖片，以避免佔用過多空間
"""

import os
import glob
import logging
import time
from datetime import datetime, timedelta

# 設定日誌
logger = logging.getLogger(__name__)

class ImageCleaner:
    """圖片清理工具類"""
    
    def __init__(self, images_dir=None, max_age_days=7):
        """
        初始化清理工具
        
        參數:
            images_dir: 圖片目錄，預設為專案下的 images 目錄
            max_age_days: 圖片保存的最大天數，超過這個天數的圖片將被刪除，預設 7 天
        """
        if images_dir is None:
            # 取得專案根目錄
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.images_dir = os.path.join(base_dir, 'images')
        else:
            self.images_dir = images_dir
            
        self.max_age_days = max_age_days
        
    def clean(self):
        """清理舊圖片"""
        if not os.path.exists(self.images_dir):
            logger.warning(f"圖片目錄不存在: {self.images_dir}")
            return 0
            
        # 計算截止日期
        cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
        cutoff_timestamp = cutoff_date.timestamp()
        
        # 獲取所有圖片文件
        image_files = glob.glob(os.path.join(self.images_dir, '*.png')) + glob.glob(os.path.join(self.images_dir, '*.jpg'))
        
        # 初始化計數器
        deleted_count = 0
        kept_count = 0
        error_count = 0
        
        # 處理每個文件
        for image_path in image_files:
            try:
                # 跳過 .gitkeep 文件
                if os.path.basename(image_path) == '.gitkeep':
                    continue
                    
                # 獲取文件修改時間
                mod_time = os.path.getmtime(image_path)
                
                # 如果文件早於截止日期，則刪除
                if mod_time < cutoff_timestamp:
                    os.remove(image_path)
                    logger.info(f"已刪除舊圖片: {os.path.basename(image_path)}")
                    deleted_count += 1
                else:
                    kept_count += 1
            except Exception as e:
                logger.error(f"刪除圖片 {image_path} 時出錯: {str(e)}")
                error_count += 1
                
        logger.info(f"圖片清理完成: 已刪除 {deleted_count} 張，保留 {kept_count} 張，錯誤 {error_count} 張")
        return deleted_count
        
# 全局實例，方便其他模塊直接調用
image_cleaner = ImageCleaner()

def clean_old_images(max_age_days=7):
    """清理超過指定天數的舊圖片"""
    cleaner = ImageCleaner(max_age_days=max_age_days)
    return cleaner.clean()

if __name__ == "__main__":
    # 設定日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 執行清理
    logger.info("開始清理舊圖片...")
    deleted = clean_old_images()
    logger.info(f"清理完成，共刪除 {deleted} 張圖片")
