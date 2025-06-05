#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/build.sh
# Render構建腳本，確保使用正確的應用程式

# 設置顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== LINE Bot 構建腳本開始 ===${NC}"

# 確保不在examples目錄中
if [ -d "examples" ]; then
  echo -e "${YELLOW}警告: 檢測到examples目錄，正在移除...${NC}"
  rm -rf examples
fi

# 顯示當前工作目錄
echo -e "${GREEN}當前工作目錄: $(pwd)${NC}"
echo -e "${GREEN}目錄內容:${NC}"
ls -la

# 安裝依賴
echo -e "${GREEN}安裝Python依賴...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}=== LINE Bot 構建腳本完成 ===${NC}"
