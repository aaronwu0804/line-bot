#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
專門針對點號和空格問題的測試腳本
"""

import logging
import sys

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger()

def is_ai_request_test(message):
    """檢查是否為 AI 請求 (專門處理點號和空格的問題)"""
    if not message:
        return False
    
    # 打印診斷訊息
    logger.info(f"檢測訊息: '{message}'")
    
    # 去除前後空格
    trimmed_message = message.strip()
    logger.info(f"去除空格後: '{trimmed_message}'")
    
    # 檢查點號+空格開頭
    if len(trimmed_message) >= 3 and trimmed_message[0] == '.' and trimmed_message[1] == ' ':
        keyword = '小幫手'
        if trimmed_message[2:].startswith(keyword):
            logger.info(f"檢測到點號+空格+關鍵字: '{keyword}'")
            return True
            
    # 其他情況
    logger.info("未檢測到點號+空格+關鍵字格式")
    return False

def run_test():
    """運行測試"""
    print("="*60)
    print("專門測試點號和空格的關鍵字檢測")
    print("="*60)
    
    test_cases = [
        ". 小幫手你好",   # 點號+空格+關鍵字 (應該通過)
        ".小幫手你好",    # 點號+關鍵字，無空格 (應該失敗)
        " . 小幫手你好",  # 空格+點號+空格+關鍵字 (應該通過，因為會去除前後空格)
    ]
    
    for case in test_cases:
        result = is_ai_request_test(case)
        print(f"測試: '{case}' -> 結果: {result}")
    
if __name__ == "__main__":
    run_test()
