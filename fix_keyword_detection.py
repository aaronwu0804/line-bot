#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/fix_keyword_detection.py
"""
緊急修復腳本：更新 LINE Bot 的關鍵字檢測
確保 'app.py' 和 'src/line_webhook.py' 都能正確檢測關鍵字
"""

import os
import sys
import re
import logging
from datetime import datetime

# 設置日誌
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'fix_keyword.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def apply_fix():
    """應用關鍵字檢測修復"""
    logger.info("開始執行關鍵字檢測修復腳本...")
    
    # 檢查並修復 app.py
    app_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    line_webhook_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'line_webhook.py')
    
    if not os.path.exists(app_file):
        logger.error(f"找不到檔案: {app_file}")
        return False
    
    # 讀取 app.py
    with open(app_file, 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # 備份原始檔案
    backup_file = app_file + f'.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(app_content)
    logger.info(f"已備份原始 app.py 至: {backup_file}")
    
    # 更新 is_ai_request 函數
    updated_is_ai_request = '''def is_ai_request(message):
    """檢查是否為AI請求"""
    if not message:
        return False
    
    message_lower = message.lower().strip()
    # 檢查常見的AI前綴
    if (message_lower.startswith(('ai:', 'ai：')) or 
        message_lower.startswith(('@ai', '@ai ')) or
        message_lower.startswith('ai ') or 
        message_lower == 'ai'):
        return True
        
    # 檢查其他觸發關鍵字 (單獨檢測每個關鍵詞，並加入詳細日誌)
    if '小幫手' in message:
        logger.info(f"檢測到關鍵字 '小幫手' 在訊息中: {message}")
        return True
    if '花生' in message:
        logger.info(f"檢測到關鍵字 '花生' 在訊息中: {message}")
        return True
    
    # 添加訊息字符分析
    logger.info(f"訊息字符ASCII碼: {[ord(c) for c in message[:20]]}")
    logger.info(f"未檢測到任何關鍵字，訊息為: {message}")
    return False'''
    
    # 使用正則表達式尋找和替換 is_ai_request 函數
    pattern = r'def is_ai_request\(message\):.*?return False'
    replacement = updated_is_ai_request
    
    # 正則表達式使用 DOTALL 標誌匹配多行文本
    updated_app_content = re.sub(pattern, replacement, app_content, flags=re.DOTALL)
    
    if app_content == updated_app_content:
        logger.warning("無法在 app.py 中找到 is_ai_request 函數，或者無法進行修改")
    else:
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(updated_app_content)
        logger.info("已成功更新 app.py 中的 is_ai_request 函數")
    
    # 同樣檢查並修復 line_webhook.py
    if os.path.exists(line_webhook_file):
        with open(line_webhook_file, 'r', encoding='utf-8') as f:
            line_webhook_content = f.read()
        
        # 備份原始檔案
        backup_line_webhook = line_webhook_file + f'.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}'
        with open(backup_line_webhook, 'w', encoding='utf-8') as f:
            f.write(line_webhook_content)
        logger.info(f"已備份原始 line_webhook.py 至: {backup_line_webhook}")
        
        updated_line_webhook_ai_request = '''def is_ai_request(message):
    """檢查是否為 AI 對話請求
    
    判斷邏輯：
    1. 訊息以 'AI:', 'ai:', '@ai' 開頭
    2. 訊息中包含 '小幫手', '花生' 關鍵字
    3. 對於正在進行中的對話，第二句之後不需要關鍵字
    """
    if not message:
        return False
    
    message_lower = message.lower().strip()
    
    # 檢查明確的前綴
    if (message_lower.startswith(('ai:', 'ai：')) or 
        message_lower.startswith(('@ai', '@ai ')) or 
        message_lower.startswith('ai ') or 
        message_lower == 'ai'):
        return True
    
    # 檢查其他觸發關鍵字
    if '小幫手' in message or '花生' in message:
        logger.info(f"檢測到關鍵字 '小幫手' 或 '花生' 在訊息中: {message}")
        return True
    
    # 如果用戶ID在全局變數中被標記為處於對話模式，則視為AI請求
    # 這部分將在其他函數中實現
    
    return False'''
        
        pattern_line_webhook = r'def is_ai_request\(message\):.*?return False'
        updated_line_webhook_content = re.sub(pattern_line_webhook, updated_line_webhook_ai_request, line_webhook_content, flags=re.DOTALL)
        
        if line_webhook_content == updated_line_webhook_content:
            logger.warning("無法在 line_webhook.py 中找到 is_ai_request 函數，或者無法進行修改")
        else:
            with open(line_webhook_file, 'w', encoding='utf-8') as f:
                f.write(updated_line_webhook_content)
            logger.info("已成功更新 line_webhook.py 中的 is_ai_request 函數")
    else:
        logger.warning(f"找不到檔案: {line_webhook_file}")
    
    logger.info("關鍵字檢測修復完成")
    return True

if __name__ == "__main__":
    banner = """
    #########################################################
    #                                                       #
    #              LINE Bot 關鍵字檢測修復工具               #
    #                                                       #
    #########################################################
    
    此工具將修復 app.py 和 src/line_webhook.py 中的
    is_ai_request 函數，確保能夠正確檢測 '小幫手' 和 '花生' 等關鍵字。
    
    修復完成後，您需要重新部署應用程式。
    """
    print(banner)
    input("按下 Enter 鍵開始修復...")
    
    try:
        if apply_fix():
            print("\n✅ 修復成功完成！")
            print("請重新部署應用程式以使變更生效。")
        else:
            print("\n⚠️ 修復過程中出現問題，請查看日誌文件了解詳情。")
    except Exception as e:
        logger.error(f"修復過程中發生錯誤: {str(e)}")
        logger.exception("詳細錯誤:")
        print(f"\n❌ 修復過程中發生錯誤: {str(e)}")
        print("請查看日誌文件了解詳情。")
