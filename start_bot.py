#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/start_bot.py
"""
早安貼文機器人啟動腳本
可用於手動測試或部署在服務器上
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime

# 設定 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 設定日誌
log_path = os.path.join(current_dir, 'logs', 'morning_bot.log')
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

def run_test_message():
    """執行測試訊息發送"""
    logger.info("執行測試訊息發送...")
    try:
        # 添加src目錄到路徑
        sys.path.append(os.path.join(current_dir, 'src'))
        
        # 優先使用增強版的測試腳本
        try:
            from src.test_image_message_fix import send_test_image_message
            logger.info("使用增強版圖片測試腳本")
            result = send_test_image_message()
        except ImportError as e:
            logger.warning(f"無法導入增強版測試腳本: {str(e)}")
            # 嘗試從 src 目錄直接導入
            try:
                from test_image_message_fix import send_test_image_message
                logger.info("從當前目錄使用增強版圖片測試腳本")
                result = send_test_image_message()
            except ImportError:
                # 如果找不到增強版，則使用原始版本
                try:
                    from src.test_weather_message import send_test_message
                    logger.info("使用原始版測試腳本 (從src導入)")
                    result = send_test_message()
                except ImportError:
                    from test_weather_message import send_test_message
                    logger.info("使用原始版測試腳本")
                    result = send_test_message()
            
        logger.info(f"測試訊息發送結果: {'成功' if result else '失敗'}")
    except Exception as e:
        logger.error(f"執行測試訊息時發生錯誤: {str(e)}")
        logger.exception("詳細錯誤:")

def run_diagnostics():
    """執行網路診斷"""
    logger.info("執行網路診斷...")
    try:
        try:
            from src.dns_fix_helper import main as run_dns_fix
        except ImportError:
            from dns_fix_helper import main as run_dns_fix
        run_dns_fix()
    except ImportError:
        logger.error("無法導入 dns_fix_helper 模組，請確認是否已安裝相依套件")
        logger.info("請先執行: pip install dnspython")
    except Exception as e:
        logger.error(f"執行網路診斷時發生錯誤: {str(e)}")

def start_bot(test_only=False):
    """啟動機器人"""
    logger.info(f"===== 啟動早安貼文機器人 v2.1.0 ({datetime.now()}) =====")
    logger.info("已整合 Gemini AI 智能問候功能！")
    
    # 檢查環境變數
    gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_KEY')
    if gemini_key:
        logger.info("已檢測到 Gemini API 密鑰，將啟用智能問候功能")
    else:
        logger.info("未設定 Gemini API 密鑰，將使用預設問候語")
    
    if test_only:
        logger.info("僅執行測試模式...")
        run_test_message()
        return
    
    try:
        try:
            from src.main import main, send_morning_message
        except ImportError:
            from main import main, send_morning_message
        
        # 先發送一次測試訊息
        logger.info("發送初始測試訊息...")
        send_morning_message()
        
        # 啟動排程
        logger.info("啟動排程任務...")
        main()
    except KeyboardInterrupt:
        logger.info("使用者中斷，程式結束")
    except Exception as e:
        logger.error(f"啟動機器人時發生錯誤: {str(e)}")
        logger.exception("詳細錯誤:")

def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='早安貼文機器人啟動工具')
    parser.add_argument('--test', action='store_true', help='僅執行測試訊息，不啟動完整排程')
    parser.add_argument('--diagnostics', action='store_true', help='執行網路診斷')
    args = parser.parse_args()
    
    if args.diagnostics:
        run_diagnostics()
        return
    
    start_bot(test_only=args.test)

if __name__ == "__main__":
    main()
