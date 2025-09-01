#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
簡單測試「. 小幫手」案例
"""

# 直接測試
message = ". 小幫手幫我"
trimmed_message = message.strip()

print(f"原始訊息: '{message}'")
print(f"去除前後空格: '{trimmed_message}'")

# 檢查點號
first_char = trimmed_message[0]
print(f"第一個字符: '{first_char}'")
print(f"是否為點號: {first_char == '.'}")

# 檢查空格
second_char = trimmed_message[1] if len(trimmed_message) > 1 else ''
print(f"第二個字符: '{second_char}'")
print(f"是否為空格: {second_char == ' '}")

# 檢查關鍵字
keyword = "小幫手"
rest = trimmed_message[2:] if len(trimmed_message) > 2 else ''
print(f"後續內容: '{rest}'")
print(f"是否以關鍵字開頭: {rest.startswith(keyword)}")

# 綜合檢查
is_valid = (first_char == '.') and (second_char == ' ') and rest.startswith(keyword)
print(f"\n綜合檢查結果: {is_valid}")
