#!/bin/bash

# LINE Bot 關鍵字位置檢測更新部署腳本
echo "===== 開始部署關鍵字位置檢測更新 ====="
echo "$(date)"

# 1. 推送更改到 GitHub
git add app.py src/line_webhook.py
git commit -m "更新關鍵字檢測邏輯: 僅檢測訊息開頭的關鍵字"
git push

# 2. 觸發 Render 重新部署
echo "正在觸發 Render 重新部署..."
curl -X POST $RENDER_DEPLOY_HOOK

echo ""
echo "===== 部署命令已執行 ====="
echo "Render 重新部署已觸發，等待 1-2 分鐘生效"
echo "$(date)"
