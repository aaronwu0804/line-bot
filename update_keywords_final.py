#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
更新關鍵字檢測邏輯 - 最終版本
===========================

該腳本用於更新 app.py 和 src/line_webhook.py 中的 is_ai_request 和 extract_query 函數。
修改內容：嚴格限制僅檢測訊息開頭或帶有允許前導字符的關鍵字，避免句中關鍵字被誤判。
移除 "前3個字符內" 的寬松條件。
"""

import re
import os
import sys
import logging
from datetime import datetime

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger()

def update_app_py():
    """更新 app.py 中的 is_ai_request 函數"""
    logger.info("開始更新 app.py 中的 is_ai_request 函數")
    
    app_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
    
    # 讀取文件內容
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 備份原文件
    backup_file = f"{app_file}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"已備份 app.py 至 {backup_file}")
    
    # 新的 is_ai_request 函數實現
    new_function = '''def is_ai_request(message):
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
            
        # 前導字符+空格的情況 (如 ". 花生")
        elif trimmed_message[1] == ' ' and len(trimmed_message) > 3:
            if trimmed_message[2] == flower_char and trimmed_message[3] == life_char:
                logger.info(f"識別為AI請求: 通過字符級別檢測到帶前導字符和空格的 '花生' 關鍵字")
                return True
    
    # 所有檢查都未通過
    logger.info("非AI請求: 未檢測到句首或帶允許前導字符的觸發關鍵字")
    return False'''
    
    # 使用正則表達式找到原始的 is_ai_request 函數並替換它
    pattern = r'def is_ai_request\(message\):.*?return False'
    replacement = new_function
    
    # 使用正則表達式來匹配並替換整個函數
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if updated_content == content:
        logger.error("無法在 app.py 中找到並替換 is_ai_request 函數")
        return False
    
    # 寫入更新後的內容
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    logger.info("已成功更新 app.py 中的 is_ai_request 函數")
    return True

def update_line_webhook_py():
    """更新 src/line_webhook.py 中的 is_ai_request 和 extract_query 函數"""
    logger.info("開始更新 src/line_webhook.py 中的 is_ai_request 函數")
    
    webhook_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "line_webhook.py")
    
    # 讀取文件內容
    with open(webhook_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 備份原文件
    backup_file = f"{webhook_file}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"已備份 line_webhook.py 至 {backup_file}")
    
    # 更新 is_ai_request 函數
    new_is_function = '''def is_ai_request(message):
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
            if len(trimmed_message) > 2 and first_char in allowed_prefixes and trimmed_message[1] == ' ':
                if trimmed_message[2:].startswith(keyword):
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
            if trimmed_message[2] == flower_char and trimmed_message[3] == life_char:
                logger.info(f"識別為AI請求: 通過字符級別檢測到帶前導字符和空格的 '花生' 關鍵字")
                return True
    
    # 所有檢查都未通過
    logger.info("非AI請求: 未檢測到句首或帶允許前導字符的觸發關鍵字")
    return False'''
    
    # 使用正則表達式找到原始的 is_ai_request 函數並替換它
    is_pattern = r'def is_ai_request\(message\):.*?return False'
    updated_content = re.sub(is_pattern, new_is_function, content, flags=re.DOTALL)
    
    if updated_content == content:
        logger.error("無法在 line_webhook.py 中找到並替換 is_ai_request 函數")
        return False
    
    # 更新 extract_query 函數
    new_extract_function = '''def extract_query(message):
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
            if message[2] == flower_char and message[3] == life_char:
                return message[4:].strip()
    
    # 如果沒有找到關鍵字或無法提取，則使用整個訊息
    return message'''
    
    # 使用正則表達式找到原始的 extract_query 函數並替換它
    extract_pattern = r'def extract_query\(message\):.*?return message'
    updated_content = re.sub(extract_pattern, new_extract_function, updated_content, flags=re.DOTALL)
    
    if content == updated_content:
        logger.error("無法在 line_webhook.py 中找到並替換函數")
        return False
    
    # 寫入更新後的內容
    with open(webhook_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    logger.info("已成功更新 line_webhook.py 中的函數")
    return True

def run_tests():
    """運行測試以驗證更新是否成功"""
    logger.info("運行測試腳本...")
    
    test_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_keyword_final.py")
    
    import subprocess
    try:
        result = subprocess.run([sys.executable, test_script], capture_output=True, text=True)
        logger.info(f"測試輸出:\n{result.stdout}")
        if result.stderr:
            logger.error(f"測試錯誤:\n{result.stderr}")
        
        # 檢查測試是否通過
        if "測試通過" in result.stdout and "失敗" not in result.stdout:
            logger.info("所有測試都通過了！")
            return True
        else:
            logger.warning("測試中有失敗的案例，請檢查輸出。")
            return False
    except Exception as e:
        logger.error(f"運行測試時出錯: {str(e)}")
        return False

def main():
    """主函數"""
    logger.info("開始執行關鍵字檢測邏輯更新 (最終版本)")
    
    # 更新 app.py
    app_updated = update_app_py()
    if not app_updated:
        logger.error("更新 app.py 失敗")
        sys.exit(1)
    
    # 更新 line_webhook.py
    webhook_updated = update_line_webhook_py()
    if not webhook_updated:
        logger.error("更新 line_webhook.py 失敗")
        sys.exit(1)
    
    logger.info("所有文件已成功更新")
    
    # 運行測試
    tests_passed = run_tests()
    
    if tests_passed:
        logger.info("PASS: 所有關鍵字檢測邏輯測試都通過！")
        logger.info("更新完成。請使用 deploy_final_fix.sh 部署至 Render 平台。")
    else:
        logger.error("FAIL: 有測試未通過，請檢查上面的輸出並修復問題。")
        sys.exit(1)

if __name__ == "__main__":
    main()
