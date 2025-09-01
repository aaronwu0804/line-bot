#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/fix_keyword_position.py
"""
關鍵字位置檢測修復工具
修改關鍵字檢測邏輯，使得:
1. 前綴關鍵詞（如「AI:」）需要在句首才算
2. 「花生」和「小幫手」等關鍵字也必須在句首或靠近句首才觸發AI回應
"""

import os
import sys
import re
import logging
from datetime import datetime

# 設置日誌
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, 'fix_keyword_position.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fix_app_py():
    """修復 app.py 中的關鍵字檢測"""
    app_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    if not os.path.exists(app_file):
        logger.error(f"找不到檔案: {app_file}")
        return False
        
    # 備份原始檔案
    backup_time = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file = app_file + f'.bak.{backup_time}'
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"已備份原始 app.py 至: {backup_file}")
    
    # 找出並替換 is_ai_request 函數
    # 尋找函數開始
    start_marker = "def is_ai_request(message):"
    start_idx = content.find(start_marker)
    if start_idx == -1:
        logger.error("找不到 is_ai_request 函數")
        return False
        
    # 尋找函數結束
    # 假設函數結束於下一個 def 之前
    next_def_idx = content.find("def ", start_idx + len(start_marker))
    if next_def_idx == -1:
        logger.error("找不到 is_ai_request 函數的結束位置")
        return False
        
    # 提取整個函數
    old_function = content[start_idx:next_def_idx].strip()
    logger.info(f"找到原始 is_ai_request 函數:\n{old_function}")
    
    # 創建新的函數
    new_function = """def is_ai_request(message):
    """檢查是否為AI請求 (修改版: 關鍵字位置檢測)"""
    if not message:
        return False
    
    # 添加日誌以查看接收到的確切訊息
    logger.info(f"檢測訊息是否為AI請求: '{message}'")
    
    message_lower = message.lower().strip()
    
    # 1. 檢查常見的AI前綴 (必須在句首)
    if (message_lower.startswith(('ai:', 'ai：')) or 
        message_lower.startswith(('@ai', '@ai ')) or
        message_lower.startswith('ai ') or 
        message_lower == 'ai'):
        logger.info("識別為AI請求: 前綴匹配")
        return True
    
    # 2. 檢查關鍵字是否在句首或句首附近 (前3個字符內)
    keywords = ['小幫手', '花生']
    
    # 移除前後空格以準確檢查
    trimmed_message = message.strip()
    
    for keyword in keywords:
        # 檢查關鍵字是否在句首
        if trimmed_message.startswith(keyword):
            logger.info(f"識別為AI請求: 檢測到句首關鍵字 '{keyword}'")
            return True
            
        # 檢查關鍵字是否在句首附近 (前3個字符內，考慮表情符號等情況)
        if len(trimmed_message) > 3:
            prefix = trimmed_message[:3]
            # 檢查關鍵字是否緊跟在前綴後面
            position = trimmed_message.find(keyword)
            if position > 0 and position <= 3:
                logger.info(f"識別為AI請求: 檢測到句首附近的關鍵字 '{keyword}'，位置: {position}")
                return True
    
    # 所有檢查都未通過
    logger.info("非AI請求: 未檢測到符合條件的觸發關鍵字")
    return False"""
    
    # 替換函數
    new_content = content.replace(old_function, new_function)
    
    # 寫入文件
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    logger.info("已更新 app.py 中的 is_ai_request 函數")
    
    return True
    
