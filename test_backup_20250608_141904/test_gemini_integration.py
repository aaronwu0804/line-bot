#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/test_gemini_integration.py
"""
測試Gemini API整合
用於測試LINE Bot與Gemini AI的整合效果
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv

# 添加主目錄到系統路徑
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

# 載入環境變數
load_dotenv()

def test_gemini_api():
    """測試Gemini API功能"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("未找到Gemini API密鑰，請在.env文件設置GEMINI_API_KEY")
            return False
            
        # 配置API
        genai.configure(api_key=api_key)
        logger.info("Gemini API配置成功")
        
        # 創建並測試模型
        model = genai.GenerativeModel('gemini-pro')
        logger.info("Gemini模型初始化成功")
        
        # 測試問題
        test_question = "你好，今天天氣如何？"
        logger.info(f"發送測試問題: '{test_question}'")
        
        # 記錄開始時間
        start_time = time.time()
        
        # 生成回應
        response = model.generate_content(test_question)
        
        # 計算耗時
        processing_time = time.time() - start_time
        
        logger.info(f"收到回應，耗時: {processing_time:.2f}秒")
        logger.info(f"回應內容: {response.text}")
        
        return True
    except ImportError:
        logger.error("未安裝google-generativeai庫，請執行: pip install google-generativeai")
        return False
    except Exception as e:
        logger.error(f"測試Gemini API時發生錯誤: {e}")
        return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='測試Gemini API整合')
    parser.add_argument('--question', type=str, default="你好，今天天氣如何？",
                        help='測試問題')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info(f"開始測試Gemini API整合 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    success = test_gemini_api()
    
    if success:
        logger.info("=" * 60)
        logger.info("✅ Gemini API測試成功！")
        logger.info("=" * 60)
        return 0
    else:
        logger.error("=" * 60)
        logger.error("❌ Gemini API測試失敗")
        logger.error("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
