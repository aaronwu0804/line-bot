#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/render_app.py
"""
Render 部署專用入口點
將 Flask 應用程式從 line_webhook.py 中導入
包含自動防止服務休眠的功能
"""

import os
import sys
import logging
import threading
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# 設定 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'src'))

# 設定日誌
log_path = os.path.join(current_dir, 'logs', 'render_webhook.log')
# 確保 logs 資料夾存在
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

# 導入 LINE Webhook 應用
try:
    from src.line_webhook import app
except ImportError:
    try:
        from line_webhook import app
    except ImportError:
        logger.critical("無法導入 LINE Webhook 應用，請確認 line_webhook.py 存在")
        raise

# 防止服務休眠的線程
def keep_alive():
    """防止 Render 服務休眠的背景線程"""
    service_url = os.getenv('RENDER_SERVICE_URL')
    if not service_url:
        logger.warning("未設定 RENDER_SERVICE_URL 環境變數，無法啟動防休眠功能")
        return
        
    ping_url = f"{service_url}/health"
    
    logger.info(f"啟動防休眠線程，每 14 分鐘 ping 一次: {ping_url}")
    
    while True:
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"[{current_time}] 自我 ping 以保持活躍")
            
            response = requests.get(ping_url, timeout=10)
            logger.info(f"自我 ping 回應: {response.status_code}")
            
            # 等待 14 分鐘
            time.sleep(14 * 60)
        except Exception as e:
            logger.error(f"自我 ping 失敗: {str(e)}")
            # 如果失敗，等待 5 分鐘後重試
            time.sleep(5 * 60)

# 啟動防休眠線程
def start_keep_alive_thread():
    """啟動防休眠線程"""
    if os.getenv('RENDER_SERVICE_URL'):
        thread = threading.Thread(target=keep_alive)
        thread.daemon = True
        thread.start()
        logger.info("防休眠線程已啟動")
    else:
        logger.info("未設定 RENDER_SERVICE_URL，跳過啟動防休眠線程")

# 在生產環境中自動啟動防休眠功能
if os.getenv('RENDER'):
    logger.info("檢測到 Render 環境，自動啟動防休眠功能")
    start_keep_alive_thread()

# 讓 gunicorn 能找到應用
application = app

if __name__ == "__main__":
    # 設定 PORT 環境變數，默認 10000
    port = int(os.environ.get('PORT', 10000))
    
    # 在本地運行時也啟動防休眠線程
    start_keep_alive_thread()
    
    # 啟動應用
    app.run(host='0.0.0.0', port=port)
