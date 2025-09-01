#!/bin/bash
# 修復 Render 上的早安貼文服務

echo "========================================================"
echo "   修復 LINE Bot 早安貼文服務"
echo "========================================================"

echo "1. 檢查本地代碼是否有最新更新..."
cd "$(dirname "$0")" || exit 1

# 檢查 git 狀態
git status

echo ""
echo "2. 確保工作目錄乾淨..."
git add .
git commit -m "準備修復 Render 服務: 確保早安貼文正常發送" || true

echo ""
echo "3. 確認時區設置已加入部署配置..."
# 檢查 render.yaml 中是否有時區設定
if ! grep -q "TZ" render.yaml; then
  echo "添加時區設置到 render.yaml..."
  
  # 備份原始文件
  cp render.yaml render.yaml.bak
  
  # 在環境變數部分加入時區設定
  sed -i '' 's/      - key: GEMINI_API_KEY/      - key: GEMINI_API_KEY\n        sync: false  # 手動設定\n      - key: TZ\n        value: "Asia\/Taipei"  # 設置為台北時區/g' render.yaml

  # 驗證更改
  echo "時區設置已添加到 render.yaml"
  grep -A 2 "TZ" render.yaml
fi

echo ""
echo "4. 確認排程日誌已啟用..."
# 檢查 main.py 中的日誌設置
if ! grep -q "schedule.run_pending" src/main.py | grep -q "logger.debug"; then
  echo "添加排程執行日誌到 src/main.py..."
  
  # 備份原始文件
  cp src/main.py src/main.py.bak
  
  # 創建臨時修改文件
  cat > schedule_logging.patch << EOF
    while True:
        pending_jobs = schedule.get_jobs()
        next_run = min([job.next_run for job in pending_jobs]) if pending_jobs else None
        if next_run:
            logger.info(f"等待下次排程執行，下次執行時間: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        schedule.run_pending()
        time.sleep(60)
EOF
  
  # 應用修改
  sed -i '' 's/    while True:\n        schedule.run_pending()\n        time.sleep(60)/'"$(cat schedule_logging.patch)"'/g' src/main.py
  
  rm schedule_logging.patch
  
  echo "已添加排程日誌"
fi

echo ""
echo "5. 確認保活機制已添加..."
# 檢查是否有保活文件
if [ ! -f "keep_render_alive.py" ]; then
  echo "添加保活機制..."
  
  cat > keep_render_alive.py << 'EOF'
#!/usr/bin/env python3
"""
Render 服務保活腳本
每小時發送一次 HTTP 請求到 Render 服務，防止服務因為不活躍而休眠
"""

import os
import time
import logging
import requests
from datetime import datetime
import random

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/keep_alive.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def keep_alive():
    """發送 HTTP 請求到 Render 服務"""
    render_url = os.getenv("RENDER_SERVICE_URL")
    
    if not render_url:
        logger.error("環境變數 RENDER_SERVICE_URL 未設置")
        return False
    
    # 添加健康檢查路徑
    health_url = f"{render_url}/health"
    
    try:
        # 添加隨機參數避免緩存
        random_param = random.randint(1, 1000000)
        response = requests.get(f"{health_url}?r={random_param}", timeout=30)
        
        if response.status_code == 200:
            logger.info(f"保活請求成功: {response.status_code}")
            return True
        else:
            logger.warning(f"保活請求失敗: {response.status_code}")
            return False
    
    except Exception as e:
        logger.error(f"保活請求出錯: {str(e)}")
        return False

def main():
    """主函數"""
    logger.info("啟動 Render 服務保活腳本")
    
    # 每小時發送一次請求
    interval_minutes = 55
    
    while True:
        try:
            current_time = datetime.now()
            logger.info(f"當前時間: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            result = keep_alive()
            logger.info(f"保活結果: {'成功' if result else '失敗'}")
            
            # 記錄下次執行時間
            next_time = current_time.replace(
                minute=(current_time.minute + interval_minutes) % 60,
                second=0
            )
            if next_time.minute < current_time.minute:
                next_time = next_time.replace(hour=(next_time.hour + 1) % 24)
                
            logger.info(f"下次執行時間: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 等待到下次執行時間
            sleep_seconds = (interval_minutes * 60) - (current_time.second)
            logger.info(f"休眠 {sleep_seconds} 秒")
            time.sleep(sleep_seconds)
            
        except Exception as e:
            logger.error(f"執行出錯: {str(e)}")
            # 出錯後休眠 5 分鐘
            logger.info("休眠 5 分鐘後重試")
            time.sleep(300)

if __name__ == "__main__":
    main()
EOF

  # 添加啟動保活機制的命令
  if ! grep -q "keep_render_alive" render.yaml; then
    cp render.yaml render.yaml.bak2
    sed -i '' 's/startCommand: python src\/main.py --schedule-only/startCommand: bash -c "python keep_render_alive.py \& python src\/main.py --schedule-only"/g' render.yaml
    echo "已添加保活機制到 render.yaml"
  fi
fi

echo ""
echo "6. 推送更新到 GitHub..."
git add src/main.py render.yaml keep_render_alive.py
git commit -m "修復: 添加時區設置、排程日誌和保活機制，確保早安貼文正常發送" || true
git push

echo ""
echo "7. 部署到 Render..."
echo "請訪問 Render 儀表板手動重新部署服務:"
echo "https://dashboard.render.com/"
echo ""
echo "重要操作步驟:"
echo "1. 點擊 line-bot-morning-post 服務"
echo "2. 點擊 \"Manual Deploy\" > \"Clear build cache & deploy\""
echo "3. 等待部署完成後，檢查日誌確認是否有 \"排程已啟動：平日 07:00、週末 08:00\" 的訊息"
echo "4. 查看日誌是否顯示正確的下次執行時間"
echo ""

echo "========================================================"
echo "   修復操作完成，請執行上述步驟在 Render 上重新部署服務"
echo "========================================================"
