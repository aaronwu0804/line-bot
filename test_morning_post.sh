#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/test_morning_post.sh
# 測試早安訊息發送功能

echo "======================================================"
echo "   測試 LINE Bot 早安訊息發送功能"
echo "======================================================"

# 確保我們在 morning-post 目錄下
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR" || exit 1

echo "[步驟 1] 本地測試早安訊息發送..."
echo "運行 src/main.py 的 --test 模式"
echo "檢查環境變數..."

# 檢查關鍵環境變數
if [ -z "$LINE_CHANNEL_ACCESS_TOKEN" ]; then
  echo "警告: LINE_CHANNEL_ACCESS_TOKEN 環境變數未設置"
fi

if [ -z "$LINE_USER_ID" ]; then
  echo "警告: LINE_USER_ID 環境變數未設置"
fi

if [ -z "$CWB_API_KEY" ]; then
  echo "警告: CWB_API_KEY 環境變數未設置"
fi

if [ -z "$GEMINI_API_KEY" ]; then
  echo "警告: GEMINI_API_KEY 環境變數未設置"
fi

echo "執行測試中，請查看輸出日誌..."
python src/main.py --test 2>&1

echo "[步驟 2] 檢查 Render 平台上的工作者服務..."
echo "請訪問 Render 儀表板，查看 'line-bot-morning-post' 服務的運行狀態和日誌"
echo "儀表板網址: https://dashboard.render.com/"
echo ""
echo "如果服務已運行，您可以檢查日誌以確認排程是否已啟動"
echo "應該能看到類似這樣的日誌: '排程已啟動：平日 07:00、週末 08:00'"
echo ""
echo "如果需要立即在 Render 平台上測試發送功能，可以:"
echo "1. 停止工作者服務"
echo "2. 修改啟動命令為: python src/main.py --test"
echo "3. 重新啟動服務"
echo "4. 查看日誌確認訊息是否成功發送"
echo "5. 完成後記得改回原始啟動命令: python src/main.py"

echo "======================================================"
echo "   測試完成！"
echo "======================================================"
