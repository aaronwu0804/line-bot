#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/keep_render_alive.py
"""
保持 Render 服務活躍的獨立腳本
可部署在其他穩定的伺服器上，定時 ping Render 服務
"""

import os
import sys
import time
import logging
import argparse
import requests
from datetime import datetime
from dotenv import load_dotenv

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keep_render_alive.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def keep_render_alive(service_url=None, interval_minutes=14):
    """
    定期 ping Render 服務以防止進入休眠
    
    參數:
        service_url (str): Render 服務 URL，如果未提供則從環境變數獲取
        interval_minutes (int): ping 間隔（分鐘）
    """
    # 如果未提供 URL，從環境變數獲取
    if not service_url:
        service_url = os.getenv('RENDER_SERVICE_URL')
        
    if not service_url:
        logger.error("未提供 Render 服務 URL，無法繼續")
        sys.exit(1)
        
    # 添加健康檢查路徑
    if not service_url.endswith('/health'):
        health_url = f"{service_url}/health"
        if health_url.startswith('http://') or health_url.startswith('https://'):
            ping_url = health_url
        else:
            ping_url = f"https://{health_url}"
    else:
        ping_url = service_url
        
    logger.info(f"開始保持 Render 服務活躍: {ping_url}")
    logger.info(f"Ping 間隔: {interval_minutes} 分鐘")
    
    try:
        while True:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"[{current_time}] Pinging {ping_url}")
            
            try:
                start_time = time.time()
                response = requests.get(ping_url, timeout=30)
                end_time = time.time()
                
                logger.info(f"收到回應: 狀態碼 {response.status_code}, 耗時 {end_time - start_time:.2f} 秒")
                
                # 如果回應非 200 OK，記錄詳細信息
                if response.status_code != 200:
                    logger.warning(f"非預期的狀態碼: {response.status_code}")
                    logger.warning(f"回應內容: {response.text[:200]}")  # 只記錄前 200 個字符
            except requests.RequestException as e:
                logger.error(f"請求失敗: {str(e)}")
                
            # 等待指定的間隔時間
            logger.info(f"等待 {interval_minutes} 分鐘後再次 ping...")
            time.sleep(interval_minutes * 60)
    except KeyboardInterrupt:
        logger.info("接收到中斷信號，程式結束")
    except Exception as e:
        logger.error(f"發生未預期的錯誤: {str(e)}")
        return False
        
    return True

def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='保持 Render 服務活躍的工具')
    parser.add_argument('--url', help='Render 服務的 URL，如未提供則使用環境變數 RENDER_SERVICE_URL')
    parser.add_argument('--interval', type=int, default=14, help='Ping 間隔（分鐘），默認 14 分鐘')
    args = parser.parse_args()
    
    keep_render_alive(args.url, args.interval)

if __name__ == "__main__":
    main()
