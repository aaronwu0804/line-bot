#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/test_unsplash_urls.py
"""
測試 Unsplash 圖片 URL 是否可訪問
"""

import os
import sys
import requests
import logging
from datetime import datetime

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 確保能夠導入其他模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 從 test_pinterest.py 中導入圖片 URL 函數
try:
    from src.test_pinterest import get_direct_image
    logger.info("成功從 src 目錄導入 get_direct_image 函數")
except ImportError:
    try:
        from test_pinterest import get_direct_image
        logger.info("成功直接導入 get_direct_image 函數")
    except ImportError:
        logger.error("無法導入 get_direct_image 函數")
        sys.exit(1)

# 從 backup_image_service.py 中導入備用圖片 URL 函數
try:
    from src.backup_image_service import get_fallback_image_url
    logger.info("成功從 src 目錄導入 get_fallback_image_url 函數")
except ImportError:
    try:
        from backup_image_service import get_fallback_image_url
        logger.info("成功直接導入 get_fallback_image_url 函數")
    except ImportError:
        logger.error("無法導入 get_fallback_image_url 函數")
        sys.exit(1)

def test_image_url(url):
    """測試圖片 URL 是否可訪問"""
    try:
        logger.info(f"測試圖片 URL: {url}")
        response = requests.head(url, timeout=10)
        logger.info(f"狀態碼: {response.status_code}")
        if response.status_code == 200:
            return True
        else:
            logger.warning(f"URL 無法訪問: {url}")
            return False
    except Exception as e:
        logger.error(f"測試圖片 URL 時發生錯誤: {str(e)}")
        return False

def print_all_direct_image_urls():
    """直接顯示所有 get_direct_image 函數中的 URL"""
    try:
        # 從 test_pinterest.py 的代碼中獲取 URL 列表
        import inspect
        source = inspect.getsource(get_direct_image)
        logger.info("get_direct_image 函數源代碼:")
        print("-" * 80)
        print(source)
        print("-" * 80)
    except Exception as e:
        logger.error(f"獲取函數源代碼時發生錯誤: {str(e)}")

if __name__ == "__main__":
    logger.info("===== 開始測試圖片 URL =====")
    
    # 測試 get_direct_image 函數返回的 URL
    logger.info("測試 get_direct_image 函數")
    direct_url = get_direct_image()
    logger.info(f"get_direct_image 返回的 URL: {direct_url}")
    test_image_url(direct_url)
    
    # 測試 get_fallback_image_url 函數返回的 URL
    logger.info("測試 get_fallback_image_url 函數")
    fallback_url = get_fallback_image_url()
    logger.info(f"get_fallback_image_url 返回的 URL: {fallback_url}")
    test_image_url(fallback_url)
    
    # 顯示所有 URL
    logger.info("顯示 get_direct_image 函數中的所有 URL")
    print_all_direct_image_urls()
    
    logger.info("===== 測試完成 =====")
