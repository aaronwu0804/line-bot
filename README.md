# Morning Post Bot

這是一個自動化的 LINE Bot 專案，用於每天定時發送 AI 生成的早安圖片和問候訊息，並支援與 Gemini AI 的對話功能。

## 功能特點

- 使用 OpenAI DALL-E 3 生成精美的早安圖片
- 自動發送到指定的 LINE 官方帳號
- 每日自動發送天氣預報與問候（平日 7:00、週末 8:00）
- 智慧型天氣相關的早安問候語
- 支援圖片本地儲存
- **全新：** 支援 Gemini AI 對話功能，在 LINE 聊天室直接與 AI 對話
- **全新：** 對話上下文記憶功能，支援連續對話

## 安裝步驟

1. 安裝必要的套件：
```bash
pip install -r requirements.txt
```

2. 複製環境變數範本並設定：
```bash
cp .env.example .env
```

3. 在 `.env` 檔案中填入您的設定：
- LINE_CHANNEL_ACCESS_TOKEN: LINE Bot 的 Channel Access Token
- LINE_CHANNEL_SECRET: LINE Bot 的 Channel Secret
- LINE_USER_ID: 接收訊息的 LINE User ID
- CWB_API_KEY: 中央氣象局 API 金鑰
- GEMINI_API_KEY: Google Gemini API 金鑰
- RENDER_SERVICE_URL: (可選) 如果使用 Render 部署，設定服務的 URL 以防止休眠
- GEMINI_API_KEY: Google Gemini API 金鑰（用於 AI 對話功能）

## 使用方式

### 啟動早安訊息服務

運行以下命令啟動自動發送早安訊息的服務：
```bash
python start_bot.py
```

執行測試模式（立即發送一條測試訊息，不啟動排程）：
```bash
python start_bot.py --test
```

### 啟動 Gemini AI 對話功能

運行以下命令啟動 LINE Bot 的 Webhook 服務，以支援 Gemini AI 對話功能：
```bash
python start_webhook.py
```

測試 Gemini API 連接：
```bash
python start_webhook.py --test-api
```

### 使用 AI 對話功能

在 LINE 聊天室中，可以使用以下格式與 Gemini AI 對話：
1. 發送 `AI: 你的問題` 格式的訊息
2. 或發送 `@AI 你的問題` 格式的訊息

系統會自動記憶對話上下文，支援連續對話。

## 注意事項

1. 需要有一個可公開訪問的網域來接收 LINE Webhook 事件
2. LINE Bot 需要設定為 Messaging API 模式並設定 Webhook URL
3. 為防止服務中斷，建議使用 process manager（如 PM2）來管理程式的執行
4. 早安服務和對話服務可以同時運行，互不影響

## 部署指南

### 使用 Ngrok 進行本地測試

如果您想在本地環境中測試 Webhook 功能，可以使用 Ngrok 建立臨時的公開網址：

1. 安裝 Ngrok：https://ngrok.com/download
2. 啟動 Ngrok，將本地 5000 端口轉發到公網：
   ```bash
   ngrok http 5000
   ```
3. 獲取 Ngrok 提供的公開 URL（例如：https://xxxx-xx-xx-xxx-xx.ngrok-free.app）
4. 在 LINE Developer Console 中設定 Webhook URL 為：https://xxxx-xx-xx-xxx-xx.ngrok-free.app/callback

### 使用 Docker 部署

專案已包含 Docker 配置，您可以使用以下命令一鍵部署：

```bash
docker-compose up -d
```

### 使用 Render 免費方案部署

我們已經準備了在 Render 上免費部署的完整指南：

1. 查看 [Render 部署指南](./docs/RENDER_DEPLOYMENT.md) 獲取詳細步驟
2. 部署後，您將獲得一個固定的 HTTPS URL，無需自行管理 SSL 證書
3. 免費方案適合測試和個人使用，無需支付任何費用
4. 使用 `keep_alive.py` 腳本防止服務休眠

## 自訂設定

1. 在 `generate_greeting_message()` 函數中可以自訂早安問候語的格式和內容
2. 可以修改 `line_webhook.py` 中的 `is_ai_request()` 函數來自訂觸發 AI 對話的關鍵字
3. 調整 `MAX_HISTORY` 變數來控制對話歷史記錄的長度
