#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/keep_alive.py
"""
防止 Render 服務休眠的腳本
每 14 分鐘向 Render 服務發送一次請求
"""

import os
import time
import logging
import requests
import threading
from dotenv import load_dotenv

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keep_alive.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def keep_service_alive():
    """防止 Render 服務進入休眠狀態"""
    # 從環境變數獲取服務 URL，如果未設定則使用默認值
    service_url = os.getenv('RENDER_SERVICE_URL', 'https://your-service-name.onrender.com')
    
    if service_url == 'https://your-service-name.onrender.com':
        logger.warning("未設定 RENDER_SERVICE_URL 環境變數，請在 .env 中設定實際的 Render 服務 URL")
    
    # 健康檢查端點
    health_check_url = f"{service_url}/health"
    
    while True:
        try:
            logger.info(f"正在 ping 服務: {health_check_url}")
            response = requests.get(health_check_url, timeout=10)
            logger.info(f"收到回應: 狀態碼 {response.status_code}")
            
            # 每 14 分鐘發送一次請求（Render 免費方案在 15 分鐘無活動後會休眠）
            time.sleep(14 * 60)
        except Exception as e:
            logger.error(f"Ping 失敗: {str(e)}")
            # 如果失敗，等待 5 分鐘後重試
            time.sleep(5 * 60)

def start_keep_alive_thread():
    """在背景執行保持服務活躍的執行緒"""
    thread = threading.Thread(target=keep_service_alive)
    thread.daemon = True  # 設為守護執行緒，這樣主程式結束時，執行緒也會結束
    thread.start()
    logger.info("已啟動保持服務活躍的背景執行緒")
    return thread

if __name__ == "__main__":
    logger.info("啟動保持服務活躍的腳本...")
    keep_service_alive()  # 在主執行緒中運行，適用於單獨執行
