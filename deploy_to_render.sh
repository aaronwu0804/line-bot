#!/bin/bash
# filepath: /Users/al02451008/Documents/code/morning-post/deploy_to_render.sh
# 部署到 Render 的腳本

# 設置顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== 準備部署 LINE Bot Webhook 到 Render ===${NC}"

# 檢查 .env 文件
if [ ! -f .env ]; then
    echo -e "${RED}找不到 .env 文件，請先設定環境變數${NC}"
    echo -e "可以使用 cp .env.example .env 創建，然後編輯填入實際值"
    exit 1
fi

# 檢查 Gemini API 金鑰
if ! grep -q "GEMINI_API_KEY" .env || grep -q "GEMINI_API_KEY=your_gemini_api_key" .env; then
    echo -e "${RED}請在 .env 文件中設定有效的 GEMINI_API_KEY${NC}"
    exit 1
fi

# 確認 Git 初始化
if [ ! -d .git ]; then
    echo -e "${YELLOW}初始化 Git 儲存庫...${NC}"
    git init
fi

# 檢查是否忽略 .env 文件
if ! grep -q ".env" .gitignore 2>/dev/null; then
    echo -e "${YELLOW}添加 .env 到 .gitignore...${NC}"
    echo ".env" >> .gitignore
fi

# 確保所有腳本有執行權限
echo -e "${YELLOW}添加執行權限到重要腳本...${NC}"
chmod +x render_app.py src/line_webhook.py keep_render_alive.py src/test_render_deployment.py start_webhook.py start_bot.py

# 提示用戶進入 Render 儀表板
echo -e "${GREEN}準備工作完成！${NC}"
echo -e "${YELLOW}接下來請訪問 Render 儀表板: https://dashboard.render.com${NC}"
echo -e "1. 創建新的 Web Service"
echo -e "2. 連接您的 GitHub 存儲庫或上傳代碼"
echo -e "3. 設定以下項目:"
echo -e "   - Name: line-bot-morning-post"
echo -e "   - Environment: Python 3"
echo -e "   - Build Command: ./build.sh"
echo -e "   - Start Command: ./start.sh"
echo -e "   - 在環境變數中添加 .env 中的所有變數"
echo -e "4. 點擊「Create Web Service」按鈕"

echo -e "${YELLOW}部署完成後，請記住您的服務 URL:${NC}"
echo -e "例如: https://line-bot-morning-post.onrender.com"
echo -e "並更新到 LINE Developers Console 的 Webhook URL 設定: https://developers.line.biz/console/"
echo -e "Webhook URL 應為: https://your-service-name.onrender.com/callback"

echo -e "${GREEN}完成後，您可以使用以下命令測試部署:${NC}"
echo -e "RENDER_SERVICE_URL=https://your-service-name.onrender.com python src/test_render_deployment.py"

echo -e "${YELLOW}如需更多資訊，請參考:${NC}"
echo -e "- docs/RENDER_DEPLOYMENT.md"
