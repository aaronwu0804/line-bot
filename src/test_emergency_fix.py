#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/test_emergency_fix.py
"""
測試緊急修復版的LINE Bot部署
"""

import os
import sys
import logging
import argparse
import requests
import time
from datetime import datetime

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def test_service_endpoints(base_url, max_retries=3, retry_delay=10):
    """測試服務的各個端點"""
    success = False
    
    for attempt in range(1, max_retries + 1):
        logger.info(f"嘗試 #{attempt}: 測試服務端點...")
        endpoints_status = {
            "home": False,
            "health": False,
            "callback": False
        }
        
        # 測試主頁
        try:
            logger.info(f"測試主頁: {base_url}")
            home_response = requests.get(base_url, timeout=15)
            logger.info(f"主頁狀態碼: {home_response.status_code}")
            if home_response.status_code == 200:
                logger.info("✅ 主頁正常")
                endpoints_status["home"] = True
                logger.info(f"回應內容前100字符: {home_response.text[:100]}")
            else:
                logger.error(f"❌ 主頁返回錯誤: {home_response.status_code}")
        except Exception as e:
            logger.error(f"❌ 訪問主頁時出錯: {str(e)}")
        
        # 測試健康檢查
        try:
            health_url = f"{base_url}/health"
            logger.info(f"測試健康檢查: {health_url}")
            health_response = requests.get(health_url, timeout=15)
            logger.info(f"健康檢查狀態碼: {health_response.status_code}")
            if health_response.status_code == 200:
                logger.info("✅ 健康檢查正常")
                endpoints_status["health"] = True
                logger.info(f"健康檢查回應: {health_response.text}")
            else:
                logger.error(f"❌ 健康檢查返回錯誤: {health_response.status_code}")
        except Exception as e:
            logger.error(f"❌ 訪問健康檢查時出錯: {str(e)}")
        
        # 簡單測試callback端點
        try:
            callback_url = f"{base_url}/callback"
            logger.info(f"測試callback端點: {callback_url}")
            # 簡單的GET請求測試端點是否存在
            callback_response = requests.get(callback_url, timeout=15)
            logger.info(f"Callback端點狀態碼: {callback_response.status_code}")
            if callback_response.status_code in [200, 405, 400]:
                # 405是正常的(方法不允許)，因為callback通常只接受POST
                # 400是正常的(請求無效)，因為缺少簽名
                logger.info("✅ Callback端點可訪問")
                endpoints_status["callback"] = True
            else:
                logger.error(f"❌ Callback端點返回意外狀態: {callback_response.status_code}")
        except Exception as e:
            logger.error(f"❌ 訪問Callback端點時出錯: {str(e)}")
        
        # 檢查是否所有端點都可訪問
        if all(endpoints_status.values()):
            logger.info("✅ 所有端點測試通過！")
            success = True
            break
        else:
            logger.warning("⚠️ 部分端點測試失敗")
            failed_endpoints = [ep for ep, status in endpoints_status.items() if not status]
            logger.warning(f"失敗的端點: {', '.join(failed_endpoints)}")
            
            if attempt < max_retries:
                logger.info(f"等待 {retry_delay} 秒後重試...")
                time.sleep(retry_delay)
    
    return success

def main():
    parser = argparse.ArgumentParser(description="測試緊急修復版LINE Bot部署")
    parser.add_argument("--url", type=str, default="https://line-bot-webhook.onrender.com",
                        help="要測試的服務URL")
    parser.add_argument("--retries", type=int, default=3,
                        help="最大重試次數")
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info(f"開始測試緊急修復版LINE Bot部署: {args.url}")
    logger.info(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    success = test_service_endpoints(args.url, max_retries=args.retries)
    
    if success:
        logger.info("=" * 60)
        logger.info("✅ 所有端點測試成功！服務運行正常")
        logger.info("=" * 60)
        # 提示運行完整webhook測試
        logger.info("要進行完整webhook測試，請運行:")
        logger.info(f"python src/line_webhook_test.py --url {args.url}/callback --text \"AI: 測試訊息\"")
        return 0
    else:
        logger.error("=" * 60)
        logger.error("❌ 服務端點測試失敗")
        logger.error("請檢查Render部署日誌以獲取更多信息")
        logger.error("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
