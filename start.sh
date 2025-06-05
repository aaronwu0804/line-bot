#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/start.sh
# Render啟動腳本，確保啟動正確的應用程式

# 設置顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== LINE Bot 啟動腳本執行 ===${NC}"
echo -e "${GREEN}當前工作目錄: $(pwd)${NC}"
echo -e "${GREEN}目錄內容:${NC}"
ls -la

# 檢查環境變數
echo -e "${GREEN}檢查環境變數:${NC}"
if [ -n "$LINE_CHANNEL_ACCESS_TOKEN" ]; then
  echo -e "${GREEN}LINE_CHANNEL_ACCESS_TOKEN: 已設定${NC}"
else
  echo -e "${RED}LINE_CHANNEL_ACCESS_TOKEN: 未設定${NC}"
fi

if [ -n "$LINE_CHANNEL_SECRET" ]; then
  echo -e "${GREEN}LINE_CHANNEL_SECRET: 已設定${NC}"
else
  echo -e "${RED}LINE_CHANNEL_SECRET: 未設定${NC}"
fi

if [ -n "$GEMINI_API_KEY" ]; then
  echo -e "${GREEN}GEMINI_API_KEY: 已設定${NC}"
else
  echo -e "${RED}GEMINI_API_KEY: 未設定${NC}"
fi

# 確保我們不是在examples目錄中
if [ -d "examples" ]; then
  echo -e "${YELLOW}警告: 檢測到examples目錄，將不使用它${NC}"
fi

# 啟動應用程式
echo -e "${GREEN}啟動 LINE Bot 應用程式...${NC}"
exec gunicorn app:app
