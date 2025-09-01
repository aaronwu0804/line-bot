#!/usr/bin/env bash
# filepath: /Users/al02451008/Documents/code/morning-post/deploy_image_fix.sh
# 部署備用圖片修正到 Render 平台

echo "======================================================"
echo "   部署備用圖片修正到 Render 平台"
echo "======================================================"

# 確保我們在正確的目錄
cd "$(dirname "$0")" || exit 1
REPO_DIR=$(pwd)

echo "[步驟 1] 確認 Git 存儲庫狀態..."
if [ ! -d ".git" ]; then
  echo "錯誤：當前目錄不是 Git 存儲庫。請確保在專案根目錄運行此腳本。"
  exit 1
fi

# 檢查當前分支
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "當前分支: $CURRENT_BRANCH"

# 檢查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
  echo "檢測到未提交的更改，即將提交..."
  
  # 提交更改
  git add src/backup_image_service.py src/test_pinterest.py
  git commit -m "修復：更新圖片資源為含有早安文字的Pinterest和Pixabay圖片，優先使用帶有早安文字的圖片"
  echo "成功提交更改"
else
  echo "沒有檢測到未提交的更改，跳過提交步驟"
fi

echo "[步驟 2] 推送更改到遠端存儲庫..."
git push origin $CURRENT_BRANCH

if [ $? -eq 0 ]; then
  echo "成功推送到遠端存儲庫"
else
  echo "錯誤：無法推送到遠端存儲庫。請檢查您的權限和網絡連接。"
  exit 1
fi

echo "[步驟 3] 等待 Render 自動部署更新..."
echo "根據 render.yaml 配置，Render 平台應該會自動檢測更改並重新部署服務。"
echo "請前往 Render 儀表板查看部署狀態: https://dashboard.render.com/"

echo "[步驟 4] 部署完成後建議監控日誌..."
echo "請在 Render 儀表板上查看以下服務的日誌:"
echo "1. line-bot-webhook - 確保 webhook 服務正常運行"
echo "2. line-bot-morning-post - 確保早安貼文工作者服務正常運行"
echo
echo "尤其請留意備用圖片的使用情況，確認圖片 URL 能夠被正確訪問"
echo 
echo "[步驟 5] 部署後測試"
echo "如需手動觸發早安貼文服務測試，執行以下步驟:"
echo "1. 在 Render 儀表板中，修改 line-bot-morning-post 服務的啟動命令為: python src/main.py --test"
echo "2. 重啟服務，等待執行完成"
echo "3. 檢查日誌確認訊息發送是否成功"
echo "4. 完成後將啟動命令改回: python src/main.py"

echo "======================================================"
echo "   部署腳本執行完畢！"
echo "======================================================"
