#!/usr/bin/env python3
"""
Render服務外部保活腳本
可以在任何可靠的外部服務器上運行，保持Render服務持續運行
使用方法: python render_keep_alive_ext.py --url https://your-render-service.onrender.com
"""

import os
import time
import logging
import requests
import argparse
from datetime import datetime

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('render_keep_alive.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("render_keepalive")

def keep_alive(service_url, interval_minutes=10, timeout_seconds=5):
    """
    定期向Render服務發送請求以保持其活躍
    
    參數:
        service_url: Render服務URL
        interval_minutes: 請求間隔（分鐘）
        timeout_seconds: 請求超時（秒）
    """
    # 確保URL格式正確
    if not service_url.startswith(('http://', 'https://')):
        service_url = f"https://{service_url}"
    
    # 添加健康檢查路徑
    health_url = f"{service_url}/health" if not service_url.endswith('/health') else service_url
    
    logger.info(f"啟動Render服務保活 - 目標: {health_url}")
    logger.info(f"請求間隔: {interval_minutes}分鐘, 超時: {timeout_seconds}秒")
    
    ping_count = 0
    success_count = 0
    error_count = 0
    
    try:
        while True:
            ping_count += 1
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"[{current_time}] Ping #{ping_count}: {health_url}")
            
            try:
                start_time = time.time()
                response = requests.get(health_url, timeout=timeout_seconds)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    success_count += 1
                    logger.info(f"成功! 回應碼: {response.status_code}, 耗時: {duration:.2f}秒")
                    if ping_count % 10 == 0:  # 每10次顯示統計信息
                        logger.info(f"統計: 總請求 {ping_count}, 成功 {success_count}, 失敗 {error_count}")
                else:
                    error_count += 1
                    logger.warning(f"異常回應碼: {response.status_code}, 內容: {response.text[:100]}")
            
            except Exception as e:
                error_count += 1
                logger.error(f"請求失敗: {str(e)}")
                
                # 連續失敗時縮短重試間隔
                if error_count > 3 and error_count % 3 == 0:
                    logger.warning(f"檢測到連續失敗，縮短重試間隔到1分鐘")
                    time.sleep(60)
                    continue
            
            # 間隔等待
            logger.info(f"等待 {interval_minutes} 分鐘後再次發送...")
            time.sleep(interval_minutes * 60)
            
    except KeyboardInterrupt:
        logger.info("收到中斷信號，程序結束")
        logger.info(f"最終統計: 總請求 {ping_count}, 成功 {success_count}, 失敗 {error_count}")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='Render服務保活工具')
    parser.add_argument('--url', type=str, required=True, help='Render服務URL')
    parser.add_argument('--interval', type=int, default=10, help='Ping間隔（分鐘），默認10分鐘')
    parser.add_argument('--timeout', type=int, default=5, help='請求超時（秒），默認5秒')
    
    args = parser.parse_args()
    
    keep_alive(args.url, args.interval, args.timeout)

if __name__ == "__main__":
    main()
