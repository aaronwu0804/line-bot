#!/bin/bash
# 部署緊急修復版本至 Render

echo "========================================================"
echo "準備部署緊急修復版本至 Render"
echo "========================================================"

# 確保腳本有執行權限
chmod +x emergency_fix.py
chmod +x scripts/render_build.sh
chmod +x scripts/render_start.sh

# 刪除 LINE SDK 示例備份文件夾，確保不會影響部署
echo "查詢 LINE SDK 位置..."
SDK_PATH=$(pip show line-bot-sdk | grep "Location" | cut -d " " -f 2)
if [ -n "$SDK_PATH" ]; then
  echo "LINE SDK 安裝在: $SDK_PATH"
  # 查找備份的範例目錄
  EXAMPLES_BAK=$(find $SDK_PATH -name "examples.bak" -type d)
  if [ -n "$EXAMPLES_BAK" ]; then
    echo "找到備份範例目錄: $EXAMPLES_BAK"
    echo "刪除備份以確保部署成功..."
    rm -rf "$EXAMPLES_BAK"
    echo "備份範例目錄已刪除"
  fi
  
  # 再次確認範例目錄
  EXAMPLES_PATH=$(find $SDK_PATH -name "examples" -type d)
  if [ -n "$EXAMPLES_PATH" ]; then
    echo "找到範例目錄: $EXAMPLES_PATH"
    echo "重命名範例目錄以防止 Render 使用它..."
    mv "$EXAMPLES_PATH" "${EXAMPLES_PATH}_disabled"
    echo "範例目錄已禁用"
  fi
fi

# 提交更改到 Git
echo "提交更改到 Git..."
git add scripts/render_start.sh emergency_fix.py deploy_emergency_fix.sh
git commit -m "配置緊急修復版本"

# 部署到 Render
echo "推送到 GitHub 並觸發 Render 部署..."
git push

echo "========================================================"
echo "部署程序完成！"
echo "請前往 Render 控制台檢查部署狀況"
echo "========================================================"
