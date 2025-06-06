#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最終關鍵字檢測邏輯更新腳本 - 解決點號和空格問題

將app.py和src/line_webhook.py中的關鍵字檢測功能更新為只檢測句首或帶允許前導字符的關鍵字。
特別處理點號+空格前導字符的情況。
"""

import re
import os
import shutil
from datetime import datetime
import logging

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def update_app_py():
    """更新app.py中的關鍵字檢測功能"""
    app_file = 'app.py'
    logger.info(f"開始更新 {app_file}")
    
    # 檢查文件是否存在
    if not os.path.exists(app_file):
        logger.error(f"{app_file} 文件不存在")
        return False
    
    # 讀取文件內容
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 備份原文件
    backup_file = f"{app_file}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy2(app_file, backup_file)
    logger.info(f"已備份 {app_file} 至 {backup_file}")
    
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
            # 特殊處理點號和空格的情況，確保正確識別
            if len(trimmed_message) > 2 and first_char in allowed_prefixes:
                # 直接指定處理點號+空格的情況
                if first_char == '.' and trimmed_message[1] == ' ':
                    if trimmed_message[2:].startswith(keyword):
                        logger.info(f"識別為AI請求: 檢測到點號+空格前導的關鍵字 '{keyword}'")
                        return True
                
                # 正常處理其他前導字符+空格的情況
                if trimmed_message[1] == ' ' and trimmed_message[2:].startswith(keyword):
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
            
        # 前導字符+空格的情況 (如 ". 花生")
        elif trimmed_message[1] == ' ' and len(trimmed_message) > 3:
            # 特殊處理點號+空格的情況
            if trimmed_message[0] == '.' and trimmed_message[2] == flower_char and trimmed_message[3] == life_char:
                logger.info(f"識別為AI請求: 通過字符級別檢測到點號+空格前導的 '花生' 關鍵字")
                return True
                
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
    updated_content = content.replace(match.group(), new_function)
    
    # 寫入更新後的內容
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    logger.info(f"{app_file} 中的 is_ai_request 函數已更新")
    return True

def update_line_webhook_py():
    """更新src/line_webhook.py中的關鍵字檢測功能"""
    webhook_file = 'src/line_webhook.py'
    logger.info(f"開始更新 {webhook_file}")
    
    # 檢查文件是否存在
    if not os.path.exists(webhook_file):
        logger.error(f"{webhook_file} 文件不存在")
        return False
    
    # 讀取文件內容
    with open(webhook_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 備份原文件
    backup_file = f"{webhook_file}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"已備份 {webhook_file} 至 {backup_file}")
    
    # 更新 is_ai_request 函數
    new_function = """def is_ai_request(message):
    """檢查是否為 AI 對話請求 (最終版: 僅檢測訊息開頭或帶允許前導字符的關鍵字)
    
    判斷邏輯：
    1. 訊息以 'AI:', 'ai:', '@ai' 開頭
    2. 訊息以 '小幫手', '花生' 關鍵字開頭或帶有允許的前導字符
    3. 對於正在進行中的對話，第二句之後不需要關鍵字
    """
    if not message:
        return False
    
    # 添加詳細日誌以診斷問題
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
            # 特殊處理點號和空格的情況，確保正確識別
            if len(trimmed_message) > 2 and first_char in allowed_prefixes:
                # 直接指定處理點號+空格的情況
                if first_char == '.' and trimmed_message[1] == ' ':
                    if trimmed_message[2:].startswith(keyword):
                        logger.info(f"識別為AI請求: 檢測到點號+空格前導的關鍵字 '{keyword}'")
                        return True
                
                # 正常處理其他前導字符+空格的情況
                if trimmed_message[1] == ' ' and trimmed_message[2:].startswith(keyword):
                    logger.info(f"識別為AI請求: 檢測到帶前導字符和空格的關鍵字 '{keyword}', 前導字符: '{first_char} '")
                    return True
    
    # 3. 進行字符級別的檢查 (花生)
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
            
        # 前導字符+空格的情況 (如 ". 花生")
        elif trimmed_message[1] == ' ' and len(trimmed_message) > 3:
            # 特殊處理點號+空格的情況
            if trimmed_message[0] == '.' and trimmed_message[2] == flower_char and trimmed_message[3] == life_char:
                logger.info(f"識別為AI請求: 通過字符級別檢測到點號+空格前導的 '花生' 關鍵字")
                return True
                
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
    updated_content = content.replace(match.group(), new_function)
    
    # 更新 extract_query 函數
    new_extract_query = """def extract_query(message):
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
                # 特殊處理點號+空格的情況
                if first_char == '.' and message[2:].startswith(keyword):
                    return message[2 + len(keyword):].strip()
                    
                if message[2:].startswith(keyword):
                    return message[2 + len(keyword):].strip()
    
    # 3. 處理「花生」字符級別檢測
    flower_char = '花'
    life_char = '生'
    
    # 直接在句首的「花生」
    if message.startswith(flower_char) and len(message) > 1:
        if message[1] == life_char:
            return message[2:].strip()
    
    # 允許的前導字符後的「花生」
    if len(message) > 2 and message[0] in allowed_prefixes:
        # 一個前導字符的情況
        if message[1] == flower_char and message[2] == life_char:
            return message[3:].strip()
        
        # 前導字符+空格的情況
        elif message[1] == ' ' and len(message) > 3:
            # 特殊處理點號+空格的情況
            if message[0] == '.' and message[2] == flower_char and message[3] == life_char:
                return message[4:].strip()
                
            if message[2] == flower_char and message[3] == life_char:
                return message[4:].strip()
    
    # 如果沒有找到關鍵字或無法提取，則使用整個訊息
    return message"""
    
    # 尋找原始的 extract_query 函數
    pattern = r'def extract_query\(message\):.*?return message'
    match = re.search(pattern, updated_content, re.DOTALL)
    
    if not match:
        logger.error("無法在 line_webhook.py 中找到 extract_query 函數")
        return False
    
    # 替換函數
    updated_content = updated_content.replace(match.group(), new_extract_query)
    
    # 寫入更新後的內容
    with open(webhook_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    logger.info(f"{webhook_file} 中的函數已更新")
    return True

def main():
    """主函數"""
    logger.info("開始執行最終關鍵字檢測邏輯更新腳本")
    
    # 更新app.py
    if update_app_py():
        logger.info("app.py 更新成功")
    else:
        logger.error("app.py 更新失敗")
    
    # 更新src/line_webhook.py
    if update_line_webhook_py():
        logger.info("src/line_webhook.py 更新成功")
    else:
        logger.error("src/line_webhook.py 更新失敗")
    
    logger.info("最終關鍵字檢測邏輯更新完成")

if __name__ == "__main__":
    main()
