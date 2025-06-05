#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/test_render_deployment.py
"""
測試 Render 部署的腳本
用於驗證 Render 部署後的功能是否正常
"""

import os
import sys
import logging
import requests
import argparse
from datetime import datetime
from dotenv import load_dotenv

# 設置系統路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('render_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def test_health_endpoint(base_url=None):
    """測試健康檢查端點"""
    if not base_url:
        base_url = os.getenv('RENDER_SERVICE_URL')
        if not base_url:
            logger.error("未提供服務 URL，無法測試")
            return False
    
    health_url = f"{base_url}/health"
    logger.info(f"測試健康檢查端點: {health_url}")
    
    try:
        response = requests.get(health_url, timeout=30)
        logger.info(f"收到回應: 狀態碼 {response.status_code}")
        logger.info(f"回應內容: {response.json()}")
        
        return response.status_code == 200
    except Exception as e:
        logger.error(f"請求健康檢查端點時發生錯誤: {str(e)}")
        return False

def test_home_endpoint(base_url=None):
    """測試首頁端點"""
    if not base_url:
        base_url = os.getenv('RENDER_SERVICE_URL')
        if not base_url:
            logger.error("未提供服務 URL，無法測試")
            return False
    
    logger.info(f"測試首頁端點: {base_url}")
    
    try:
        response = requests.get(base_url, timeout=30)
        logger.info(f"收到回應: 狀態碼 {response.status_code}")
        logger.info(f"回應內容: {response.json()}")
        
        return response.status_code == 200
    except Exception as e:
        logger.error(f"請求首頁端點時發生錯誤: {str(e)}")
        return False

def test_basic_functionality(base_url=None):
    """進行基本功能測試"""
    health_passed = test_health_endpoint(base_url)
    home_passed = test_home_endpoint(base_url)
    
    if health_passed and home_passed:
        logger.info("基本功能測試全部通過！")
        return True
    else:
        logger.error("基本功能測試有部分失敗")
        return False

def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='Render 部署測試工具')
    parser.add_argument('--url', help='Render 服務的 URL，如未提供則使用環境變數 RENDER_SERVICE_URL')
    args = parser.parse_args()
    
    logger.info(f"===== 開始測試 Render 部署 ({datetime.now()}) =====")
    
    success = test_basic_functionality(args.url)
    
    if success:
        logger.info("測試結果: 成功")
        return 0
    else:
        logger.error("測試結果: 失敗")
        return 1

if __name__ == "__main__":
    sys.exit(main())
