#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/render_keyword_fix.py
"""
Render 平台專用關鍵字檢測修復腳本
針對 Render 環境的特殊處理
"""

import os
import sys
import logging
import json
from datetime import datetime

# 設置日誌
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, 'render_keyword_fix.log')

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
    \"\"\"檢查是否為AI請求 (Render 專用增強版)\"\"\"
    # 無論如何先記錄原始訊息，方便診斷
    logger.info(f"[RENDER-FIX] 檢查訊息: '{message}'")
    if not message:
        return False
    
    try:
        # 檢查原始訊息
        # 1. 檢查前綴
        message_lower = message.lower().strip()
        if (message_lower.startswith(('ai:', 'ai：')) or 
            message_lower.startswith(('@ai', '@ai ')) or 
            message_lower.startswith('ai ') or 
            message_lower == 'ai'):
            logger.info(f"[RENDER-FIX] 前綴匹配成功: '{message}'")
            return True
            
        # 2. 直接檢查關鍵字 (獨立檢查每個關鍵字，記錄詳細信息)
        if '小幫手' in message:
            logger.info(f"[RENDER-FIX] 檢測到關鍵字 '小幫手': '{message}'")
            return True
            
        if '花生' in message:
            logger.info(f"[RENDER-FIX] 檢測到關鍵字 '花生': '{message}'")
            return True
            
        # 3. 字符級別檢查
        for i in range(len(message) - 1):
            # 花生的Unicode碼位是: 33457(花), 29983(生)
            try:
                if (i + 1 < len(message) and 
                    ord(message[i]) == 33457 and 
                    ord(message[i+1]) == 29983):
                    logger.info(f"[RENDER-FIX] 通過字符級別檢測到 '花生': '{message}'")
                    return True
            except Exception as e:
                logger.error(f"[RENDER-FIX] 字符檢查出錯: {str(e)}")
                
        # 4. 手動比對每個字符
        logger.info(f"[RENDER-FIX] 訊息字符詳情:")
        for i, c in enumerate(message):
            try:
                logger.info(f"[RENDER-FIX] 位置 {i}: '{c}' (Unicode: {ord(c)})")
                # 花: 33457, 生: 29983
                if ord(c) == 33457:
                    logger.info(f"[RENDER-FIX] 檢測到字符 '花'")
                    # 檢查下一個字符是否為 '生'
                    if i + 1 < len(message) and ord(message[i+1]) == 29983:
                        logger.info(f"[RENDER-FIX] 檢測到連續字符 '花生'")
                        return True
            except Exception as e:
                logger.error(f"[RENDER-FIX] 分析字符 {i} 時出錯: {str(e)}")
                
        # 5. 使用不同編碼嘗試
        try:
            normalized = message.encode('utf-8').decode('utf-8')
            if '花生' in normalized:
                logger.info(f"[RENDER-FIX] UTF-8 轉換後檢測到 '花生': '{message}' -> '{normalized}'")
                return True
        except Exception as e:
            logger.error(f"[RENDER-FIX] UTF-8 轉換出錯: {str(e)}")
            
        # 最終檢查：列出所有可能標記為 AI 請求的條件
        logger.info(f"[RENDER-FIX] 訊息未包含任何觸發關鍵字: '{message}'")
        return False
    except Exception as e:
        logger.error(f"[RENDER-FIX] is_ai_request 出現未處理的錯誤: {str(e)}")
        # 安全起見，發生任何錯誤時，我們不把它視為 AI 請求
        return False
"""
    
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
    \"\"\"檢查是否為 AI 對話請求 (Render 專用增強版)
    
    判斷邏輯：
    1. 訊息以 'AI:', 'ai:', '@ai' 開頭
    2. 訊息中包含 '小幫手', '花生' 關鍵字
    3. 對於正在進行中的對話，第二句之後不需要關鍵字
    \"\"\"
    # 無論如何先記錄原始訊息，方便診斷
    logger.info(f"[RENDER-FIX] 檢查訊息: '{message}'")
    if not message:
        return False
    
    try:
        # 檢查原始訊息
        # 1. 檢查前綴
        message_lower = message.lower().strip()
        if (message_lower.startswith(('ai:', 'ai：')) or 
            message_lower.startswith(('@ai', '@ai ')) or 
            message_lower.startswith('ai ') or 
            message_lower == 'ai'):
            logger.info(f"[RENDER-FIX] 前綴匹配成功: '{message}'")
            return True
            
        # 2. 直接檢查關鍵字 (獨立檢查每個關鍵字，記錄詳細信息)
        if '小幫手' in message:
            logger.info(f"[RENDER-FIX] 檢測到關鍵字 '小幫手': '{message}'")
            return True
            
        if '花生' in message:
            logger.info(f"[RENDER-FIX] 檢測到關鍵字 '花生': '{message}'")
            return True
            
        # 3. 字符級別檢查
        for i in range(len(message) - 1):
            # 花生的Unicode碼位是: 33457(花), 29983(生)
            try:
                if (i + 1 < len(message) and 
                    ord(message[i]) == 33457 and 
                    ord(message[i+1]) == 29983):
                    logger.info(f"[RENDER-FIX] 通過字符級別檢測到 '花生': '{message}'")
                    return True
            except Exception as e:
                logger.error(f"[RENDER-FIX] 字符檢查出錯: {str(e)}")
                
        # 4. 手動比對每個字符
        logger.info(f"[RENDER-FIX] 訊息字符詳情:")
        for i, c in enumerate(message):
            try:
                logger.info(f"[RENDER-FIX] 位置 {i}: '{c}' (Unicode: {ord(c)})")
                # 花: 33457, 生: 29983
                if ord(c) == 33457:
                    logger.info(f"[RENDER-FIX] 檢測到字符 '花'")
                    # 檢查下一個字符是否為 '生'
                    if i + 1 < len(message) and ord(message[i+1]) == 29983:
                        logger.info(f"[RENDER-FIX] 檢測到連續字符 '花生'")
                        return True
            except Exception as e:
                logger.error(f"[RENDER-FIX] 分析字符 {i} 時出錯: {str(e)}")
                
        # 5. 使用不同編碼嘗試
        try:
            normalized = message.encode('utf-8').decode('utf-8')
            if '花生' in normalized:
                logger.info(f"[RENDER-FIX] UTF-8 轉換後檢測到 '花生': '{message}' -> '{normalized}'")
                return True
        except Exception as e:
            logger.error(f"[RENDER-FIX] UTF-8 轉換出錯: {str(e)}")
            
        # 最終檢查：列出所有可能標記為 AI 請求的條件
        logger.info(f"[RENDER-FIX] 訊息未包含任何觸發關鍵字: '{message}'")
        return False
    except Exception as e:
        logger.error(f"[RENDER-FIX] is_ai_request 出現未處理的錯誤: {str(e)}")
        # 安全起見，發生任何錯誤時，我們不把它視為 AI 請求
        return False

"""
    
    # 替換函數
    new_content = content.replace(old_function, new_function)
    
    # 寫入文件
    with open(webhook_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    logger.info("已更新 line_webhook.py 中的 is_ai_request 函數")
    
    return True

if __name__ == "__main__":
    banner = """
    #########################################################
    #                                                       #
    #       Render 專用關鍵字檢測修復工具                    #
    #                                                       #
    #########################################################
    
    此工具專為 Render 平台設計，用於修復關鍵字檢測問題
    包含更詳細的日誌和各種字符級別的檢測方法
    """
    
    print(banner)
    
    input_text = input("是否要執行 Render 專用關鍵字檢測修復? (y/n): ")
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
