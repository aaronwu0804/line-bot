#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/fix_render_deployment.sh
# 修復Render部署問題，防止執行LINE SDK中的範例程式

# 設置顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== 修復Render部署問題 ===${NC}"

# 確保scripts目錄存在
mkdir -p scripts

# 建立專門的Render部署腳本
cat > scripts/render_build.sh << 'EOL'
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
EOL

# 建立專門的Render啟動腳本
cat > scripts/render_start.sh << 'EOL'
#!/bin/bash
# Render平台啟動腳本

echo "=== 啟動 LINE Bot Webhook 服務 ==="
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

# 顯示 app.py 的內容確認它存在
if [ -f "app.py" ]; then
  echo "找到 app.py:"
  head -n 10 app.py
else
  echo "錯誤: 找不到 app.py 文件"
  exit 1
fi

# 直接在當前目錄啟動應用程式
echo "啟動 LINE Bot Webhook 服務..."
exec gunicorn app:app
EOL

# 設置執行權限
chmod +x scripts/render_build.sh scripts/render_start.sh

# 更新 render.yaml
cat > render.yaml << 'EOL'
version: "2"
services:
  - type: web
    name: line-bot-webhook
    runtime: python
    buildCommand: ./scripts/render_build.sh
    startCommand: ./scripts/render_start.sh
    plan: free
    envVars:
      - key: PORT
        value: 8080
      - key: RENDER_SERVICE_URL
        sync: false  # 手動設定
      - key: LINE_CHANNEL_ACCESS_TOKEN
        sync: false  # 手動設定
      - key: LINE_CHANNEL_SECRET
        sync: false  # 手動設定
      - key: LINE_USER_ID
        sync: false  # 手動設定
      - key: CWB_API_KEY
        sync: false  # 手動設定
      - key: GEMINI_API_KEY
        sync: false  # 手動設定
    autoDeploy: false
    healthCheckPath: /health
EOL

# 打印提示信息
echo -e "${GREEN}=== 修復完成 ===${NC}"
echo -e "已創建專用的構建和啟動腳本，並更新了render.yaml文件。"
echo -e "請在Render儀表板上進行以下操作:"
echo -e "1. 進入您的服務設置 (https://dashboard.render.com/web/srv-xxxx/settings)"
echo -e "2. 修改以下設置:"
echo -e "   - Build Command: ${YELLOW}./scripts/render_build.sh${NC}"
echo -e "   - Start Command: ${YELLOW}./scripts/render_start.sh${NC}"
echo -e "3. 點擊「Save Changes」並重新部署服務"
echo
echo -e "或者您也可以刪除當前服務並使用新的render.yaml從頭創建。"
echo

# 提交修改
echo -e "${YELLOW}提交修改到Git存儲庫...${NC}"
git add scripts render.yaml
git commit -m "修復Render部署問題：防止執行LINE SDK範例代碼"

echo -e "${GREEN}一切準備就緒，請部署到Render!${NC}"
