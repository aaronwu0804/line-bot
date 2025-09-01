#!/bin/bash
# 監控 Render 部署狀態和圖片生成檢測功能

echo "======================================================"
echo "   監控 Render 部署狀態"
echo "======================================================"

SERVICE_URL="https://line-bot-pikj.onrender.com"
HEALTH_URL="$SERVICE_URL/health"

echo "⏱️ 等待 Render 重新部署..."
echo "通常需要 2-5 分鐘時間"
echo ""

# 監控部署狀態
for i in {1..20}; do
  echo "[$i/20] 檢查服務狀態..."
  
  # 檢查健康狀態
  if response=$(curl -s -f "$HEALTH_URL"); then
    echo "✅ 服務響應正常"
    
    # 檢查版本或時間戳變化
    timestamp=$(echo "$response" | grep -o '"timestamp":"[^"]*"' | cut -d'"' -f4)
    echo "🕒 服務時間戳: $timestamp"
    
    # 檢查是否包含更新的內容
    if echo "$response" | grep -q "Smart Response\|Image Generation\|2\."; then
      echo "🎯 檢測到更新版本的服務"
      break
    else
      echo "⚠️ 服務可能尚未更新到最新版本"
    fi
  else
    echo "❌ 服務無法訪問或正在重啟"
  fi
  
  if [ $i -lt 20 ]; then
    echo "等待 30 秒後重試..."
    sleep 30
  fi
done

echo ""
echo "======================================================"
echo "   部署監控完成"
echo "======================================================"
echo ""
echo "🧪 測試指南："
echo ""
echo "1. 測試圖片生成請求檢測："
echo "   發送：'花生，生成圖片，一群小孩在打棒球'"
echo "   期望：立即收到友善的功能說明回覆"
echo "   不應該：看到'讓我想想...'後沒有回應"
echo ""
echo "2. 測試正常對話："
echo "   發送：'小幫手，今天天氣如何？'"
echo "   期望：正常的處理狀態指示和 AI 回應"
echo ""
echo "3. 測試連續對話："
echo "   第一句：'花生，你好'"
echo "   第二句：'還有其他功能嗎？'（不需要加關鍵字）"
echo "   期望：兩句都能正常回應"
echo ""
echo "📊 日誌監控重點："
echo "- 應該看到：'檢測到圖片生成請求'"
echo "- 不應該看到：圖片生成請求被發送到 Gemini API"
echo "- 應該看到：'識別為 AI 請求'"
echo ""
echo "如果問題仍然存在，可能需要："
echo "1. 檢查 Render 控制台的部署日誌"
echo "2. 確認 webhook URL 指向正確的服務"
echo "3. 檢查 LINE Bot 設定"

exit 0
