#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/test_line_gemini_integration.py
"""
LINE Bot 與 Gemini 整合測試腳本
用於測試 LINE Bot 發送 Gemini 回應的功能
"""

import os
import sys
import logging
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    PushMessageRequest
)

# 設置 Python Path 以便能夠導入其他模組
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(current_dir)

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('line_gemini_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def test_gemini_integration():
    """測試 LINE Bot 與 Gemini 的整合"""
    logger.info("開始測試 LINE Bot 與 Gemini 的整合")
    
    try:
        # 導入 Gemini 服務
        try:
            from gemini_service import get_gemini_response
        except ImportError:
            logger.error("無法導入 Gemini 服務")
            return False
            
        # 設定 LINE Bot API
        configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
        if not configuration.access_token:
            logger.error("未設定 LINE_CHANNEL_ACCESS_TOKEN")
            return False
            
        api_client = ApiClient(configuration)
        line_bot_api = MessagingApi(api_client)
        
        LINE_USER_ID = os.getenv('LINE_USER_ID')
        if not LINE_USER_ID:
            logger.error("未設定 LINE_USER_ID")
            return False
            
        # 取得 Gemini 回應
        prompt = "請用繁體中文寫一段100字的早安問候，強調今天是測試日"
        logger.info(f"向 Gemini 發送請求: {prompt}")
        
        gemini_response = get_gemini_response(prompt)
        if not gemini_response:
            logger.error("無法獲取 Gemini 回應")
            return False
            
        logger.info(f"獲取 Gemini 回應: {gemini_response[:100]}...")
        
        # 構建測試訊息
        message = f"[Gemini AI 整合測試]\n\n{gemini_response}\n\n（這是一條自動測試訊息，請忽略）"
        
        # 發送訊息
        logger.info("發送測試訊息到 LINE...")
        line_bot_api.push_message(
            PushMessageRequest(
                to=LINE_USER_ID,
                messages=[TextMessage(text=message)]
            )
        )
        logger.info("測試訊息發送成功！")
        return True
        
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    print("開始 LINE Bot 與 Gemini 整合測試...")
    success = test_gemini_integration()
    print(f"測試結果: {'成功' if success else '失敗'}")
