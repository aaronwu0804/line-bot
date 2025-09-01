#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/deploy_keyword_fix.sh
# 部署關鍵字檢測修復版本至 Render

# 設置顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== 準備部署 LINE Bot 關鍵字檢測修復版本至 Render ===${NC}"

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
chmod +x fix_keyword_detection.py
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
    open https://dashboard.render.com 2>/dev/null || \
    xdg-open https://dashboard.render.com 2>/dev/null || \
    echo "無法自動打開瀏覽器，請手動訪問 https://dashboard.render.com"
fi

echo ""
echo -e "${YELLOW}完成部署後，您可以使用以下命令測試服務是否正常運行:${NC}"
echo "curl ${RENDER_URL}/health"
echo ""
echo -e "${GREEN}修復說明:${NC}"
echo "1. 已修復 is_ai_request 函數，添加了額外的日誌輸出"
echo "2. 現在 '小幫手' 和 '花生' 關鍵字會被正確識別為 AI 請求"
echo ""
echo -e "${GREEN}完成！${NC}"
