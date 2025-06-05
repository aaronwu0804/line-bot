# Render 部署指南

這篇文檔將指導您如何使用 Render 的免費方案部署 LINE Bot Webhook 服務。

## 1. 準備工作

在開始部署前，請確保您已經：

1. 在 [LINE Developers Console](https://developers.line.biz/console/) 創建了一個 Provider 和 Channel（Messaging API 類型）
2. 獲取了 Channel Access Token 和 Channel Secret
3. 獲取了 Google Gemini API 金鑰

## 2. 註冊 Render 帳戶

1. 前往 [Render 官網](https://render.com/)
2. 點擊 "Sign Up" 創建一個新帳戶
3. 可以選擇使用 GitHub、GitLab 或者電子郵件進行註冊

## 3. 創建新的 Web Service

1. 登入 Render 帳戶後，點擊 Dashboard 中的 "New +" 按鈕
2. 選擇 "Web Service"
3. 連接您的 GitHub/GitLab 帳戶，或者直接上傳代碼

### 方法 A：從 GitHub 部署

如果您的代碼已經在 GitHub 上：

1. 授權 Render 訪問您的 GitHub 帳戶
2. 選擇包含您 LINE Bot 代碼的存儲庫

### 方法 B：直接上傳

如果您想直接從本地上傳：

1. 選擇 "Upload" 選項
2. 壓縮整個專案文件夾
3. 上傳壓縮包

## 4. 配置 Web Service

填寫以下信息：

- **Name**: 為您的服務命名，例如 "line-bot-webhook"
- **Environment**: 選擇 "Python 3"
- **Region**: 選擇離您用戶最近的地區
- **Branch**: 如果從 GitHub 部署，選擇要部署的分支
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn render_app:app`

## 5. 環境變數設置

在 "Environment Variables" 部分，添加以下環境變數：

- `LINE_CHANNEL_ACCESS_TOKEN`: 您的 LINE Channel Access Token
- `LINE_CHANNEL_SECRET`: 您的 LINE Channel Secret
- `LINE_USER_ID`: 您的 LINE User ID
- `CWB_API_KEY`: 中央氣象局 API 金鑰
- `GEMINI_API_KEY`: Google Gemini API 金鑰
- `PORT`: 8080（Render 推薦的端口）

## 6. 部署和測試

1. 點擊 "Create Web Service" 按鈕開始部署
2. 等待部署完成（通常需要幾分鐘）
3. 部署完成後，Render 將提供一個形如 `https://your-service-name.onrender.com` 的網址

## 7. 配置 LINE Webhook URL

1. 訪問 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇您的 Provider 和 Channel
3. 點擊 "Messaging API" 選項卡
4. 在 "Webhook settings" 部分：
   - 將 "Webhook URL" 設定為 `https://your-service-name.onrender.com/callback`
   - 將 "Use webhook" 設定為 "Enabled"
   - 點擊 "Verify" 按鈕確認 Webhook 可以正常工作

## 8. 測試 Webhook

1. 將 LINE Bot 添加為朋友（使用 LINE Developers Console 中提供的 QR 碼）
2. 發送一條測試消息，格式如下：
   ```
   AI: 你好，請自我介紹
   ```
3. 如果一切正常，您應該會收到來自 Gemini AI 的回應

## 9. 注意事項

1. **Render 的免費方案限制**：
   - 每月 750 小時免費使用時間
   - 如果 15 分鐘內沒有流量，您的服務會進入休眠狀態
   - 第一個請求可能會比較慢（需要喚醒服務）

2. **日誌查看**：
   - 您可以在 Render Dashboard 中查看應用日誌
   - 這對於調試和監控服務狀態非常有用

3. **自動部署**：
   - 如果您從 GitHub 部署，每次推送到選定分支時，Render 會自動重新部署

4. **早安貼文功能維護**：
   - 早安貼文功能不會受到影響，它仍然可以使用定時器在本地或其他服務器上運行
   
5. **避免服務休眠**：
   - 如果希望服務不進入休眠狀態，可以設置一個定時 ping，每 14 分鐘請求一次您的服務

通過以上步驟，您可以完全免費地在 Render 上部署 LINE Bot Webhook 服務！
