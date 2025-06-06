#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/fix_gemini_model.sh
# 修復 Gemini 模型選擇和 LINE SDK 圖片參數問題

echo "===== 開始部署 Gemini 模型修復版本 ====="
echo "當前時間: $(date)"

# 確保工作目錄正確
cd "$(dirname "$0")"
echo "工作目錄: $(pwd)"

# 提交更改到 git
echo "提交更改到 git..."
git add .
git commit -m "修復: 更新 Gemini 模型優先順序和 LINE SDK 圖片參數 (v2.1.1)"

# 推送到 GitHub
echo "推送到 GitHub..."
git push origin main

echo "===== 更改已提交，正在部署到 Render ====="
echo "請確認 Render 上的自動部署是否啟用"
echo "或使用 Render Dashboard 手動執行部署"
echo "* 更新的更改:"
echo "  1. 更新了 Gemini 模型優先順序，優先使用免費模型"
echo "  2. 修復了 LINE SDK v3 的圖片參數問題"
echo "  3. 增強了錯誤處理機制"

# 執行一次測試，驗證改動
echo "===== 執行測試以驗證改動 ====="
if [ -f ".env" ]; then
    echo "使用本地環境變數執行測試..."
    python src/main.py --test
    echo "測試完成，請檢查日誌確認功能是否正常"
else
    echo "未找到 .env 檔案，跳過本地測試"
    echo "部署後請在 Render 平台上檢查日誌"
fi

echo "===== 修復部署完成 ====="
