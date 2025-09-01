#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/deploy_keyword_advanced.sh
# 部署進階關鍵字檢測修復版本至 Render

# 設置顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== 準備部署 LINE Bot 進階關鍵字檢測修復版本 ===${NC}"

# 確保修復腳本有執行權限
chmod +x fix_keyword_advanced.py

# 執行修復腳本
echo -e "${BLUE}執行進階關鍵字檢測修復腳本...${NC}"
python3 fix_keyword_advanced.py

# 檢查 .env 文件
if [ ! -f .env ]; then
    echo -e "${RED}找不到 .env 文件，請先設定環境變數${NC}"
    exit 1
fi

# 從 .env 獲取 RENDER_SERVICE_URL
RENDER_URL=$(grep RENDER_SERVICE_URL .env | cut -d '=' -f 2)

if [ -z "$RENDER_URL" ]; then
    echo -e "${RED}無法從 .env 獲取 RENDER_SERVICE_URL${NC}"
    echo "請手動訪問 Render 控制台重新部署服務。"
    exit 1
fi

echo -e "${GREEN}您的 Render 服務 URL 是: ${RENDER_URL}${NC}"

# 確保腳本有執行權限
chmod +x start_webhook.py
chmod +x scripts/render_build.sh 2>/dev/null || true
chmod +x scripts/render_start.sh 2>/dev/null || true

echo -e "${YELLOW}準備工作完成，需要執行下列步驟重新部署:${NC}"
echo ""
echo "1. 訪問 Render 儀表板: https://dashboard.render.com"
echo "2. 找到您的 LINE Bot 服務"
echo "3. 點擊 \"Manual Deploy\" 按鈕"
echo "4. 選擇 \"Deploy latest commit\""
echo "5. 等待部署完成（通常需要幾分鐘）"
echo ""
echo -e "${YELLOW}服務重新啟動後，您可以測試「小幫手」和「花生」觸發詞。${NC}"

# 詢問是否自動打開瀏覽器
echo -e "${YELLOW}是否自動打開 Render 儀表板? (y/n)${NC}"
read -r OPEN_BROWSER

if [ "$OPEN_BROWSER" = "y" ] || [ "$OPEN_BROWSER" = "Y" ]; then
    echo "嘗試打開 Render 儀表板..."
    if [ "$(uname)" == "Darwin" ]; then
        # macOS
        open https://dashboard.render.com
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
        # Linux
        xdg-open https://dashboard.render.com 2>/dev/null || echo "無法自動打開瀏覽器，請手動訪問 https://dashboard.render.com"
    else
        # Windows
        echo "無法自動打開瀏覽器，請手動訪問 https://dashboard.render.com"
    fi
fi

echo -e "${BLUE}部署後請進行下列測試:${NC}"
echo "1. 發送帶有「小幫手」的訊息，例如：「小幫手，你好」"
echo "2. 發送帶有「花生」的訊息，例如：「花生，幫我查一下這個字怎麼念」"
echo "3. 測試連續對話功能，發送一條訊息後不加關鍵字繼續發送"
echo "4. 測試手動結束對話，發送「結束對話」"
echo ""
echo -e "${GREEN}如有問題，請檢查 Render 日誌中的診斷信息${NC}"
