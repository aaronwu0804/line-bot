#!/bin/bash
# 全面驗證 Gemini 2.5 Flash 和圖片生成修正

echo "🚀 驗證 Gemini 2.5 Flash 和圖片生成修正"
echo "=" * 60

SERVICE_URL="https://line-bot-pikj.onrender.com"

# 1. 等待部署完成
echo "⏱️ [步驟 1] 等待 Render 重新部署..."
for i in {1..10}; do
  echo "等待部署完成... $i/10"
  sleep 30
  
  if response=$(curl -s -f "$SERVICE_URL/health"); then
    timestamp=$(echo "$response" | grep -o '"timestamp":"[^"]*"' | cut -d'"' -f4)
    echo "✅ 服務響應正常，時間戳: $timestamp"
    break
  else
    echo "⚠️ 服務可能正在重啟..."
  fi
done

# 2. 檢查模型版本
echo ""
echo "🔍 [步驟 2] 檢查可用的 Gemini 模型..."
if response=$(curl -s "$SERVICE_URL/health"); then
  if echo "$response" | grep -q "gemini-2.5-flash"; then
    echo "✅ Gemini 2.5 Flash 可用"
  else
    echo "❌ Gemini 2.5 Flash 不可用"
  fi
  
  if echo "$response" | grep -q "gemini-2.5-pro"; then
    echo "✅ Gemini 2.5 Pro 可用"
  else
    echo "❌ Gemini 2.5 Pro 不可用"
  fi
  
  model_count=$(echo "$response" | grep -o '"model_count":[0-9]*' | cut -d':' -f2)
  echo "📊 總共可用模型數量: $model_count"
else
  echo "❌ 無法獲取健康狀態"
fi

# 3. 嘗試清除緩存
echo ""
echo "🗑️ [步驟 3] 清除圖片生成緩存..."
if clear_response=$(curl -s -X POST "$SERVICE_URL/clear_cache"); then
  echo "✅ 清除緩存請求成功"
  echo "$clear_response" | grep -o '"cleared_count":[0-9]*' | cut -d':' -f2 | sed 's/^/已清除 /' | sed 's/$/ 個緩存項目/'
else
  echo "⚠️ 清除緩存請求失敗或端點不可用"
fi

# 4. 檢查緩存狀態
echo ""
echo "📊 [步驟 4] 檢查當前緩存狀態..."
if response=$(curl -s "$SERVICE_URL/health"); then
  # 檢查是否還有圖片生成相關緩存
  if echo "$response" | grep -q "生成圖片"; then
    echo "⚠️ 仍存在圖片生成相關緩存"
    echo "$response" | grep -o '"prompt":"[^"]*生成圖片[^"]*"' | head -3
  else
    echo "✅ 沒有發現圖片生成相關緩存"
  fi
  
  cache_files=$(echo "$response" | grep -o '"files":[0-9]*' | cut -d':' -f2)
  echo "📁 當前緩存文件數量: $cache_files"
fi

# 5. 驗證修正版本
echo ""
echo "🔧 [步驟 5] 驗證修正版本..."
git_commit=$(git log --oneline -1 | cut -d' ' -f1)
echo "📝 本地最新提交: $git_commit"

echo ""
echo "=" * 60
echo "🧪 測試建議："
echo ""
echo "1. 測試 Gemini 2.5 Flash 使用："
echo "   發送：'小幫手，介紹一下台灣的夜市文化'"
echo "   期望：日誌顯示使用 gemini-2.5-flash 模型"
echo ""
echo "2. 測試圖片生成檢測："
echo "   發送：'花生，生成圖片，貓咪在花園裡玩耍'"
echo "   期望：立即收到功能說明回覆"
echo "   不應該：看到 Gemini API 調用日誌"
echo ""
echo "3. 測試連續對話："
echo "   第一句：'花生，你好'"
echo "   第二句：'台灣有什麼著名景點？'"
echo "   期望：兩句都正常回應"
echo ""
echo "📊 監控要點："
echo "- 模型選擇日誌應顯示：gemini-2.5-flash"
echo "- 圖片生成請求應顯示：'檢測到圖片生成請求'"
echo "- 不應該有：'回應已保存到緩存' 針對圖片生成請求"

exit 0
