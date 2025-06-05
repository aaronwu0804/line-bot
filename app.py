#!/usr/bin/env python3
"""
主要入口點 - 直接啟動LINE Webhook服務
"""

import os
import sys
import logging

print("="*80)
print("啟動 LINE Bot Webhook 服務 - 2025年6月5日更新版")
print("包含AI對話功能和對話記憶功能")
print("="*80)

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("正在從/src目錄導入LINE Webhook模組")

# 添加路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'src'))

# 載入環境變數
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("環境變數載入成功")
except Exception as e:
    logger.error(f"載入環境變數時發生錯誤: {str(e)}")

# 導入LINE Webhook應用
try:
    from src.line_webhook import app
    logger.info("成功導入LINE Webhook應用")
except ImportError:
    try:
        from line_webhook import app
        logger.info("從根目錄成功導入LINE Webhook應用")
    except ImportError as e:
        logger.critical(f"無法導入LINE Webhook應用: {str(e)}")
        logger.critical("檢查當前目錄內容:")
        import os
        logger.critical(str(os.listdir('.')))
        if os.path.exists('src'):
            logger.critical("src目錄內容:")
            logger.critical(str(os.listdir('src')))
        raise

# 讓gunicorn能夠找到應用
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"在端口 {port} 啟動應用")
    app.run(host='0.0.0.0', port=port)
