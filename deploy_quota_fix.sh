#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/deploy_quota_fix.sh
# 部署 Gemini API 配額優化版本到 Render

echo "===== 開始部署 Gemini API 配額優化版本 (v2.1.0) ====="
echo "當前時間: $(date)"

# 確保工作目錄正確
cd "$(dirname "$0")"
echo "工作目錄: $(pwd)"

# 檢查 git 狀態
echo "檢查 git 狀態..."
if ! git diff-index --quiet HEAD --; then
    echo "有未提交的變更。是否繼續? (y/n)"
    read -r response
    if [[ "$response" != "y" ]]; then
        echo "部署已取消"
        exit 1
    fi
fi

# 提交更改到 git
echo "提交更改到 git..."
git add .
git commit -m "配額優化：實現智能緩存和錯誤處理 (v2.1.0)"

# 推送到 GitHub
echo "推送到 GitHub..."
git push origin main

# 使用 curl 觸發 Render 部署
RENDER_SERVICE_URL=${RENDER_SERVICE_URL:-"https://line-bot-pikj.onrender.com"}

echo "觸發 Render 部署..."
echo "服務 URL: $RENDER_SERVICE_URL"

# 開啟瀏覽器訪問 Render Dashboard
echo "正在打開 Render Dashboard..."
open "https://dashboard.render.com/"

echo "===== 部署流程已完成 ====="
echo "請在 Render Dashboard 中手動點擊 'Clear build cache & deploy' 按鈕以確保完全重新部署"
echo "部署完成後，請訪問 $RENDER_SERVICE_URL/health 檢查服務狀態"
