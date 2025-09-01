#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
針對特定案例的更詳細調試，帶有各種不同形式的測試。
"""

def test_space_dot_case(message, debug=True):
    """測試帶點號和空格的案例，更詳細的調試"""
    if debug:
        print(f"\n===== 測試案例: '{message}' =====")
    
    # 去除前後空格
    trimmed_message = message.strip()
    if debug:
        print(f"去除前後空格: '{trimmed_message}'")
        print(f"字符串長度: {len(trimmed_message)}")
        print(f"字符串ASCII: {[ord(c) for c in trimmed_message[:5]]}")
    
    # 檢查前導字符
    if len(trimmed_message) < 2:
        if debug:
            print("字符串太短，至少需要2個字符")
        return False
    
    first_char = trimmed_message[0]
    second_char = trimmed_message[1]
    
    if debug:
        print(f"第一個字符: '{first_char}' (ASCII: {ord(first_char)})")
        print(f"第二個字符: '{second_char}' (ASCII: {ord(second_char)})")
    
    # 允許的前導字符列表
    allowed_prefixes = ['!', '！', ',', '，', '。', '.', '?', '？', ' ', '　', ':', '：', '@', '#', '$', '%', '、', '~', '～']
    
    # 檢查條件1: 第一個字符是否為允許的前導字符
    condition1 = first_char in allowed_prefixes
    if debug:
        print(f"條件1 - 前導字符在允許列表中: {condition1}")
        if not condition1:
            print(f"  前導字符 '{first_char}' 不在允許列表中")
    
    if not condition1:
        return False
    
    # 檢查條件2: 第二個字符是否為空格
    condition2 = second_char == ' '
    if debug:
        print(f"條件2 - 第二個字符是空格: {condition2}")
        if not condition2:
            print(f"  第二個字符 '{second_char}' 不是空格")
    
    if not condition2:
        return False
    
    # 檢查條件3: 剩餘部分是否以關鍵字開頭
    if len(trimmed_message) < 3:
        if debug:
            print("字符串太短，無法檢查關鍵字")
        return False
    
    keyword = "小幫手"
    rest = trimmed_message[2:]
    
    condition3 = rest.startswith(keyword)
    if debug:
        print(f"條件3 - 空格後的內容 '{rest}' 是否以關鍵字 '{keyword}' 開頭: {condition3}")
    
    return condition1 and condition2 and condition3

# 測試不同變體，加倍檢查問題
variants = [
    ". 小幫手幫我",    # 基本案例 - 點號+空格+關鍵字
    ".小幫手幫我",     # 無空格版本
    " . 小幫手幫我",   # 帶前導空格
    ". 小幫手",        # 只有關鍵字，沒有額外內容
    "！ 小幫手",       # 不同的前導字符
    "。 小幫手",       # 中文點號
    "hello",           # 無關案例
]

print("="*60)
print("詳細調試帶點號和空格的關鍵字檢測")
print("="*60)

for idx, case in enumerate(variants):
    result = test_space_dot_case(case)
    print(f"\n結果 {idx+1}: '{case}' -> {result}")

# 額外測試：檢查欄位特殊符號的ASCII值，確保不是顯示問題
print("\n"+"="*60)
print("特殊欄位ASCII值檢查")
print("="*60)

test_str = ". 小幫手"
print(f"測試字符串: '{test_str}'")
print(f"總長度: {len(test_str)}")
print(f"每個字符的ASCII值:")
for i, c in enumerate(test_str):
    print(f"位置 {i}: '{c}' -> ASCII: {ord(c)}")

# 對比檢查，確保函數能正常處理其他案例
print("\n"+"="*60)
print("對比檢查 - 使用已知可工作的案例")
print("="*60)

working_case = "！小幫手"
print(f"已知可工作的案例: '{working_case}'")

# 只檢查前導字符的處理
trimmed = working_case.strip()
first_char = trimmed[0]
allowed_prefixes = ['!', '！', ',', '，', '。', '.', '?', '？', ' ', '　', ':', '：', '@', '#', '$', '%', '、', '~', '～']

print(f"前導字符: '{first_char}'")
print(f"前導字符在允許列表中: {first_char in allowed_prefixes}")
print(f"後續是否為關鍵字: {trimmed[1:].startswith('小幫手')}")

# 檢查ASCII字符範圍
print("\n無顯示字符檢查 (ASCII 0-31):")
for i in range(32):
    if chr(i) in trimmed:
        print(f"發現ASCII {i} 在字符串中!")
