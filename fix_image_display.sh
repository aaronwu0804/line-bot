#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/fix_image_display.sh
# 修復 LINE Bot 圖片顯示問題

echo "===== 圖片顯示修復版本 ====="
echo "當前時間: $(date)"

# 確保工作目錄正確
cd "$(dirname "$0")"
echo "工作目錄: $(pwd)"

# 顯示 images 目錄中的檔案數量
echo "查看 images 目錄..."
ls -l images | wc -l
echo "發現圖片檔案數量: $(find images -type f -name "*.png" | wc -l)"

# 驗證修改後的網址
echo "測試備用圖片服務..."
python3 -c "
from src.backup_image_service import get_backup_image
url = get_backup_image()
print(f'備用圖片 URL: {url}')
import requests
try:
    r = requests.head(url)
    print(f'URL 狀態碼: {r.status_code}')
except Exception as e:
    print(f'錯誤: {e}')
"

# 提交更改到 git
echo "提交更改到 git..."
git add .
git commit -m "修復: 更新備用圖片 URL 來源，確保 LINE 可以正常顯示圖片 (v2.1.2)"

# 推送到 GitHub
echo "推送到 GitHub..."
git push origin main

echo "===== 圖片顯示修復完成 ====="
echo "請確認 Render 上的自動部署是否啟用"
echo "或使用 Render Dashboard 手動執行部署"
