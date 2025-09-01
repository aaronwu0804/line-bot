#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/deploy_render_fix.sh
# 部署 Render 專用關鍵字檢測修復

# 設置顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== 部署 Render 專用關鍵字檢測修復 ===${NC}"
echo -e "${BLUE}此版本專為 Render 平台優化，解決關鍵字檢測問題${NC}"

# 執行修復腳本
echo -e "${PURPLE}執行 Render 專用修復腳本...${NC}"
chmod +x render_keyword_fix.py
python3 render_keyword_fix.py

# 檢查 git 狀態
echo -e "${BLUE}檢查代碼變更...${NC}"
git status

# 提交變更到 git
echo -e "${PURPLE}是否要提交當前變更? (y/n)${NC}"
read -r COMMIT_CHANGES

if [ "$COMMIT_CHANGES" = "y" ] || [ "$COMMIT_CHANGES" = "Y" ]; then
    echo -e "${BLUE}提交代碼變更...${NC}"
    git add app.py src/line_webhook.py render_keyword_fix.py
    git commit -m "添加 Render 專用關鍵字檢測修復"
    echo -e "${GREEN}代碼變更已提交${NC}"
fi

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

echo -e "${YELLOW}準備工作完成，請執行下列步驟重新部署:${NC}"
echo ""
echo -e "1. 訪問 ${PURPLE}Render 儀表板: https://dashboard.render.com${NC}"
echo "2. 找到您的 LINE Bot 服務"
echo "3. 點擊 \"Manual Deploy\" 按鈕"
echo "4. 選擇 \"Deploy latest commit\""
echo "5. 等待部署完成（通常需要幾分鐘）"
echo ""

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

echo -e "${BLUE}部署後查看 Render 日誌，特別關注 [RENDER-FIX] 標記的日誌${NC}"
echo -e "${BLUE}這些日誌將幫助我們診斷關鍵字檢測的具體問題${NC}"
echo ""
echo -e "${GREEN}部署後請測試:${NC}"
echo "1. 發送「花生 香蕉的英文是什麼」"
echo "2. 檢查 Render 日誌中的 [RENDER-FIX] 標記"
echo "3. 確認關鍵字檢測是否生效"
