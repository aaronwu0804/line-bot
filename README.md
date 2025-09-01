# 早安貼文機器人 (Morning Post Bot) - 獨立LINE Bot專案

這是一個自動化的 LINE Bot **獨立專案**，用於每天定時發送 AI 生成的早安圖片和問候訊息，並支援與 Gemini AI 的對話功能。本專案不屬於LINE SDK的一部分，而是一個完全獨立的應用程序。

## 功能特點

- 使用 OpenAI DALL-E 3 生成精美的早安圖片
- 自動發送到指定的 LINE 官方帳號
- 每日自動發送天氣預報與問候（平日 7:00、週末 8:00）
- 智慧型天氣相關的早安問候語
- 支援圖片本地儲存
- **全新：** 支援 Gemini AI 對話功能，在 LINE 聊天室直接與 AI 對話
- **全新：** 對話上下文記憶功能，支援連續對話
- **全新 v2.1.0：** 智能緩存系統，減少重複 API 調用
- **全新 v2.1.0：** 增強型錯誤處理，自動處理配額限制問題
- **全新 v2.1.0：** 智能模型選擇，優先使用輕量級模型以節省配額
- **全新 v2.2.0：** 自動清理舊圖片，防止儲存空間浪費和 Git 倉庫體積過大

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

### 圖片清理功能

早安訊息發送後會自動清理舊圖片，您也可以手動執行清理：

```bash
# 透過主程式清理圖片（清理 7 天前的圖片）
python start_bot.py --clean-images

# 指定清理 X 天前的圖片
python start_bot.py --clean-images X

# 使用獨立清理腳本（清理 7 天前的圖片）
python src/clean_images.py

# 使用獨立清理腳本（指定天數）
python src/clean_images.py 10  # 清理 10 天前的圖片
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

監控 API 使用情況：
```bash
python src/api_usage_monitor.py --test
```

分析 API 使用統計：
```bash
python src/api_usage_monitor.py --analyze
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
2. 可以修改 `app.py` 中的 `is_ai_request()` 函數來自訂觸發 AI 對話的關鍵字
3. 在 `src/response_cache.py` 中可調整緩存的有效期和設定
4. 在 `app.py` 中可調整 Gemini API 的重試策略和模型選擇邏輯

## 配額限制管理

Gemini API 在免費方案下有配額限制，本專案已實現以下機制來處理這一問題：

1. **智能緩存系統**：相同問題自動使用緩存回應
2. **指數退避策略**：遇到配額限制自動延遲重試
3. **模型回退機制**：優先使用輕量模型，遇到問題時自動嘗試其他模型
4. **參數優化**：根據重試次數動態調整參數降低令牌消耗

詳細資訊請參閱 [API 配額管理指南](./docs/API_QUOTA_MANAGEMENT.md)

## 特別說明：避免 LINE SDK 衝突

本專案是一個完全獨立的應用程序，不依賴於 LINE SDK 的原始倉庫。在部署到 Render 時，我們使用的是獨立的、自維護的程式碼，這樣可以避免與 LINE SDK 示例代碼產生混淆或衝突。
