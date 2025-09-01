#!/bin/bash
# 使用 Render API 重新部署服務

echo "======================================================"
echo "   重新部署 LINE Bot 早安貼文服務"
echo "======================================================"

echo "請訪問 Render 儀表板手動重新部署服務:"
echo "https://dashboard.render.com/"
echo ""
echo "重要操作步驟:"
echo "1. 點擊 line-bot-morning-post 服務"
echo "2. 點擊 \"Manual Deploy\" > \"Clear build cache & deploy\""
echo "3. 等待部署完成後，檢查日誌確認是否有 \"排程已啟動：平日 07:00、週末 08:00\" 的訊息"
echo "4. 查看日誌是否顯示正確的下次執行時間"
echo ""

# 嘗試打開瀏覽器
echo "嘗試打開 Render 儀表板..."
open https://dashboard.render.com/ 2>/dev/null || \
xdg-open https://dashboard.render.com/ 2>/dev/null || \
echo "無法自動打開瀏覽器，請手動訪問 https://dashboard.render.com/"

echo "======================================================"
echo "   部署完成後，請檢查日誌確認服務狀態"
echo "======================================================"
