#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/restart_simple.sh
# 簡化版重新啟動 Render 服務的腳本

echo "=== 重新啟動 LINE Bot 在 Render 上的服務 ==="

# 檢查 .env 文件中的 RENDER_SERVICE_URL
if [ ! -f .env ]; then
    echo "找不到 .env 文件，無法獲取 RENDER_SERVICE_URL"
    echo "請手動訪問 Render 控制台重新部署服務。"
    exit 1
fi

# 從 .env 獲取 RENDER_SERVICE_URL
RENDER_URL=$(grep RENDER_SERVICE_URL .env | cut -d '=' -f 2)

if [ -z "$RENDER_URL" ]; then
    echo "無法從 .env 獲取 RENDER_SERVICE_URL"
    echo "請手動訪問 Render 控制台重新部署服務。"
    echo "或者更新您的 .env 文件，添加正確的 RENDER_SERVICE_URL"
    exit 1
fi

echo "您的 Render 服務 URL 是: ${RENDER_URL}"
echo ""
echo "請執行以下步驟來重新啟動您的服務:"
echo ""
echo "1. 訪問 Render 儀表板: https://dashboard.render.com"
echo "2. 找到您的 LINE Bot 服務"
echo "3. 點擊 \"Manual Deploy\" 按鈕"
echo "4. 選擇 \"Deploy latest commit\""
echo "5. 等待部署完成（通常需要幾分鐘）"
echo ""
echo "服務重啟後，您可以使用以下命令測試:"
echo "curl ${RENDER_URL}/health"
echo ""
echo "完成以上步驟後，您的修改將應用於 Render 服務"

# 詢問是否自動打開瀏覽器
echo "是否自動打開 Render 儀表板? (y/n)"
read -r OPEN_BROWSER

if [ "$OPEN_BROWSER" = "y" ] || [ "$OPEN_BROWSER" = "Y" ]; then
    echo "嘗試打開 Render 儀表板..."
    open https://dashboard.render.com 2>/dev/null || \
    xdg-open https://dashboard.render.com 2>/dev/null || \
    echo "無法自動打開瀏覽器，請手動訪問 https://dashboard.render.com"
fi

echo ""
echo "完成！"
