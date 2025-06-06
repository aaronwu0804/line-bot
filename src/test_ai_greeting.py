#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/test_ai_greeting.py
"""
測試 Gemini API 智能問候語生成
用於驗證 Gemini API 集成與智能問候語生成
"""

import os
import sys
import time
import logging
from datetime import datetime

# 設定 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def test_ai_greeting():
    """測試 Gemini API 智能問候語生成"""
    print("=" * 60)
    print(f"Gemini API 智能問候語測試 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 檢查環境變數
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_KEY')
    if not gemini_key:
        logger.error("未設定 Gemini API 密鑰，無法執行測試")
        return False
        
    logger.info("已檢測到 Gemini API 密鑰")
    
    # 測試導入 main 模組
    try:
        from src.main import generate_ai_greeting
        logger.info("成功導入 generate_ai_greeting 函數")
    except ImportError:
        try:
            from main import generate_ai_greeting
            logger.info("成功導入 generate_ai_greeting 函數 (從當前目錄)")
        except ImportError:
            logger.error("無法導入 generate_ai_greeting 函數，請確認 main.py 中已添加此函數")
            return False
    
    # 測試生成問候語
    try:
        logger.info("測試無天氣資訊的問候語生成...")
        greeting1 = generate_ai_greeting()
        if greeting1:
            logger.info(f"成功生成問候語: {greeting1}")
        else:
            logger.warning("未能生成問候語，將使用備用問候語")
        
        # 測試帶天氣資訊的問候語
        logger.info("測試帶天氣資訊的問候語生成...")
        weather_info = {
            'weather': '晴時多雲',
            'temp': '28',
            'rain_prob': '20',
            'humidity': '75%',
            'comfort': '舒適',
            'min_temp': '25',
            'max_temp': '30',
            'district': '桃園市',
            'description': '今天天氣晴朗，適合戶外活動。'
        }
        
        greeting2 = generate_ai_greeting(weather_info)
        if greeting2:
            logger.info(f"成功生成天氣問候語: {greeting2}")
        else:
            logger.warning("未能生成天氣問候語，將使用備用問候語")
        
        return greeting1 or greeting2
            
    except Exception as e:
        logger.error(f"測試時發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    if test_ai_greeting():
        print("\n✓ 測試成功: Gemini API 智能問候語生成功能正常")
        sys.exit(0)
    else:
        print("\n✗ 測試失敗: Gemini API 智能問候語生成出現問題")
        sys.exit(1)
