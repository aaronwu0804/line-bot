#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/keyword_debug.py
"""
關鍵字檢測診斷工具
用於分析為什麼LINE Bot無法檢測到特定關鍵字
"""

import os
import sys
import logging
import json
from datetime import datetime

# 設置日誌
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, 'keyword_debug.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def debug_message(message):
    """詳細分析消息中的字符和關鍵字"""
    logger.info(f"開始分析消息: '{message}'")
    logger.info(f"消息長度: {len(message)}")
    
    # 分析每個字符
    logger.info("字符分析:")
    for i, char in enumerate(message):
        logger.info(f"  位置 {i}: '{char}' (ASCII/Unicode: {ord(char)})")
    
    # 關鍵字檢測
    keywords = ['小幫手', '花生', 'ai:', 'AI:', '@ai']
    logger.info("關鍵字檢測:")
    for keyword in keywords:
        logger.info(f"  '{keyword}' 在消息中: {keyword in message}")
        
        # 如果關鍵字不在消息中，進一步檢查每個字符
        if keyword not in message and len(keyword) > 1:
            logger.info(f"  進一步分析 '{keyword}':")
            for i, char in enumerate(keyword):
                found = char in message
                logger.info(f"    字符 '{char}' (位置 {i}) 在消息中: {found}")
    
    # 檢測常見問題
    message_lower = message.lower().strip()
    logger.info(f"消息小寫後: '{message_lower}'")
    logger.info(f"消息開頭: '{message[:10]}' (如果足夠長)")

    # 測試關鍵字檢測函數
    is_ai = is_ai_request_test(message)
    logger.info(f"is_ai_request 函數結果: {is_ai}")
    
    return {
        "message": message,
        "length": len(message),
        "chars": [{"position": i, "char": c, "code": ord(c)} for i, c in enumerate(message)],
        "keywords": {keyword: keyword in message for keyword in keywords},
        "is_ai_request": is_ai
    }

def is_ai_request_test(message):
    """測試用的 is_ai_request 函數"""
    if not message:
        return False
    
    logger.info(f"測試 is_ai_request 函數: '{message}'")
    
    message_lower = message.lower().strip()
    # 檢查常見的AI前綴
    if (message_lower.startswith(('ai:', 'ai：')) or 
        message_lower.startswith(('@ai', '@ai ')) or
        message_lower.startswith('ai ') or 
        message_lower == 'ai'):
        logger.info("識別為AI請求: 前綴匹配")
        return True
        
    # 檢查其他觸發關鍵字 (加強檢測)
    if '小幫手' in message:
        logger.info("識別為AI請求: 檢測到'小幫手'關鍵字")
        return True
    if '花生' in message:
        logger.info("識別為AI請求: 檢測到'花生'關鍵字")
        return True
    
    # 嘗試不同編碼方式
    try:
        ascii_message = message.encode('ascii', 'ignore').decode('ascii')
        logger.info(f"ASCII 過濾後: '{ascii_message}'")
    except Exception as e:
        logger.error(f"ASCII 轉換錯誤: {str(e)}")

    try:
        utf8_message = message.encode('utf-8').decode('utf-8')
        logger.info(f"UTF-8 轉換: '{utf8_message}'")
        if '花生' in utf8_message:
            logger.info("UTF-8 轉換後檢測到 '花生'")
    except Exception as e:
        logger.error(f"UTF-8 轉換錯誤: {str(e)}")
    
    # 檢查每個字符是否可能有問題
    for i, c in enumerate(message):
        try:
            if ord(c) > 127:
                logger.info(f"非ASCII字符 at {i}: '{c}' (Unicode: {ord(c)})")
        except Exception as e:
            logger.error(f"字符處理錯誤 at {i}: {str(e)}")
    
    logger.info("訊息未被識別為AI請求")
    return False

def analyze_webhook_event(event_json):
    """分析webhook事件"""
    try:
        data = json.loads(event_json)
        logger.info(f"解析webhook事件: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        # 查找訊息文本
        events = data.get('events', [])
        for event in events:
            if event.get('type') == 'message' and event.get('message', {}).get('type') == 'text':
                message_text = event['message']['text']
                logger.info(f"找到訊息文本: '{message_text}'")
                return debug_message(message_text)
        
        logger.warning("未找到訊息文本")
        return None
    except Exception as e:
        logger.error(f"解析webhook事件時出錯: {str(e)}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("關鍵字檢測診斷工具")
    print("=" * 60)
    
    # 1. 測試一般的訊息
    test_messages = [
        "花生 香蕉的英文是什麼",
        "小幫手 告訴我台北天氣",
        "AI: 幫我寫一首詩",
        "@AI 今天有什麼新聞"
    ]
    
    print("測試常見訊息格式:")
    for msg in test_messages:
        print(f"\n測試訊息: '{msg}'")
        debug_message(msg)
    
    # 2. 分析一個特定的webhook事件
    print("\n\n" + "=" * 60)
    print("分析webhook事件")
    print("=" * 60)
    
    sample_event = """{"destination":"U1f5522466669362a56ddec99d44d134f","events":[{"type":"message","message":{"type":"text","id":"564320775130055022","quoteToken":"Is4BixBCwgjWAbUsm0ghwqSv6jp021gxLmtlwIJkzz_B4MoljnFcnNhv90UkffLlg4UJYtdkpljQWNtT3CSTppxwrTsV7GFY0WEWESyyll1Sl9j7UY83h-yyiU3mRkgcej8_Bp3kmdvoC3P85m3pVw","text":"花生 香蕉的英文是什麼"},"webhookEventId":"01JX204SV8DSEFTZFJZWJWP9YZ","deliveryContext":{"isRedelivery":false},"timestamp":1749192697423,"source":{"type":"user","userId":"Uefa34c50e1d90cbf728a6364c8d453e3"},"replyToken":"6ed821b5a63f42f1991eea6de50fa10c","mode":"active"}]}"""
    
    print(f"分析webhook事件樣本...")
    analyze_webhook_event(sample_event)
    
    # 3. 交互式模式
    print("\n\n" + "=" * 60)
    print("交互式測試")
    print("=" * 60)
    
    choice = input("是否要進入交互式測試模式? (y/n): ")
    if choice.lower() == 'y':
        while True:
            test_message = input("\n請輸入要測試的訊息 (輸入'exit'結束): ")
            if test_message.lower() == 'exit':
                break
            debug_message(test_message)
    
    print("\n診斷完成，結果已記錄在日誌文件中.")
