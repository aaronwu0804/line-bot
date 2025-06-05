#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/start_webhook.py
"""
LINE Bot Webhook 服務啟動腳本
用於啟動 LINE Bot 的 Webhook 服務，接收用戶消息並處理 Gemini AI 對話功能
"""

import os
import sys
import logging
import signal
import argparse
from dotenv import load_dotenv

# 設定 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'src'))

# 設定日誌
log_path = os.path.join(current_dir, 'logs', 'webhook_service.log')
# 確保 logs 資料夾存在
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def check_environment_variables():
    """檢查必要的環境變數是否已設定"""
    required_vars = [
        'LINE_CHANNEL_ACCESS_TOKEN',
        'LINE_CHANNEL_SECRET',
        'GEMINI_API_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"缺少以下環境變數: {', '.join(missing_vars)}")
        return False
    
    return True

def test_gemini_api():
    """測試 Gemini API 連接"""
    try:
        from src.gemini_service import test_gemini_api
    except ImportError:
        from gemini_service import test_gemini_api
    
    logger.info("測試 Gemini API 連接...")
    return test_gemini_api()

def signal_handler(sig, frame):
    """處理終止信號"""
    logger.info("接收到終止信號，正在關閉服務...")
    sys.exit(0)

def start_webhook_service(port=5000, debug=False):
    """啟動 Webhook 服務"""
    logger.info(f"正在啟動 LINE Bot Webhook 服務，監聽端口: {port}...")
    
    # 檢查環境變數
    if not check_environment_variables():
        logger.error("環境變數檢查失敗，無法啟動服務")
        return False
    
    # 注意：由於 Gemini API 配額限制，我們暫時跳過 API 測試
    # gemini_test_result = test_gemini_api()
    # logger.info(f"Gemini API 測試結果: {gemini_test_result}")
    logger.info(f"由於 Gemini API 配額限制，跳過 API 測試")
    
    try:
        # 導入 Webhook 模組
        try:
            from src.line_webhook import app
        except ImportError:
            from line_webhook import app
        
        # 註冊信號處理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 啟動 Flask 服務
        app.run(host='0.0.0.0', port=port, debug=debug)
        return True
    except Exception as e:
        logger.error(f"啟動 Webhook 服務時發生錯誤: {str(e)}")
        logger.exception("詳細錯誤:")
        return False

def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='LINE Bot Webhook 服務啟動工具')
    parser.add_argument('--port', type=int, default=5000, help='服務監聽端口 (預設: 5000)')
    parser.add_argument('--debug', action='store_true', help='啟用 Flask 除錯模式')
    parser.add_argument('--test-api', action='store_true', help='僅測試 Gemini API 連接')
    args = parser.parse_args()
    
    if args.test_api:
        result = test_gemini_api()
        print(f"Gemini API 測試結果: {result}")
        return
    
    start_webhook_service(port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()
