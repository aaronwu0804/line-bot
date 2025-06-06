#!/bin/bash
# 簡化的緊急部署腳本

# 顯示腳本開始的通知
echo "================================================"
echo "    LINE Bot 緊急修復部署腳本 - 簡化版"
echo "================================================"

# 設置一些必要的環境變數
export RENDER="true"

# 顯示當前工作目錄和文件
echo "當前工作目錄: $(pwd)"
echo "確認關鍵文件存在:"
ls -la app.py render.yaml requirements.txt

echo "================================================"
echo "驗證app.py是否包含緊急修復代碼..."
if grep -q "緊急修復版" app.py; then
  echo "✅ app.py 已包含緊急修復代碼"
else
  echo "❌ app.py 未包含緊急修復代碼，請確認更新"
  exit 1
fi

echo "驗證render.yaml是否使用直接命令..."
if grep -q "gunicorn app:app" render.yaml; then
  echo "✅ render.yaml 已配置為直接啟動app.py"
else
  echo "❌ render.yaml 未使用直接啟動命令，請確認更新"
  exit 1
fi

echo "================================================"
echo "測試應用在本地的啟動情況..."

# 安裝依賴
echo "安裝依賴項..."
pip install -r requirements.txt

# 在後台啟動應用
echo "在本地啟動應用以進行測試..."
python app.py > app_test.log 2>&1 &
APP_PID=$!
echo "應用已在背景啟動，PID: $APP_PID"

# 等待應用啟動
echo "等待應用啟動..."
sleep 5

# 測試應用
echo "測試應用健康檢查端點..."
curl -s http://localhost:8080/health

# 停止應用
echo "測試完成，關閉本地應用..."
kill $APP_PID

echo "================================================"
echo "應用已準備好部署到Render"
echo ""
echo "請手動執行以下操作:"
echo "1. 登錄到Render控制台: https://dashboard.render.com"
echo "2. 選擇您的LINE Bot服務"
echo "3. 點擊'Manual Deploy'按鈕並選擇'Clear build cache & deploy'"
echo "4. 等待部署完成"
echo ""
echo "部署完成後，您可以運行以下命令測試webhook:"
echo "python src/line_webhook_test.py --url https://line-bot-pikj.onrender.com/callback --text \"AI: 測試訊息\""
echo ""
echo "如果遇到部署超時問題，請考慮使用保活服務:"
echo "python render_keep_alive_ext.py --url https://line-bot-pikj.onrender.com --interval 10"
echo "================================================"
