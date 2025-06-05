#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/quick_service_check.py
"""
快速檢查LINE Bot Webhook服務狀態
用於Render部署後的基礎功能驗證
"""

import os
import sys
import logging
import requests
import argparse
from dotenv import load_dotenv

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def check_service(url):
    """檢查服務狀態"""
    if not url:
        url = os.getenv('RENDER_SERVICE_URL')
        if not url:
            logger.error("未提供服務URL且未設定RENDER_SERVICE_URL環境變數")
            return False
            
    url = url.rstrip('/')  # 移除末尾斜線
    
    # 檢查首頁
    try:
        logger.info(f"檢查服務首頁: {url}")
        home_response = requests.get(url, timeout=10)
        logger.info(f"首頁狀態碼: {home_response.status_code}")
        if home_response.status_code == 200:
            logger.info("✅ 首頁可訪問")
            # 顯示回應內容的前200字符
            content = home_response.text[:200].replace('\n', ' ')
            logger.info(f"首頁內容片段: {content}...")
        else:
            logger.error(f"❌ 首頁返回錯誤狀態碼: {home_response.status_code}")
            logger.error(f"錯誤回應: {home_response.text[:100]}...")
    except Exception as e:
        logger.error(f"❌ 無法訪問首頁: {str(e)}")
        
    # 檢查健康檢查端點
    try:
        health_url = f"{url}/health"
        logger.info(f"檢查健康檢查端點: {health_url}")
        health_response = requests.get(health_url, timeout=10)
        logger.info(f"健康檢查狀態碼: {health_response.status_code}")
        if health_response.status_code == 200:
            logger.info("✅ 健康檢查端點正常")
            logger.info(f"健康檢查回應: {health_response.text}")
            
            # 嘗試解析JSON回應
            try:
                health_data = health_response.json()
                if health_data.get('status') == 'ok':
                    logger.info("✅ 健康狀態報告正常")
                else:
                    logger.warning(f"⚠️ 健康狀態異常: {health_data}")
            except:
                logger.warning("⚠️ 無法解析健康檢查回應為JSON")
        else:
            logger.error(f"❌ 健康檢查返回錯誤: {health_response.status_code}")
    except Exception as e:
        logger.error(f"❌ 無法訪問健康檢查端點: {str(e)}")
    
    # 檢查callback端點
    try:
        callback_url = f"{url}/callback"
        logger.info(f"檢查callback端點: {callback_url}")
        # 只發送GET請求查看回應，不進行實際webhook測試
        callback_response = requests.get(callback_url, timeout=10)
        logger.info(f"Callback端點狀態碼: {callback_response.status_code}")
        if callback_response.status_code in [200, 405]:
            # 405是正常的，因為callback通常只接受POST
            logger.info("✅ Callback端點可訪問")
        else:
            logger.warning(f"⚠️ Callback端點返回意外狀態: {callback_response.status_code}")
    except Exception as e:
        logger.error(f"❌ 無法訪問Callback端點: {str(e)}")
    
    # 整體總結
    logger.info("======= 服務檢查結束 =======")
    logger.info("要進行完整的webhook測試，請運行:")
    logger.info(f"python src/line_webhook_test.py --url {url}/callback --text \"AI: 測試訊息\"")
    
    return True

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='檢查LINE Bot Webhook服務狀態')
    parser.add_argument('--url', type=str, help='服務URL，例如https://your-service.onrender.com')
    
    args = parser.parse_args()
    check_service(args.url)

if __name__ == "__main__":
    main()
