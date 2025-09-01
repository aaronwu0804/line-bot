#!/bin/bash

# LINE Bot 關鍵字位置檢測更新部署腳本
echo "===== 開始部署關鍵字位置檢測更新 ====="
echo "$(date)"

# 1. 更新關鍵字檢測邏輯
echo "正在更新關鍵字檢測邏輯..."
python3 update_keywords.py

# 2. 確認更新成功
if [ $? -ne 0 ]; then
    echo "更新失敗，請檢查日誌檔案。"
    exit 1
fi

# 3. 推送更改到 GitHub
echo "正在推送更改到 GitHub..."
git add app.py src/line_webhook.py
git commit -m "更新關鍵字檢測邏輯: 僅檢測訊息開頭或帶允許前導字符的關鍵字"
git push

# 4. 觸發 Render 重新部署
if [ -z "$RENDER_DEPLOY_HOOK" ]; then
    echo "RENDER_DEPLOY_HOOK 環境變數未設置。請手動重新部署。"
else
    echo "正在觸發 Render 重新部署..."
    curl -X POST $RENDER_DEPLOY_HOOK
fi

echo ""
echo "===== 部署命令已執行 ====="
echo "更新內容:"
echo "1. 修改 is_ai_request 函數，只檢測訊息開頭或帶允許前導字符的關鍵字"
echo "2. 更新 extract_query 函數，適配新的關鍵字檢測邏輯"
echo "3. 改進標點符號處理，支援標點符號+空格+關鍵字的格式"
echo ""
echo "Render 重新部署已觸發，等待 1-2 分鐘生效"
echo "$(date)"
