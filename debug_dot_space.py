#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
特定案例調試腳本 - 處理帶點號和空格前導字符的關鍵字檢測
"""

class Logger:
    def info(self, message):
        print(f"INFO: {message}")

logger = Logger()

def test_case(message):
    """測試特定案例"""
    print(f"\n===== 測試案例: '{message}' =====")
    
    # 去除前後空格
    trimmed_message = message.strip()
    print(f"1. 去除前後空格: '{trimmed_message}'")
    
    # 檢查基本資訊
    print(f"2. 字符串長度: {len(trimmed_message)}")
    print(f"3. 字符編碼: {[ord(c) for c in trimmed_message[:10]]}")
    
    # 檢查前導字符
    first_char = trimmed_message[0]
    print(f"4. 第一個字符: '{first_char}' (ASCII: {ord(first_char)})")
    
    # 允許的前導字符列表
    allowed_prefixes = ['!', '！', ',', '，', '。', '.', '?', '？', ' ', '　', ':', '：', '@', '#', '$', '%', '、', '~', '～']
    print(f"5. 前導字符在允許列表中: {first_char in allowed_prefixes}")
    
    # 檢查第二個字符
    second_char = trimmed_message[1] if len(trimmed_message) > 1 else ''
    print(f"6. 第二個字符: '{second_char}' (ASCII: {ord(second_char) if second_char else 0})")
    print(f"7. 第二個字符是空格: {second_char == ' '}")
    
    # 檢查關鍵字
    keyword = '小幫手'
    rest = trimmed_message[2:] if len(trimmed_message) > 2 else ''
    print(f"8. 空格後的內容: '{rest}'")
    print(f"9. 是否以關鍵字開頭: {rest.startswith(keyword)}")
    
    # 完整條件判斷
    condition1 = len(trimmed_message) > 2
    condition2 = first_char in allowed_prefixes
    condition3 = second_char == ' '
    condition4 = rest.startswith(keyword) if rest else False
    
    print("\n=== 條件判斷 ===")
    print(f"- 長度 > 2: {condition1}")
    print(f"- 前導字符在允許列表中: {condition2}")
    print(f"- 第二個字符是空格: {condition3}")
    print(f"- 剩餘部分以關鍵字開頭: {condition4}")
    print(f"- 所有條件都滿足: {condition1 and condition2 and condition3 and condition4}")

if __name__ == "__main__":
    print("="*60)
    print("特定案例調試 - 帶點號和空格前導字符的關鍵字檢測")
    print("="*60)
    
    # 測試原始問題案例
    test_case(". 小幫手幫我")
    
    # 測試其他的變體
    test_case(".小幫手幫我")  # 沒有空格
    test_case(". 小幫手")     # 只有關鍵字
    test_case("。 小幫手")    # 中文句號
