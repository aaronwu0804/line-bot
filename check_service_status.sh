#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/check_service_status.sh
# 檢查 LINE Bot 早安訊息服務的狀態

echo "======================================================"
echo "   檢查 LINE Bot 早安訊息服務的狀態"
echo "======================================================"

# 確保我們在 morning-post 目錄下
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR" || exit 1

# 設置顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 檢查最新的日誌並顯示排程狀態
echo -e "${YELLOW}[步驟 1] 檢查本地日誌中的排程狀態...${NC}"
LOGS_DIR="./logs"
if [ -d "$LOGS_DIR" ]; then
  LOG_FILE="$LOGS_DIR/morning_post.log"
  if [ -f "$LOG_FILE" ]; then
    echo "最近的排程日誌記錄:"
    grep -n "排程" "$LOG_FILE" | tail -5
    SCHEDULE_STATUS=$(grep "排程已啟動" "$LOG_FILE" | tail -1)
    if [ -n "$SCHEDULE_STATUS" ]; then
      echo -e "${GREEN}排程狀態: $SCHEDULE_STATUS${NC}"
    else
      echo -e "${RED}警告: 未找到排程啟動記錄${NC}"
    fi
    
    # 檢查最近是否有成功發送消息的記錄
    echo -e "\n最近的訊息發送記錄:"
    grep -n "成功發送早安貼文" "$LOG_FILE" | tail -3
    LAST_SEND=$(grep "成功發送早安貼文" "$LOG_FILE" | tail -1)
    if [ -n "$LAST_SEND" ]; then
      echo -e "${GREEN}最後成功發送: $LAST_SEND${NC}"
    else
      echo -e "${RED}警告: 未找到訊息發送成功記錄${NC}"
    fi
  else
    echo -e "${RED}錯誤: 找不到日誌文件 $LOG_FILE${NC}"
  fi
else
  echo -e "${RED}錯誤: 找不到日誌目錄 $LOGS_DIR${NC}"
fi

echo -e "\n${YELLOW}[步驟 2] Render 平台服務檢查建議${NC}"
echo "請訪問 Render 儀表板，檢查 line-bot-morning-post 服務的狀態:"
echo "1. 網址: https://dashboard.render.com/"
echo "2. 確認服務是否處於「Running」狀態"
echo "3. 查看服務日誌，確認是否有「排程已啟動：平日 07:00、週末 08:00」的記錄"
echo "4. 檢查啟動命令是否為: python src/main.py --schedule-only"
echo ""

echo -e "${YELLOW}[步驟 3] 如何重新啟動服務${NC}"
echo "如果服務未正常運行，可以嘗試以下步驟:"
echo "1. 在 Render 儀表板中，點擊 line-bot-morning-post 服務"
echo "2. 點擊「Manual Deploy」按鈕"
echo "3. 選擇「Clear build cache & deploy」"
echo "4. 等待部署完成，然後檢查日誌確認服務是否正常啟動"
echo "5. 如果仍有問題，可以嘗試編輯環境變數然後重新部署"

echo -e "\n${YELLOW}[步驟 4] 手動測試訊息發送${NC}"
echo "如果需要手動測試訊息發送功能，可運行:"
echo "python src/main.py --test"
echo ""

echo "======================================================"
echo "   檢查完成"
echo "======================================================"
