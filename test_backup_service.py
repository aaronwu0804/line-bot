#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/test_backup_service.py
"""
測試修改後的備用圖片服務
"""

import sys
import os
import logging

# 設定 Python Path 以便能夠導入其他模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 導入備用圖片服務
try:
    from src.backup_image_service import get_backup_image, get_fallback_image_url
    logger.info("成功導入備用圖片服務")
except ImportError as e:
    logger.error(f"無法導入備用圖片服務: {str(e)}")
    sys.exit(1)

def main():
    # 測試獲取備用 URL
    logger.info("測試獲取備用圖片 URL...")
    fallback_url = get_fallback_image_url()
    if fallback_url:
        logger.info(f"成功獲取備用圖片 URL: {fallback_url}")
    else:
        logger.error("無法獲取備用圖片 URL")
        return False

    # 測試完整的備用圖片服務
    logger.info("測試完整的備用圖片服務...")
    backup_image = get_backup_image()
    if backup_image:
        logger.info(f"成功獲取備用圖片: {backup_image}")
        return True
    else:
        logger.error("無法獲取備用圖片")
        return False

if __name__ == "__main__":
    if main():
        logger.info("測試成功：備用圖片服務正常工作")
        sys.exit(0)
    else:
        logger.error("測試失敗：備用圖片服務有問題")
        sys.exit(1)
