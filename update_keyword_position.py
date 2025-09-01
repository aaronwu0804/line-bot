#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LINE Bot 關鍵字位置檢測修復工具 (最終版)
================================================

此工具將修改關鍵字檢測邏輯，使得:
1. 只有訊息開頭的關鍵字才會觸發AI回應，而非訊息中的任何位置
2. 允許前3個字符內出現的關鍵字觸發 (考慮可能的空格或表情符號)
3. 更新 extract_query 函數匹配新的檢測邏輯
4. 兼容所有支援的關鍵字 ("AI:", "@AI", "小幫手", "花生")

使用方法:
    python update_keyword_position.py
"""

import os
import re
import sys
import logging
import datetime

# 配置日誌
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"keyword_position_update_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.log")

# 配置 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("keyword_position_update")

def update_app_is_ai_request(app_file):
    """更新 app.py 中的 is_ai_request 函數"""
    try:
        # 讀取整個文件內容
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找出並替換 is_ai_request 函數
        start_marker = "def is_ai_request(message):"
        start_idx = content.find(start_marker)
        if start_idx == -1:
            logger.error("找不到 is_ai_request 函數")
            return False
            
        # 尋找函數結束 - 使用下一個 def 作為標記
        next_def_idx = content.find("\ndef ", start_idx + len(start_marker))
        if next_def_idx == -1:
            logger.error("找不到 is_ai_request 函數的結束位置")
            return False
            
        # 提取整個函數
        old_function = content[start_idx:next_def_idx].strip()
        logger.info(f"找到原始 is_ai_request 函數:\n{old_function}")
        
        # 創建新的函數
        new_function = """def is_ai_request(message):
    """檢查是否為AI請求 (最終版: 僅檢測訊息開頭的關鍵字)"""
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
    
    # 2. 檢查中文關鍵字是否在句首或句首附近 (前3個字符內)
    keywords = ['小幫手', '花生']
    
    for keyword in keywords:
        # 檢查關鍵字是否在句首
        if trimmed_message.startswith(keyword):
            logger.info(f"識別為AI請求: 檢測到句首關鍵字 '{keyword}'")
            return True
            
        # 檢查關鍵字是否在句首附近 (前3個字符內)
        if len(trimmed_message) > 3:
            position = trimmed_message.find(keyword)
            if position > 0 and position <= 3:
                logger.info(f"識別為AI請求: 檢測到句首附近的關鍵字 '{keyword}'，位置: {position}")
                return True
    
    # 3. 進行字符級別的檢查，確保在句首或句首附近 (前3個字符內)
    # 花生的Unicode碼位是: 33457(花), 29983(生)
    flower_char = '花'  # Unicode: 33457
    life_char = '生'    # Unicode: 29983
    
    flower_pos = trimmed_message.find(flower_char)
    if flower_pos != -1 and flower_pos <= 3:
        if flower_pos + 1 < len(trimmed_message) and trimmed_message[flower_pos + 1] == life_char:
            logger.info(f"識別為AI請求: 通過字符級別檢測到句首附近的 '花生' 關鍵字，位置: {flower_pos}")
            return True
    
    # 所有檢查都未通過
    logger.info("非AI請求: 未檢測到句首或句首附近的觸發關鍵字")
    return False"""
        
        # 替換函數
        new_content = content.replace(old_function, new_function)
        
        # 寫入文件
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        logger.info("已更新 app.py 中的 is_ai_request 函數")
        
        return True
    except Exception as e:
        logger.error(f"更新 app.py 中的 is_ai_request 函數時發生錯誤: {str(e)}")
        return False

def update_webhook_is_ai_request(webhook_file):
    """更新 line_webhook.py 中的 is_ai_request 函數"""
    try:
        # 讀取整個文件內容
        with open(webhook_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找出並替換 is_ai_request 函數
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
    """檢查是否為 AI 對話請求 (最終版: 僅檢測訊息開頭的關鍵字)
    
    判斷邏輯：
    1. 訊息以 'AI:', 'ai:', '@ai' 開頭
    2. 訊息以 '小幫手', '花生' 關鍵字開頭或在句首附近 (前3個字符內)
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
    
    # 2. 檢查中文關鍵字是否在句首或句首附近 (前3個字符內)
    keywords = ['小幫手', '花生']
    
    for keyword in keywords:
        # 檢查關鍵字是否在句首
        if trimmed_message.startswith(keyword):
            logger.info(f"識別為AI請求: 檢測到句首關鍵字 '{keyword}'")
            return True
            
        # 檢查關鍵字是否在句首附近 (前3個字符內)
        if len(trimmed_message) > 3:
            position = trimmed_message.find(keyword)
            if position > 0 and position <= 3:
                logger.info(f"識別為AI請求: 檢測到句首附近的關鍵字 '{keyword}'，位置: {position}")
                return True
    
    # 3. 進行字符級別的檢查，確保在句首或句首附近 (前3個字符內)
    # 花生的Unicode碼位是: 33457(花), 29983(生)
    flower_char = '花'  # Unicode: 33457
    life_char = '生'    # Unicode: 29983
    
    flower_pos = trimmed_message.find(flower_char)
    if flower_pos != -1 and flower_pos <= 3:
        if flower_pos + 1 < len(trimmed_message) and trimmed_message[flower_pos + 1] == life_char:
            logger.info(f"識別為AI請求: 通過字符級別檢測到句首附近的 '花生' 關鍵字，位置: {flower_pos}")
            return True
    
    # 所有檢查都未通過
    logger.info("非AI請求: 未檢測到句首或句首附近的觸發關鍵字")
    return False"""
        
        # 替換函數
        updated_content = content.replace(old_function, new_function)
        
        # 寫入文件
        with open(webhook_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        logger.info("已更新 line_webhook.py 中的 is_ai_request 函數")
        
        # 還需要修改 extract_query 函數來適配新的檢測邏輯
        update_extract_query(webhook_file, updated_content)
        
        return True
    except Exception as e:
        logger.error(f"更新 line_webhook.py 中的 is_ai_request 函數時發生錯誤: {str(e)}")
        return False

def update_extract_query(webhook_file, content):
    """更新 extract_query 函數以適配新的檢測邏輯"""
    try:
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
        updated_content = content.replace(old_function, new_function)
        
        # 寫入文件
        with open(webhook_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        logger.info("已更新 line_webhook.py 中的 extract_query 函數")
        
        return True
    except Exception as e:
        logger.error(f"更新 extract_query 函數時發生錯誤: {str(e)}")
        return False

def create_deploy_script():
    """創建部署腳本"""
    script_content = """#!/bin/bash

