#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LINE Bot 關鍵字位置檢測測試工具 (最終版)
================================================

此工具測試 is_ai_request 函數對於不同位置的關鍵字的行為。
用於確認只有訊息開頭或帶有允許的前導字符的關鍵字才能觸發AI回應。
"""

import logging

# 模擬 logger
class Logger:
    def info(self, message):
        print(f"INFO: {message}")
    def error(self, message):
        print(f"ERROR: {message}")

logger = Logger()

def is_ai_request(message):
    """檢查是否為AI請求 (最終版: 僅檢測訊息開頭或帶允許前導字符的關鍵字)"""
    if not message:
        return False
    
    # 添加日誌以查看接收到的確切訊息
    logger.info(f"檢測訊息是否為AI請求: '{message}'")
    
    # 去除前後空格，便於檢查句首關鍵字
    trimmed_message = message.strip()
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
            if len(trimmed_message) > 2 and first_char in allowed_prefixes:
                # 特殊處理點號+空格情況
                if first_char == '.' and trimmed_message[1] == ' ' and trimmed_message[2:].startswith(keyword):
                    logger.info(f"識別為AI請求: 檢測到特殊點號和空格前導的關鍵字 '{keyword}'")
                    return True
                
                # 正常處理其他前導字符+空格情況
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
            if trimmed_message[2] == flower_char and trimmed_message[3] == life_char:
                logger.info(f"識別為AI請求: 通過字符級別檢測到帶前導字符和空格的 '花生' 關鍵字")
                return True
    
    # 所有檢查都未通過
    logger.info("非AI請求: 未檢測到句首或帶允許前導字符的觸發關鍵字")
    return False

def test_is_ai_request():
    """測試不同位置的關鍵字是否觸發 AI 回應"""
    test_cases = [
        # 1. 開頭關鍵字 (應該觸發)
        {"message": "小幫手你好", "expected": True, "desc": "開頭關鍵字"},
        {"message": "花生請告訴我", "expected": True, "desc": "開頭關鍵字"},
        {"message": "AI: 請問", "expected": True, "desc": "開頭關鍵字"},
        {"message": "ai：你好", "expected": True, "desc": "開頭關鍵字"},
        {"message": "@AI 幫我", "expected": True, "desc": "開頭關鍵字"},
        
        # 2. 帶允許的前導字符的關鍵字 (應該觸發)
        {"message": "！小幫手你好", "expected": True, "desc": "帶標點前導字符的關鍵字"},
        {"message": "，花生請回答", "expected": True, "desc": "帶標點前導字符的關鍵字"},
        {"message": ". 小幫手幫我", "expected": True, "desc": "帶點號和空格前導字符的關鍵字"},
        {"message": "？花生告訴我", "expected": True, "desc": "帶問號前導字符的關鍵字"},
        {"message": " 小幫手，請問", "expected": True, "desc": "帶空格前導字符的關鍵字"},
        
        # 3. 中間或結尾的關鍵字 (不應該觸發)
        {"message": "請問這個小幫手怎麼用", "expected": False, "desc": "中間關鍵字"},
        {"message": "我想了解一下花生的功能", "expected": False, "desc": "中間關鍵字"},
        {"message": "我想要一個小幫手", "expected": False, "desc": "結尾關鍵字"},
        {"message": "可以給我花生嗎", "expected": False, "desc": "結尾關鍵字"},
        {"message": "好像小幫手可以回答這個", "expected": False, "desc": "中間關鍵字"},
        
        # 4. 多個字符前導後的關鍵字 (不應該觸發)
        {"message": "你好啊，小幫手幫我", "expected": False, "desc": "多字符前導後的關鍵字"},
        {"message": "請問一下花生可以回答嗎", "expected": False, "desc": "多字符前導後的關鍵字"},
        {"message": "最近天氣如何，小幫手", "expected": False, "desc": "中間關鍵字"}
    ]
    
    # 執行測試
    print("=" * 60)
    print("開始測試最終版的 is_ai_request 函數")
    print("=" * 60)
    
    success = 0
    for idx, case in enumerate(test_cases):
        result = is_ai_request(case["message"])
        match = result == case["expected"]
        status = "✅ 通過" if match else "❌ 失敗"
        
        if match:
            success += 1
        
        print(f"{idx+1}. {status} - {case['desc']}: '{case['message']}' -> 預期: {case['expected']}, 實際: {result}")
    
    print(f"\n結果: {success}/{len(test_cases)} 測試通過 ({success/len(test_cases)*100:.0f}%)")
    print("=" * 60)

if __name__ == "__main__":
    print("""
    #########################################################
    #                                                       #
    #       LINE Bot 關鍵字位置檢測測試工具 (最終版)          #
    #                                                       #
    #########################################################
    """)
    
    test_is_ai_request()
