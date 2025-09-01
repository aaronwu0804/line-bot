#!/bin/bash
# 部署最終關鍵字檢測邏輯到 Render 平台

echo "======================================================"
echo "   部署關鍵字檢測邏輯最終修正版到 Render 平台"
echo "======================================================"

# 確保我們在 morning-post 目錄下
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR" || exit 1

# 檢查是否有未提交的更改
if [[ $(git status --porcelain) ]]; then
  echo "[步驟 1] 提交本地更改..."
  git add app.py src/line_webhook.py update_keywords_final_complete.py
  git commit -m "修正關鍵字檢測邏輯：改進點號空格檢測"
  echo "✅ 已提交更改"
else
  echo "[步驟 1] 沒有發現需要提交的更改"
fi

# 推送到 Render
echo "[步驟 2] 推送更改到 Render 部署分支..."
git push -f origin main
PUSH_STATUS=$?

if [ $PUSH_STATUS -eq 0 ]; then
  echo "✅ 已推送更改到 Render"
  echo "Render 將自動檢測更改並開始部署..."
  echo "你可以訪問 Render 的儀表板來查看部署進度。"
else
  echo "❌ 推送到 Render 失敗。請檢查 Git 配置和網絡連接。"
  exit 1
fi

echo "[步驟 3] 等待部署完成..."
echo "這可能需要幾分鐘時間..."
sleep 20

echo "======================================================"
echo "   部署完成！請檢查 Render 平台確認部署狀態"
echo "======================================================"

# 可選: 自動檢查部署健康狀態
SERVICE_URL="https://line-bot-pikj.onrender.com/health"
echo "檢查服務健康狀態: $SERVICE_URL"
curl -s "$SERVICE_URL" | grep -q "ok"
if [ $? -eq 0 ]; then
  echo "✅ 服務運行正常！"
else
  echo "⚠️ 服務可能尚未就緒，請稍後再次檢查。"
fi

exit 0
