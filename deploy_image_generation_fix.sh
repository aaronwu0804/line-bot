#!/bin/bash
# 部署圖片生成請求處理修正到 Render 平台

echo "======================================================"
echo "   部署圖片生成請求處理修正到 Render 平台"
echo "======================================================"

# 確保我們在 morning-post 目錄下
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR" || exit 1

echo "[步驟 1] 檢查當前 Git 狀態..."
git status

echo "[步驟 2] 確認最新修正已提交..."
git log --oneline -3

echo "[步驟 3] 推送到 Render 部署分支..."
git push -f origin main
PUSH_STATUS=$?

if [ $PUSH_STATUS -eq 0 ]; then
  echo "✅ 已推送圖片生成處理修正到 Render"
  echo "Render 將自動檢測更改並開始重新部署..."
  echo ""
  echo "📋 本次部署包含："
  echo "- ✅ 圖片生成請求檢測功能"
  echo "- ✅ 友善的功能說明回覆"  
  echo "- ✅ 改善的連續對話日誌"
  echo "- ✅ 處理狀態指示功能"
  echo ""
  echo "你可以訪問 Render 的儀表板來查看部署進度："
  echo "https://dashboard.render.com/"
else
  echo "❌ 推送到 Render 失敗。請檢查 Git 配置和網絡連接。"
  exit 1
fi

echo "[步驟 4] 等待部署完成..."
echo "這可能需要 2-5 分鐘時間..."
echo "部署完成後，圖片生成請求將得到友善回覆而不是被發送到 Gemini API"

# 等待一段時間讓部署開始
sleep 30

echo "[步驟 5] 檢查服務健康狀態..."
SERVICE_URL="https://line-bot-pikj.onrender.com/health"
echo "檢查服務: $SERVICE_URL"

# 檢查健康狀態
for i in {1..5}; do
  echo "嘗試 $i/5..."
  if curl -s -f "$SERVICE_URL" >/dev/null 2>&1; then
    echo "✅ 服務運行正常！"
    break
  else
    echo "⚠️ 服務尚未就緒，等待 30 秒後重試..."
    sleep 30
  fi
done

echo "======================================================"
echo "   部署完成！"
echo "======================================================"
echo ""
echo "🧪 測試建議："
echo "1. 在 LINE 中發送：'花生，生成圖片，貓咪在花園裡玩耍'"
echo "2. 應該收到友善的功能說明回覆，而不是處理中後無回應"
echo "3. 測試正常文字對話：'小幫手，今天天氣如何？'"
echo ""
echo "📊 監控日誌："
echo "- 圖片生成請求應該在日誌中顯示 '檢測到圖片生成請求'"
echo "- 不應該再發送到 Gemini API 進行處理"

exit 0
