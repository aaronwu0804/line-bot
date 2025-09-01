#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/clean_images.py
"""
獨立的圖片清理工具
可以直接執行或通過系統排程定期執行
使用方法: python clean_images.py [天數]
預設清理 7 天前的圖片
"""

import sys
import logging
import os

# 設定日誌
log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'image_cleaner.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """主程式"""
    try:
        # 導入圖片清理功能
        try:
            from src.image_cleaner import clean_old_images
            logger.info("從 src 導入圖片清理模組")
        except ImportError:
            from image_cleaner import clean_old_images
            logger.info("導入圖片清理模組")
        
        # 處理命令行參數
        max_age_days = 7  # 預設 7 天
        if len(sys.argv) > 1:
            try:
                max_age_days = int(sys.argv[1])
                logger.info(f"使用指定的天數參數: {max_age_days} 天")
            except ValueError:
                logger.warning(f"無效的天數參數: {sys.argv[1]}，使用預設值 7 天")
        
        # 執行清理
        logger.info(f"開始清理超過 {max_age_days} 天的舊圖片...")
        deleted = clean_old_images(max_age_days=max_age_days)
        logger.info(f"圖片清理完成: 已刪除 {deleted} 張超過 {max_age_days} 天的舊圖片")
        
        return 0  # 成功執行
    except Exception as e:
        logger.error(f"圖片清理時發生錯誤: {str(e)}")
        return 1  # 執行失敗

if __name__ == "__main__":
    print(f"圖片清理工具 v1.0.0")
    print("=============================")
    sys.exit(main())  # 返回執行狀態碼
