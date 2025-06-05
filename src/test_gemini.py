#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/test_gemini.py
"""
Gemini API 測試腳本
測試 Google Gemini API 連接和回應功能
"""

import os
import logging
from dotenv import load_dotenv

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gemini_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def run_gemini_test():
    """測試 Gemini API 連線和基本功能"""
    logger.info("開始測試 Gemini API...")
    
    try:
        # 導入 Gemini 服務
        from gemini_service import get_gemini_response, test_gemini_api
        
        # 測試 API 連接
        connection_result = test_gemini_api()
        logger.info(f"API 連接測試結果: {connection_result}")
        
        # 測試基本問答
        questions = [
            "用繁體中文告訴我今天的日期是什麼?",
            "什麼是人工智能?",
            "推薦五本經典科幻小說",
            "寫一首關於早晨的短詩"
        ]
        
        for i, question in enumerate(questions):
            logger.info(f"測試問題 {i+1}: {question}")
            try:
                response = get_gemini_response(question)
                logger.info(f"回應: {response[:100]}..." if len(response) > 100 else f"回應: {response}")
            except Exception as e:
                logger.error(f"回答問題時發生錯誤: {str(e)}")
        
        # 測試對話上下文功能
        logger.info("測試對話上下文功能...")
        try:
            # 模擬一個簡短的對話歷史
            conversation_history = [
                {"role": "user", "parts": ["我叫小明"]},
                {"role": "model", "parts": ["你好，小明！很高興認識你。有什麼我可以幫助你的嗎？"]}
            ]
            
            # 發送後續問題，應該能記住用戶名字
            follow_up = "你還記得我的名字嗎？"
            logger.info(f"後續問題: {follow_up}")
            response = get_gemini_response(follow_up, conversation_history)
            logger.info(f"回應: {response}")
            
            return True
        except Exception as e:
            logger.error(f"測試對話上下文時發生錯誤: {str(e)}")
            return False
        
    except ImportError as e:
        logger.error(f"導入 Gemini 服務失敗: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    print("開始 Gemini API 測試...")
    result = run_gemini_test()
    print(f"測試結果: {'成功' if result else '失敗'}")