def fix_line_webhook_py():
    """修復 src/line_webhook.py 中的關鍵字檢測"""
    webhook_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'line_webhook.py')
    if not os.path.exists(webhook_file):
        logger.error(f"找不到檔案: {webhook_file}")
        return False
        
    # 備份原始檔案
    backup_time = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file = webhook_file + f'.bak.{backup_time}'
    
    with open(webhook_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"已備份原始 line_webhook.py 至: {backup_file}")
    
    # 找出並替換 is_ai_request 函數
    # 尋找函數開始
    start_marker = "def is_ai_request(message):"
    start_idx = content.find(start_marker)
    if start_idx == -1:
        logger.error("找不到 is_ai_request 函數")
        return False
        
    # 尋找函數結束
    # 這個函數通常以 "def extract_query" 開始的下一個函數為結束
    end_marker = "def extract_query"
    end_idx = content.find(end_marker, start_idx)
    if end_idx == -1:
        logger.error("找不到 is_ai_request 函數的結束位置")
        return False
        
    # 提取整個函數
    old_function = content[start_idx:end_idx].strip()
    logger.info(f"找到原始 is_ai_request 函數:\n{old_function}")
    
    # 創建新的函數
    new_function = """def is_ai_request(message):
    """檢查是否為 AI 對話請求 (修改版: 關鍵字位置檢測)
    
    判斷邏輯：
    1. 訊息以 'AI:', 'ai:', '@ai' 開頭
    2. 訊息以或幾乎以 '小幫手', '花生' 開頭
    3. 對於正在進行中的對話，第二句之後不需要關鍵字
    """
    if not message:
        return False
    
    # 添加日誌以查看接收到的確切訊息
    logger.info(f"檢測訊息是否為AI請求: '{message}'")
    
    message_lower = message.lower().strip()
    
    # 1. 檢查明確的前綴 (必須在句首)
    if (message_lower.startswith(('ai:', 'ai：')) or 
        message_lower.startswith(('@ai', '@ai ')) or 
        message_lower.startswith('ai ') or 
        message_lower == 'ai'):
        logger.info("識別為AI請求: 前綴匹配")
        return True
    
    # 2. 檢查關鍵字是否在句首或句首附近 (前3個字符內)
    keywords = ['小幫手', '花生']
    
    # 移除前後空格以準確檢查
    trimmed_message = message.strip()
    
    for keyword in keywords:
        # 檢查關鍵字是否在句首
        if trimmed_message.startswith(keyword):
            logger.info(f"識別為AI請求: 檢測到句首關鍵字 '{keyword}'")
            return True
            
        # 檢查關鍵字是否在句首附近 (前3個字符內，考慮表情符號等情況)
        if len(trimmed_message) > 3:
            prefix = trimmed_message[:3]
            # 檢查關鍵字是否緊跟在前綴後面
            position = trimmed_message.find(keyword)
            if position > 0 and position <= 3:
                logger.info(f"識別為AI請求: 檢測到句首附近的關鍵字 '{keyword}'，位置: {position}")
                return True
    
    # 3. 檢查用戶是否處於活躍對話狀態 (這部分保持不變)
    # 如果用戶ID在全局變數中被標記為處於對話模式，則視為AI請求
    # 這部分將在其他函數中實現
    
    # 所有檢查都未通過
    logger.info("非AI請求: 未檢測到符合條件的觸發關鍵字")
"""
    
    # 替換函數
    new_content = content.replace(old_function, new_function)
    
    # 寫入文件
    with open(webhook_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    logger.info("已更新 line_webhook.py 中的 is_ai_request 函數")
    
    # 還需要修改 extract_query 函數來適配新的檢測邏輯
    update_extract_query(webhook_file, content)
    
    return True

def update_extract_query(webhook_file, content):
    """更新 extract_query 函數以適配新的檢測邏輯"""
    # 尋找函數開始
    start_marker = "def extract_query(message):"
    start_idx = content.find(start_marker)
    if start_idx == -1:
        logger.error("找不到 extract_query 函數")
        return False
        
    # 尋找函數結束
    # 這個函數通常以 "def update_conversation_history" 開始的下一個函數為結束
    end_marker = "def update_conversation_history"
    end_idx = content.find(end_marker, start_idx)
    if end_idx == -1:
        logger.error("找不到 extract_query 函數的結束位置")
        return False
        
    # 提取整個函數
    old_function = content[start_idx:end_idx].strip()
    logger.info(f"找到原始 extract_query 函數:\n{old_function}")
    
    # 創建新的函數
    new_function = """def extract_query(message):
    """從訊息中提取實際查詢內容 (修改版: 適配關鍵字位置檢測)"""
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
    
    # 2. 處理「小幫手」和「花生」關鍵字 (只考慮句首或句首附近)
    keywords = ['小幫手', '花生']
    
    for keyword in keywords:
        # 如果關鍵字在開頭，移除它
        if message.startswith(keyword):
            return message[len(keyword):].strip()
        
        # 檢查關鍵字是否在句首附近 (前3個字符內)
        if len(message) > 3:
            position = message.find(keyword)
            if position > 0 and position <= 3:
                return message[position + len(keyword):].strip()
    
    # 3. 如果沒有找到關鍵字或無法提取，則使用整個訊息
    return message"""
    
    # 替換函數
    with open(webhook_file, 'r', encoding='utf-8') as f:
        updated_content = f.read()
        
    updated_content = updated_content.replace(old_function, new_function)
    
    # 寫入文件
    with open(webhook_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    logger.info("已更新 line_webhook.py 中的 extract_query 函數")
    
    return True

if __name__ == "__main__":
    banner = """
    #########################################################
    #                                                       #
    #            LINE Bot 關鍵字位置檢測修復工具             #
    #                                                       #
    #########################################################
    
    此工具將修改關鍵字檢測邏輯，使得:
    1. 前綴關鍵詞（如「AI:」）需要在句首才算
    2. 「花生」和「小幫手」等關鍵字也必須在句首或靠近句首才觸發AI回應
    例如：「花生，告訴我」會觸發，但「我想吃花生」不會觸發
    """
    
    print(banner)
    
    input_text = input("是否要執行關鍵字位置檢測修復? (y/n): ")
    if input_text.lower() == 'y':
        app_result = fix_app_py()
        webhook_result = fix_line_webhook_py()
        
        if app_result and webhook_result:
            print("\n✓ 修復已完成! 接下來請重新部署應用。")
            print("\n請使用以下命令部署到 Render:")
            print("\nbash deploy_keyword_fix.sh")
        else:
            print("\n✗ 修復失敗! 請檢查日誌以獲取更多信息。")
    else:
        print("已取消操作")
