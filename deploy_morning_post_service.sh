#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/deploy_morning_post_service.sh
# 部署 LINE Bot 早安訊息服務

echo "======================================================"
echo "   部署 LINE Bot 早安訊息服務到 Render 平台"
echo "======================================================"

# 確保我們在 morning-post 目錄下
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR" || exit 1

# 檢查是否有未提交的更改
if [[ $(git status --porcelain) ]]; then
  echo "[步驟 1] 提交本地更改..."
  git add render.yaml
  git commit -m "增加早安訊息服務背景工作者配置"
  echo "✅ 已提交更改"
else
  echo "[步驟 1] 沒有發現需要提交的更改"
fi

# 推送到 Render
echo "[步驟 2] 推送更改到 Render 部署分支..."
git push origin main
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
echo "   部署請求已成功發送！"
echo "======================================================"
echo ""
echo "重要提示："
echo "1. 請登錄 Render 平台儀表板查看部署進度"
echo "2. 確保新工作者服務 'line-bot-morning-post' 已正確創建"
echo "3. 在 Render 儀表板中設置服務的環境變數"
echo "   - LINE_CHANNEL_ACCESS_TOKEN"
echo "   - LINE_USER_ID"
echo "   - CWB_API_KEY"
echo "   - GEMINI_API_KEY"
echo ""
echo "4. 部署完成後，檢查服務日誌以確保定時任務正確運行"
echo ""

# 檢查服務健康狀態
SERVICE_URL="https://line-bot-pikj.onrender.com/health"
echo "檢查 Webhook 服務健康狀態: $SERVICE_URL"
curl -s "$SERVICE_URL" | grep -q "ok"
if [ $? -eq 0 ]; then
  echo "✅ Webhook 服務運行正常！"
else
  echo "⚠️ Webhook 服務可能尚未就緒，請稍後再次檢查。"
fi
