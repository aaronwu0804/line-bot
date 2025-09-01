#!/bin/bash
# 清理不需要的測試檔案

# 保留的測試檔案列表
KEEP=(
  "/Users/al02451008/Documents/code/morning-post/src/test_pinterest.py"          # 修改後的圖片下載功能
  "/Users/al02451008/Documents/code/morning-post/test_backup_service.py"         # 備用圖片服務測試
  "/Users/al02451008/Documents/code/morning-post/test_morning_post.sh"           # 早安貼文測試腳本
)

echo "===== 開始清理不需要的測試檔案 ====="
echo "將保留以下檔案:"
for file in "${KEEP[@]}"; do
  echo "  - $(basename "$file")"
done

# 建立備份目錄
BACKUP_DIR="/Users/al02451008/Documents/code/morning-post/test_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "已建立備份目錄: $BACKUP_DIR"

# 查找所有測試檔案
find /Users/al02451008/Documents/code/morning-post -name "test_*.py" -type f | while read file; do
  # 檢查是否在保留列表中
  keep=false
  for keep_file in "${KEEP[@]}"; do
    if [ "$file" = "$keep_file" ]; then
      keep=true
      break
    fi
  done
  
  # 如果不在保留列表中，移動到備份目錄
  if [ "$keep" = false ]; then
    echo "移動到備份: $(basename "$file")"
    cp "$file" "$BACKUP_DIR/"
    rm "$file"
  fi
done

# 清理我們今天創建的測試檔案
TEST_FILES_TO_DELETE=(
  "/Users/al02451008/Documents/code/morning-post/test_image_urls.py"
  "/Users/al02451008/Documents/code/morning-post/test_image_urls_expanded.py"
  "/Users/al02451008/Documents/code/morning-post/test_pinterest_download.py"
)

for file in "${TEST_FILES_TO_DELETE[@]}"; do
  if [ -f "$file" ]; then
    echo "移動到備份: $(basename "$file")"
    cp "$file" "$BACKUP_DIR/"
    rm "$file"
  fi
done

echo "===== 清理完成 ====="
echo "備份檔案保存在: $BACKUP_DIR"
echo "請檢查確認所有功能正常運作。"
