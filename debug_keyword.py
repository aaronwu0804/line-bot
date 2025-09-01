#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
關鍵字檢測問題調試腳本
===================
調試特定案例為什麼沒有被正確識別
"""

# 測試案例
test_case = ". 小幫手幫我"

# 檢查前導字符
print(f"測試案例: '{test_case}'")
print(f"第一個字符: '{test_case[0]}'")  # 應該是 '.'
print(f"第二個字符: '{test_case[1]}'")  # 應該是 ' '
print(f"從第三個字符開始: '{test_case[2:]}'")  # 應該是 '小幫手幫我'

# 模擬函數執行
trimmed_message = test_case.strip()
print(f"\n去除前後空白: '{trimmed_message}'")
print(f"字符數量: {len(trimmed_message)}")

# 檢查前導字符和空格
first_char = trimmed_message[0]
allowed_prefixes = ['!', '！', ',', '，', '。', '.', '?', '？', ' ', '　', ':', '：', '@', '#', '$', '%', '、', '~', '～']
print(f"\n檢查前導字符: '{first_char}'")
print(f"前導字符在允許列表中: {first_char in allowed_prefixes}")

# 檢查前導字符後面是否為空格
has_space = len(trimmed_message) > 1 and trimmed_message[1] == ' '
print(f"前導字符後是否為空格: {has_space}")

# 檢查空格後面是否為關鍵字
keyword = '小幫手'
starts_with_keyword = len(trimmed_message) > 2 and trimmed_message[2:].startswith(keyword)
print(f"空格後是否為關鍵字: {starts_with_keyword}")

# 完整模擬檢測邏輯
print("\n模擬完整檢測邏輯:")
if len(trimmed_message) > 2 and first_char in allowed_prefixes and trimmed_message[1] == ' ':
    if trimmed_message[2:].startswith(keyword):
        print(f"✅ 成功: 檢測到帶前導字符和空格的關鍵字 '{keyword}', 前導字符: '{first_char} '")
    else:
        print(f"❌ 失敗: 空格後不是關鍵字")
else:
    print(f"❌ 失敗: 不符合前導字符+空格+關鍵字的格式")
