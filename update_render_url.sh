#!/bin/bash
# 更新 Render 服務 URL

# 以防萬一，確保腳本具有可執行權限
chmod +x ./deploy_to_render.sh
chmod +x ./src/line_webhook.py
chmod +x ./render_app.py

# 定義 Render 服務 URL
RENDER_URL="https://line-bot-python-flask-pulo.onrender.com"
WEBHOOK_PATH="/callback"
FULL_WEBHOOK_URL="$RENDER_URL$WEBHOOK_PATH"

echo "準備更新 Webhook URL 設定..."
echo "Render 服務 URL: $RENDER_URL"
echo "完整 Webhook URL: $FULL_WEBHOOK_URL"

# 檢查是否存在 .env 文件
if [ -f ./.env ]; then
    echo "更新 .env 檔案中的 RENDER_SERVICE_URL..."
    
    # 檢查是否已存在 RENDER_SERVICE_URL
    if grep -q "RENDER_SERVICE_URL" ./.env; then
        # 更新現有的 RENDER_SERVICE_URL
        sed -i '' "s|RENDER_SERVICE_URL=.*|RENDER_SERVICE_URL=$RENDER_URL|" ./.env
    else
        # 添加新的 RENDER_SERVICE_URL
        echo "RENDER_SERVICE_URL=$RENDER_URL" >> ./.env
    fi
    
    echo "RENDER_SERVICE_URL 已更新！"
else
    echo "警告: 未找到 .env 檔案，正在創建..."
    echo "RENDER_SERVICE_URL=$RENDER_URL" > ./.env
    echo ".env 檔案已創建！"
fi

echo "==================================================="
echo "✅ URL 更新成功！"
echo "==================================================="
echo "現在您需要執行以下步驟:"
echo ""
echo "1. 將代碼提交到 Git 儲存庫（如果使用的話）"
echo "   git add ."
echo "   git commit -m \"更新 Webhook URL 配置\""
echo "   git push"
echo ""
echo "2. 部署到 Render 平台"
echo "   ./deploy_to_render.sh"
echo ""
echo "3. 在 LINE Developers Console 中設定 Webhook URL:"
echo "   $FULL_WEBHOOK_URL"
echo ""
echo "4. 點選「Verify」按鈕驗證 Webhook 連接"
echo "==================================================="
