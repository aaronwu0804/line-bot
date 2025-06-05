"""
獲取並更新 LINE Channel Access Token 的工具

這個腳本幫助您:
1. 獲取新的 LINE Channel Access Token
2. 更新 .env 文件
3. 驗證新 token 是否有效
"""

import os
import sys
import re
from dotenv import load_dotenv, set_key

# 載入環境變數
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

def update_line_token():
    """更新 LINE Channel Access Token"""
    print("\n===== LINE Bot Token 更新工具 =====")
    print("\n要獲取新的 LINE Channel Access Token，請按照以下步驟操作：")
    print("\n步驟 1: 登入 LINE Developers Console")
    print("      訪問: https://developers.line.biz/console/")
    
    print("\n步驟 2: 選擇您的 Provider 和 Channel")
    
    print("\n步驟 3: 前往「Messaging API」選項卡")
    
    print("\n步驟 4: 在「Channel access token」區域")
    print("      點擊「Issue」按鈕生成新的 token")
    print("      或查看現有的 token")
    
    print("\n步驟 5: 複製生成的 Channel Access Token")
    
    # 獲取新 token
    print("\n請輸入新的 LINE Channel Access Token:")
    new_token = input().strip()
    
    if not new_token:
        print("錯誤: 未輸入 token，操作取消")
        return
    
    # 檢查 token 格式
    if len(new_token) < 100:
        print(f"警告: 輸入的 token 長度 ({len(new_token)}) 似乎過短，正常應超過 100 字元")
        confirm = input("確定要使用這個 token 嗎? (y/n): ").lower()
        if confirm != 'y':
            print("操作取消")
            return
    
    # 更新 .env 文件
    try:
        # 讀取現有 .env 內容
        with open(env_path, 'r') as file:
            content = file.read()
        
        # 使用正則表達式替換 token
        pattern = r'(LINE_CHANNEL_ACCESS_TOKEN=).*'
        new_content = re.sub(pattern, f'\\1{new_token}', content)
        
        # 寫入新內容
        with open(env_path, 'w') as file:
            file.write(new_content)
            
        print(f"\n成功更新 .env 文件中的 LINE_CHANNEL_ACCESS_TOKEN")
        
        # 建議進行驗證
        print("\n請運行以下命令驗證新 token:")
        print("python src/check_token.py")
        
    except Exception as e:
        print(f"更新 token 時發生錯誤: {str(e)}")

if __name__ == "__main__":
    update_line_token()
