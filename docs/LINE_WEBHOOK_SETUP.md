# LINE Bot Webhook 設定指南

這篇文檔將指導您如何配置 LINE Bot 的 Webhook 以支援 Gemini AI 對話功能。

## 步驟 1: 準備工作

在開始設定前，請確保您已經：

1. 在 [LINE Developers Console](https://developers.line.biz/console/) 創建了一個 Provider 和 Channel（Messaging API 類型）
2. 獲取了 Channel Access Token 和 Channel Secret，並已加入 `.env` 文件
3. 獲取了 Google Gemini API 金鑰，並已加入 `.env` 文件
4. 安裝了所有必要依賴項 (`pip install -r requirements.txt`)

## 步驟 2: 設定公開訪問的 Webhook URL

LINE Bot 要求 Webhook URL 必須是公開可訪問的 HTTPS 網址。您有以下選擇：

### 選項 A: 使用 Ngrok 進行本地測試

1. 下載並安裝 [Ngrok](https://ngrok.com/download)
2. 啟動 webhook 服務：
   ```bash
   python start_webhook.py
   ```
3. 在另一個終端視窗中運行 Ngrok：
   ```bash
   ngrok http 5000
   ```
4. Ngrok 將提供一個臨時的 HTTPS URL，例如 `https://abcd-ef-gh-ij.ngrok-free.app`

### 選項 B: 部署到雲端服務器

1. 將代碼部署到支持 Python 的雲端服務器上（如 AWS、GCP、Heroku 等）
2. 確保公開訪問的 URL 是 HTTPS 的
3. 啟動 webhook 服務：
   ```bash
   python start_webhook.py
   ```

## 步驟 3: 在 LINE Developers Console 中配置 Webhook

1. 訪問 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇您的 Provider 和 Channel
3. 點擊 "Messaging API" 選項卡
4. 在 "Webhook settings" 部分：
   - 將 "Webhook URL" 設定為您的公開 URL + "/callback" 路徑（例如：`https://abcd-ef-gh-ij.ngrok-free.app/callback`）
   - 將 "Use webhook" 設定為 "Enabled"
   - 點擊 "Verify" 按鈕確認 Webhook 可以正常工作

## 步驟 4: 測試 Webhook

1. 將 LINE Bot 添加為朋友（使用 LINE Developers Console 中提供的 QR 碼）
2. 發送一條測試消息，格式如下：
   ```
   AI: 你好，請自我介紹
   ```
3. 如果一切正常，您應該會收到來自 Gemini AI 的回應

## 步驟 5: 監控和故障排除

- 運行 webhook 服務時，可以監控終端中的輸出以查看訊息收發狀態
- 查看 `logs/line_webhook.log` 文件以獲取更詳細的日誌信息
- 如果遇到問題，請確認：
  - Webhook URL 是否正確
  - LINE Channel Access Token 和 Channel Secret 是否正確設定
  - Gemini API 金鑰是否有效
  - 服務器防火牆是否允許入站連接

## 維護和更新

當您需要更新程式時，請按照以下步驟：

1. 停止當前運行的 webhook 服務
2. 拉取最新代碼或進行修改
3. 重新啟動 webhook 服務
4. 如果您使用 Ngrok，可能需要重新啟動 Ngrok 並更新 LINE 開發者控制台中的 Webhook URL

這樣，您的 LINE Bot 就能夠接收用戶的消息並透過 Gemini AI 進行回應了！
