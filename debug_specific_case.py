#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
特殊案例調試
==========

調試帶點號和空格前導字符的關鍵字檢測
"""

import logging
import sys

# 配置日誌
logging.basicConfig(level=logging.INFO, 
                    format='%(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger()

def debug_specific_case():
    """專門測試帶點號和空格前導字符的案例"""
    message = ". 小幫手幫我"
    logger.info(f"測試特殊案例: '{message}'")
    
    # 去除前後空格
    trimmed_message = message.strip()
    logger.info(f"去除前後空格: '{trimmed_message}'")
    
    # 檢查長度
    logger.info(f"長度: {len(trimmed_message)}")
    
    # 檢查第一個字符
    first_char = trimmed_message[0]
    logger.info(f"第一個字符: '{first_char}'")
    
    # 允許的前導字符列表
    allowed_prefixes = ['!', '！', ',', '，', '。', '.', '?', '？', ' ', '　', ':', '：', '@', '#', '$', '%', '、', '~', '～']
    logger.info(f"第一個字符在允許列表中: {first_char in allowed_prefixes}")
    
    # 檢查第二個字符是否為空格
    if len(trimmed_message) > 1:
        second_char = trimmed_message[1]
        logger.info(f"第二個字符: '{second_char}'")
        logger.info(f"第二個字符是空格: {second_char == ' '}")
        
        # 檢查條件
        condition1 = len(trimmed_message) > 2
        condition2 = first_char in allowed_prefixes
        condition3 = trimmed_message[1] == ' '
        
        logger.info(f"條件檢查:")
        logger.info(f"- 長度 > 2: {condition1}")
        logger.info(f"- 第一個字符在允許列表: {condition2}")
        logger.info(f"- 第二個字符是空格: {condition3}")
        logger.info(f"- 所有條件都滿足: {condition1 and condition2 and condition3}")
        
        # 檢查後續字符
        if condition1 and condition2 and condition3:
            rest = trimmed_message[2:]
            logger.info(f"空格後剩餘部分: '{rest}'")
            
            keyword = '小幫手'
            starts_with_keyword = rest.startswith(keyword)
            logger.info(f"剩餘部分是否以 '{keyword}' 開頭: {starts_with_keyword}")

if __name__ == "__main__":
    print("="*60)
    print("特殊案例調試: 帶點號和空格前導字符的關鍵字檢測")
    print("="*60)
    debug_specific_case()