# LINE Bot 關鍵字位置檢測更新部署腳本
echo "===== 開始部署關鍵字位置檢測更新 ====="
echo "$(date)"

# 1. 推送更改到 GitHub
git add app.py src/line_webhook.py
git commit -m "更新關鍵字檢測邏輯: 僅檢測訊息開頭的關鍵字"
git push

# 2. 觸發 Render 重新部署
echo "正在觸發 Render 重新部署..."
curl -X POST $RENDER_DEPLOY_HOOK

echo ""
echo "===== 部署命令已執行 ====="
echo "Render 重新部署已觸發，等待 1-2 分鐘生效"
echo "$(date)"
"""
    
    script_path = "/Users/al02451008/Documents/code/morning-post/deploy_keyword_position_fix.sh"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # 設定腳本執行權限
    os.chmod(script_path, 0o755)
    logger.info(f"已創建部署腳本: {script_path}")

def main():
    """主函數"""
    banner = """
    #########################################################
    #                                                       #
    #       LINE Bot 關鍵字位置檢測修復工具 (最終版)         #
    #                                                       #
    #########################################################
    
    此工具將:
    1. 修改關鍵字檢測邏輯，使得只有訊息開頭的關鍵字才會觸發AI回應
    2. 允許前3個字符內出現的關鍵字觸發 (考慮空格或表情符號)
    3. 更新 extract_query 函數匹配新的檢測邏輯
    4. 創建部署腳本，方便推送更新到 Render
    """
    
    print(banner)
    logger.info("開始執行關鍵字位置檢測修復")
    
    app_file = "/Users/al02451008/Documents/code/morning-post/app.py"
    webhook_file = "/Users/al02451008/Documents/code/morning-post/src/line_webhook.py"
    
    # 1. 更新 app.py
    if update_app_is_ai_request(app_file):
        logger.info("成功更新 app.py 中的 is_ai_request 函數")
    else:
        logger.error("更新 app.py 失敗")
        return
    
    # 2. 更新 line_webhook.py
    if update_webhook_is_ai_request(webhook_file):
        logger.info("成功更新 line_webhook.py 中的函數")
    else:
        logger.error("更新 line_webhook.py 失敗")
        return
    
    # 3. 創建部署腳本
    create_deploy_script()
    
    logger.info("修復完成！")
    print("\n修復成功完成！已創建部署腳本 deploy_keyword_position_fix.sh")
    print("請查看日誌文件以獲取詳細資訊:", log_file)
    print("\n要部署更新，請執行:")
    print("    ./deploy_keyword_position_fix.sh")

if __name__ == "__main__":
    main()
