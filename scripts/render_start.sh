#!/bin/bash
# Render平台啟動腳本 (緊急修復版)

echo "=== 啟動 LINE Bot Webhook 服務 (緊急修復版) ==="
echo "當前目錄: $(pwd)"
echo "文件列表:"
ls -la

# 檢查環境變數
echo "檢查關鍵環境變數:"
if [ -n "$LINE_CHANNEL_ACCESS_TOKEN" ]; then
  echo "LINE_CHANNEL_ACCESS_TOKEN: 已設定"
else
  echo "警告: LINE_CHANNEL_ACCESS_TOKEN 未設定"
fi

if [ -n "$LINE_CHANNEL_SECRET" ]; then
  echo "LINE_CHANNEL_SECRET: 已設定"
else
  echo "警告: LINE_CHANNEL_SECRET 未設定"
fi

if [ -n "$GEMINI_API_KEY" ]; then
  echo "GEMINI_API_KEY: 已設定"
else
  echo "警告: GEMINI_API_KEY 未設定"
fi

# 使用緊急修復腳本而不是app.py
echo "使用緊急修復腳本..."
if [ -f "emergency_fix.py" ]; then
  echo "找到 emergency_fix.py:"
  head -n 10 emergency_fix.py
  # 直接從緊急修復腳本啟動
  echo "從緊急修復腳本啟動應用程序..."
  exec gunicorn emergency_fix:app
else
  echo "錯誤: 找不到 emergency_fix.py 文件"
  exit 1
fi
