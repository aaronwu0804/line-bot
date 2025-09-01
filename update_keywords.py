#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LINE Bot 關鍵字位置檢測更新工具
================================================

此工具用於更新 app.py 和 line_webhook.py 中的 is_ai_request 函數，
確保只有訊息開頭或帶有允許前導字符的關鍵字才會觸發AI回應。
"""

import os
import sys
import re
import logging
from datetime import datetime

# 配置日誌
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"keyword_update_{datetime.now().strftime('%Y%m%d%H%M%S')}.log")

# 配置 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("keyword_update")

def update_app_py():
    """更新 app.py 中的 is_ai_request 函數"""
    app_file = "/Users/al02451008/Documents/code/morning-post/app.py"
    
    # 讀取文件內容
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 備份原文件
    backup_file = f"{app_file}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"已備份 app.py 至 {backup_file}")
    
    # 更新 is_ai_request 函數
    new_function = """def is_ai_request(message):
    """檢查是否為AI請求 (最終版: 僅檢測訊息開頭或帶允許前導字符的關鍵字)"""
    if not message:
        return False
    
    # 添加日誌以查看接收到的確切訊息
    logger.info(f"檢測訊息是否為AI請求: '{message}'")
    
    # 嘗試處理可能的特殊字符或編碼問題
    normalized_message = message
    try:
        # 先嘗試規範化字符
        import unicodedata
        normalized_message = unicodedata.normalize('NFKC', message)
        if normalized_message != message:
            logger.info(f"已規範化訊息: '{normalized_message}'")
    except Exception as e:
        logger.error(f"規範化訊息時出錯: {str(e)}")
    
    # 去除前後空格，便於檢查句首關鍵字
    trimmed_message = normalized_message.strip()
    message_lower = trimmed_message.lower()
    
    # 1. 檢查常見的AI前綴 (必須在句首)
    if (message_lower.startswith(('ai:', 'ai：')) or 
        message_lower.startswith(('@ai', '@ai ')) or
        message_lower.startswith('ai ') or 
        message_lower == 'ai'):
        logger.info("識別為AI請求: 前綴匹配")
        return True
    
    # 2. 檢查中文關鍵字是否在句首或帶有允許的前導字符
    keywords = ['小幫手', '花生']
    
    # 允許的前導字符列表
    allowed_prefixes = ['!', '！', ',', '，', '。', '.', '?', '？', ' ', '　', ':', '：', '@', '#', '$', '%', '、', '~', '～']
    
    for keyword in keywords:
        # 檢查關鍵字是否在句首
        if trimmed_message.startswith(keyword):
            logger.info(f"識別為AI請求: 檢測到句首關鍵字 '{keyword}'")
            return True
        
        # 檢查是否有允許的前導字符後接關鍵字
        if len(trimmed_message) > 1:
            # 處理只有一個前導字符的情況
            first_char = trimmed_message[0]
            if first_char in allowed_prefixes and trimmed_message[1:].startswith(keyword):
                logger.info(f"識別為AI請求: 檢測到帶前導字符的關鍵字 '{keyword}', 前導字符: '{first_char}'")
                return True
            
            # 處理有前導字符和空格的情況 (如 ". 小幫手")
            if len(trimmed_message) > 2 and first_char in allowed_prefixes and trimmed_message[1] == ' ':
                if trimmed_message[2:].startswith(keyword):
                    logger.info(f"識別為AI請求: 檢測到帶前導字符和空格的關鍵字 '{keyword}', 前導字符: '{first_char} '")
                    return True
    
    # 3. 特殊處理「花生」(字符級別)
    flower_char = '花'
    life_char = '生'
    
    # 直接在句首的「花生」
    if trimmed_message.startswith(flower_char) and len(trimmed_message) > 1:
        if trimmed_message[1] == life_char:
            logger.info(f"識別為AI請求: 通過字符級別檢測到句首 '花生' 關鍵字")
            return True
    
    # 允許的前導字符後的「花生」
    if len(trimmed_message) > 2 and trimmed_message[0] in allowed_prefixes:
        # 一個前導字符的情況
        if trimmed_message[1] == flower_char and trimmed_message[2] == life_char:
            logger.info(f"識別為AI請求: 通過字符級別檢測到帶前導字符的 '花生' 關鍵字")
            return True
        
        # 前導字符+空格的情況
        elif trimmed_message[1] == ' ' and len(trimmed_message) > 3:
            if trimmed_message[2] == flower_char and trimmed_message[3] == life_char:
                logger.info(f"識別為AI請求: 通過字符級別檢測到帶前導字符和空格的 '花生' 關鍵字")
                return True
    
    # 所有檢查都未通過
    logger.info("非AI請求: 未檢測到句首或帶允許前導字符的觸發關鍵字")
    return False"""
    
    # 尋找原始的 is_ai_request 函數
    pattern = r'def is_ai_request\(message\):.*?return False'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        logger.error("無法在 app.py 中找到 is_ai_request 函數")
        return False
    
    # 替換函數
    updated_content = content.replace(match.group(0), new_function)
    
    # 寫入修改後的內容
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    logger.info("已更新 app.py 中的 is_ai_request 函數")
    return True

def update_extract_query():
    """更新 line_webhook.py 中的 extract_query 函數"""
    webhook_file = "/Users/al02451008/Documents/code/morning-post/src/line_webhook.py"
    
    # 讀取文件內容
    with open(webhook_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 備份原文件
    backup_file = f"{webhook_file}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"已備份 line_webhook.py 至 {backup_file}")
    
    # 更新 extract_query 函數
    new_function = """def extract_query(message):
    """從訊息中提取實際查詢內容 (最終版: 適配句首關鍵字檢測)"""
    message = message.strip()
    
    # 1. 處理明確的前綴
    if message.lower().startswith('ai:'):
        return message[3:].strip()
    elif message.lower().startswith('ai：'):  # 中文冒號
        return message[3:].strip()
    elif message.lower().startswith('@ai'):
        return message[3:].strip()
    elif message.lower().startswith('ai '):
        return message[3:].strip()
    
    # 2. 處理「小幫手」和「花生」關鍵字 (只考慮句首或帶允許的前導字符)
    keywords = ['小幫手', '花生']
    allowed_prefixes = ['!', '！', ',', '，', '。', '.', '?', '？', ' ', '　', ':', '：', '@', '#', '$', '%', '、', '~', '～']
    
    for keyword in keywords:
        # 如果關鍵字在開頭，移除它
        if message.startswith(keyword):
            return message[len(keyword):].strip()
        
        # 處理有前導字符的情況
        if len(message) > 1:
            first_char = message[0]
            # 單個前導字符
            if first_char in allowed_prefixes and message[1:].startswith(keyword):
                return message[1 + len(keyword):].strip()
            
            # 前導字符+空格的情況 (如 ". 小幫手")
            if len(message) > 2 and first_char in allowed_prefixes and message[1] == ' ':
                if message[2:].startswith(keyword):
                    return message[2 + len(keyword):].strip()
    
    # 3. 如果沒有找到關鍵字或無法提取，則使用整個訊息
    return message"""
    
    # 尋找原始的 extract_query 函數
    pattern = r'def extract_query\(message\):.*?return message'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        logger.error("無法在 line_webhook.py 中找到 extract_query 函數")
        return False
    
    # 替換函數
    updated_content = content.replace(match.group(0), new_function)
    
    # 寫入修改後的內容
    with open(webhook_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    logger.info("已更新 line_webhook.py 中的 extract_query 函數")
    return True

def update_webhook_is_ai_request():
    """更新 line_webhook.py 中的 is_ai_request 函數"""
    webhook_file = "/Users/al02451008/Documents/code/morning-post/src/line_webhook.py"
    
    # 讀取文件內容
    with open(webhook_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新 is_ai_request 函數
    new_function = """def is_ai_request(message):
    """檢查是否為 AI 對話請求 (最終版: 僅檢測訊息開頭或帶允許前導字符的關鍵字)
    
    判斷邏輯：
    1. 訊息以 'AI:', 'ai:', '@ai' 開頭
    2. 訊息以 '小幫手', '花生' 關鍵字開頭或帶允許的前導字符
    3. 對於正在進行中的對話，第二句之後不需要關鍵字
    """
    if not message:
        return False
    
    # 添加日誌以查看接收到的確切訊息
    logger.info(f"檢測訊息是否為AI請求: '{message}'")
    
    # 嘗試處理可能的特殊字符或編碼問題
    normalized_message = message
    try:
        # 先嘗試規範化字符
        import unicodedata
        normalized_message = unicodedata.normalize('NFKC', message)
        if normalized_message != message:
            logger.info(f"已規範化訊息: '{normalized_message}'")
    except Exception as e:
        logger.error(f"規範化訊息時出錯: {str(e)}")
    
    # 去除前後空格，便於檢查句首關鍵字
    trimmed_message = normalized_message.strip()
    message_lower = trimmed_message.lower()
    
    # 1. 檢查常見的AI前綴 (必須在句首)
    if (message_lower.startswith(('ai:', 'ai：')) or 
        message_lower.startswith(('@ai', '@ai ')) or
        message_lower.startswith('ai ') or 
        message_lower == 'ai'):
        logger.info("識別為AI請求: 前綴匹配")
        return True
    
    # 2. 檢查中文關鍵字是否在句首或帶有允許的前導字符
    keywords = ['小幫手', '花生']
    
    # 允許的前導字符列表
    allowed_prefixes = ['!', '！', ',', '，', '。', '.', '?', '？', ' ', '　', ':', '：', '@', '#', '$', '%', '、', '~', '～']
    
    for keyword in keywords:
        # 檢查關鍵字是否在句首
        if trimmed_message.startswith(keyword):
            logger.info(f"識別為AI請求: 檢測到句首關鍵字 '{keyword}'")
            return True
        
        # 檢查是否有允許的前導字符後接關鍵字
        if len(trimmed_message) > 1:
            # 處理只有一個前導字符的情況
            first_char = trimmed_message[0]
            if first_char in allowed_prefixes and trimmed_message[1:].startswith(keyword):
                logger.info(f"識別為AI請求: 檢測到帶前導字符的關鍵字 '{keyword}', 前導字符: '{first_char}'")
                return True
            
            # 處理有前導字符和空格的情況 (如 ". 小幫手")
            if len(trimmed_message) > 2 and first_char in allowed_prefixes and trimmed_message[1] == ' ':
                if trimmed_message[2:].startswith(keyword):
                    logger.info(f"識別為AI請求: 檢測到帶前導字符和空格的關鍵字 '{keyword}', 前導字符: '{first_char} '")
                    return True
    
    # 3. 特殊處理「花生」(字符級別)
    flower_char = '花'
    life_char = '生'
    
    # 直接在句首的「花生」
    if trimmed_message.startswith(flower_char) and len(trimmed_message) > 1:
        if trimmed_message[1] == life_char:
            logger.info(f"識別為AI請求: 通過字符級別檢測到句首 '花生' 關鍵字")
            return True
    
    # 允許的前導字符後的「花生」
    if len(trimmed_message) > 2 and trimmed_message[0] in allowed_prefixes:
        # 一個前導字符的情況
        if trimmed_message[1] == flower_char and trimmed_message[2] == life_char:
            logger.info(f"識別為AI請求: 通過字符級別檢測到帶前導字符的 '花生' 關鍵字")
            return True
        
        # 前導字符+空格的情況
        elif trimmed_message[1] == ' ' and len(trimmed_message) > 3:
            if trimmed_message[2] == flower_char and trimmed_message[3] == life_char:
                logger.info(f"識別為AI請求: 通過字符級別檢測到帶前導字符和空格的 '花生' 關鍵字")
                return True
    
    # 所有檢查都未通過
    logger.info("非AI請求: 未檢測到句首或帶允許前導字符的觸發關鍵字")
    return False"""
    
    # 尋找原始的 is_ai_request 函數
    pattern = r'def is_ai_request\(message\):.*?return False'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        logger.error("無法在 line_webhook.py 中找到 is_ai_request 函數")
        return False
    
    # 替換函數
    updated_content = content.replace(match.group(0), new_function)
    
    # 寫入修改後的內容
    with open(webhook_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    logger.info("已更新 line_webhook.py 中的 is_ai_request 函數")
    return True

if __name__ == "__main__":
    print("""
    #########################################################
    #                                                       #
    #           LINE Bot 關鍵字位置檢測更新工具               #
    #                                                       #
    #########################################################
    
    此工具將修改關鍵字檢測邏輯，使得:
    1. 僅檢測訊息開頭或帶有允許前導字符的關鍵字
    2. 允許的前導字符包括標點符號、空格等
    3. 支援前導字符+空格+關鍵字的格式 (如 ". 小幫手")
    """)
    
    success_app = update_app_py()
    success_webhook = update_webhook_is_ai_request()
    success_extract = update_extract_query()
    
    if success_app and success_webhook and success_extract:
        print("\n✅ 所有更新完成!")
        print("✅ 已更新 app.py 中的 is_ai_request 函數")
        print("✅ 已更新 line_webhook.py 中的 is_ai_request 函數")
        print("✅ 已更新 line_webhook.py 中的 extract_query 函數")
        print("\n更新內容:")
        print("1. 只檢測訊息開頭或帶有允許前導字符的關鍵字")
        print("2. 允許的前導字符包括標點符號、空格等")
        print("3. 支援前導字符+空格+關鍵字的格式 (如 \". 小幫手\")")
        print("\n請執行 python3 test_keyword_position_final.py 進行測試")
    else:
        print("\n❌ 更新過程中出現問題，請檢查日誌文件")
