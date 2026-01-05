#!/bin/bash
# 部署每日英語功能到 Render

echo "======================================"
echo "部署每日英語功能到 Render"
echo "======================================"

# 檢查 git 狀態
echo ""
echo "1. 檢查 Git 狀態..."
git status

# 添加新文件
echo ""
echo "2. 添加新文件到 Git..."
git add src/daily_english_service.py
git add test_daily_english.py
git add DAILY_ENGLISH_GUIDE.md
git add app.py

# 提交變更
echo ""
echo "3. 提交變更..."
git commit -m "新增每日英語功能 - 365天不重複單字學習"

# 推送到 GitHub
echo ""
echo "4. 推送到 GitHub..."
git push origin main

echo ""
echo "======================================"
echo "✅ 部署完成!"
echo "======================================"
echo ""
echo "請到 Render Dashboard 確認部署狀態:"
echo "https://dashboard.render.com/"
echo ""
echo "部署完成後,在 LINE 輸入以下指令測試:"
echo "- 每日單字"
echo "- 每日英語"
echo "- Daily English"
echo ""
