#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/test_improvements.sh
# 測試 Gemini API 配額限制改進

echo "===== 開始測試 Gemini API 配額限制改進 ====="
echo "當前時間: $(date)"

# 確保工作目錄正確
cd "$(dirname "$0")"
echo "工作目錄: $(pwd)"

# 建立必要的目錄
echo "確保必要目錄存在..."
mkdir -p .cache
mkdir -p logs

# 運行緩存系統測試
echo "測試緩存系統..."
python src/test_quota_limits.py

# 測試 API 使用監控工具
echo "測試 API 使用監控..."
python src/api_usage_monitor.py --simulate

# 檢查健康狀態
echo "檢查健康狀態..."
python -c "import requests; response = requests.get('http://localhost:5000/health'); print(response.json())" 2>/dev/null || echo "應用未運行，跳過健康檢查"

echo "===== 測試完成 ====="
