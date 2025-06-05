#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/test_line_service.py
"""
LINE Bot 服務測試工具
用於測試和診斷LINE Bot服務的問題
"""

import os
import sys
import json
import requests
import argparse
import logging
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
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def test_render_service(url=None):
    """測試Render服務是否正常運行"""
    if url is None:
        url = os.getenv('RENDER_SERVICE_URL')
        if not url:
            logger.error("未設定RENDER_SERVICE_URL環境變數，請指定服務URL")
            return False
    
    endpoints = ['/', '/health', '/callback']
    
    for endpoint in endpoints:
        full_url = f"{url.rstrip('/')}{endpoint}"
        logger.info(f"測試端點: {full_url}")
        
        try:
            if endpoint == '/callback':
                # 對於callback端點，我們只檢查是否存在，不發送POST請求
                response = requests.head(full_url, timeout=10)
                logger.info(f"HEAD {endpoint}: 狀態碼 {response.status_code}")
            else:
                response = requests.get(full_url, timeout=10)
                logger.info(f"GET {endpoint}: 狀態碼 {response.status_code}")
                
                # 如果成功，顯示回應內容片段
                if response.status_code == 200:
                    content_preview = response.text[:100] + "..." if len(response.text) > 100 else response.text
                    logger.info(f"回應內容: {content_preview}")
                else:
                    logger.warning(f"回應不成功，狀態碼: {response.status_code}")
        
        except Exception as e:
            logger.error(f"訪問 {endpoint} 時發生錯誤: {str(e)}")
    
    logger.info("檢查環境變數設定...")
    
    # 檢查必要的環境變數是否設定
    required_vars = ['LINE_CHANNEL_SECRET', 'LINE_CHANNEL_ACCESS_TOKEN', 'GEMINI_API_KEY']
    for var_name in required_vars:
        value = os.getenv(var_name)
        if value:
            # 只顯示變數值的前4個字符作為安全顯示
            preview = value[:4] + "****" if len(value) > 4 else "****"
            logger.info(f"{var_name}: 已設定 ({preview})")
        else:
            logger.error(f"{var_name}: 未設定")
    
    return True

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='測試LINE Bot服務')
    parser.add_argument('--url', type=str, help='服務URL，例如https://your-service.onrender.com')
    
    args = parser.parse_args()
    
    url = args.url
    test_render_service(url)

if __name__ == "__main__":
    main()
