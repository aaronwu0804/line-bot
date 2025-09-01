#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/restart_render_service.sh
# 重新啟動 Render 服務的腳本

# 設置顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== 重新啟動 LINE Bot 在 Render 上的服務 ===${NC}"

# 檢查 .env 文件中的 RENDER_SERVICE_URL
if [ ! -f .env ]; then
    echo -e "${RED}找不到 .env 文件，無法獲取 RENDER_SERVICE_URL${NC}"
    echo "請手動訪問 Render 控制台重新部署服務。"
    exit 1
fi

# 從 .env 獲取 RENDER_SERVICE_URL
RENDER_URL=$(grep RENDER_SERVICE_URL .env | cut -d '=' -f 2)

if [ -z "$RENDER_URL" ]; then
    echo -e "${RED}無法從 .env 獲取 RENDER_SERVICE_URL${NC}"
    echo "請手動訪問 Render 控制台重新部署服務。"
    echo "或者更新您的 .env 文件，添加正確的 RENDER_SERVICE_URL"
    exit 1
fi

echo -e "${GREEN}您的 Render 服務 URL 是: ${RENDER_URL}${NC}"
echo ""
echo -e "${YELLOW}請執行以下步驟來重新啟動您的服務:${NC}"
echo ""
echo "1. 訪問 Render 儀表板: https://dashboard.render.com"
echo "2. 找到您的 LINE Bot 服務"
echo "3. 點擊 \"Manual Deploy\" 按鈕"
echo "4. 選擇 \"Deploy latest commit\""
echo "5. 等待部署完成（通常需要幾分鐘）"
echo ""
echo -e "${YELLOW}服務重啟後，您可以使用以下命令測試:${NC}"
echo "curl ${RENDER_URL}/health"
echo ""
echo -e "${GREEN}完成以上步驟後，您的修改將應用於 Render 服務${NC}"

# 自動打開 Render 控制台
echo -e "${YELLOW}嘗試打開 Render 儀表板...${NC}"
open https://dashboard.render.com 2>/dev/null || \
xdg-open https://dashboard.render.com 2>/dev/null || \
echo -e "${RED}無法自動打開瀏覽器，請手動訪問 https://dashboard.render.com${NC}"

echo ""
echo -e "${GREEN}完成！${NC}"
