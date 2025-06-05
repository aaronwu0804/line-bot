#!/bin/bash
# Render平台構建腳本

echo "=== 執行 LINE Bot Webhook 構建程序 ==="
echo "當前目錄: $(pwd)"
echo "當前文件列表:"
ls -la

# 安裝依賴
echo "安裝Python依賴..."
pip install -r requirements.txt

# 阻止LINE SDK範例程式碼干擾
if pip show line-bot-sdk > /dev/null; then
  echo "檢測到LINE SDK安裝"
  # 查找SDK安裝目錄
  SDK_PATH=$(pip show line-bot-sdk | grep "Location" | cut -d " " -f 2)
  if [ -d "$SDK_PATH" ]; then
    echo "LINE SDK安裝在: $SDK_PATH"
    # 查找範例目錄
    EXAMPLES_PATH=$(find $SDK_PATH -name "examples" -type d)
    if [ -n "$EXAMPLES_PATH" ]; then
      echo "找到範例目錄: $EXAMPLES_PATH"
      echo "重命名範例目錄以防止Render使用它..."
      mv "$EXAMPLES_PATH" "$EXAMPLES_PATH.bak"
      echo "範例目錄已重命名為: $EXAMPLES_PATH.bak"
    else
      echo "未找到LINE SDK範例目錄"
    fi
  fi
fi

echo "構建過程完成"
