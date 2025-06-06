# 獨立LINE Bot部署指南

本文檔說明如何使用獨立的GitHub倉庫來部署LINE Bot，完全避免與LINE SDK混淆的問題。

## 獨立倉庫的優勢

1. **避免與LINE SDK示例代碼混淆**：Render等平台不會誤解並部署LINE SDK的示例代碼
2. **完全控制部署流程**：清晰的依賴關係和構建過程
3. **更簡單的維護**：無需處理外部倉庫的變化
4. **更清晰的錯誤診斷**：部署日誌更加明確

## 部署到Render的步驟

### 方法1：使用GitHub倉庫自動部署（推薦）

1. 訪問[Render控制台](https://dashboard.render.com)
2. 點擊"New"，然後選擇"Web Service"
3. 選擇"GitHub"，並授權Render訪問您的GitHub帳戶
4. 選擇倉庫`aaronwu0804/line-bot`
5. 使用以下設置：
   - Name: `line-bot-webhook`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Plan: Free
6. 在"Environment Variables"部分添加以下變數：
   - `PORT`: `8080`
   - `RENDER`: `true`
   - `LINE_CHANNEL_ACCESS_TOKEN`: 您的LINE頻道訪問令牌
   - `LINE_CHANNEL_SECRET`: 您的LINE頻道密鑰
   - `LINE_USER_ID`: 您的LINE用戶ID
   - `GEMINI_API_KEY`: 您的Google Gemini API金鑰
7. 點擊"Create Web Service"開始部署

### 方法2：使用Render Blueprint（自動配置）

1. 點擊這個按鈕直接部署到Render：
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
2. 選擇倉庫`aaronwu0804/line-bot`
3. 填寫環境變數（同上）
4. 點擊"Apply"開始部署

## 驗證部署

部署完成後，執行以下步驟來驗證部署是否成功：

1. 檢查Render控制台，確保服務狀態為"Live"
2. 訪問`https://your-service-name.onrender.com`，應該會看到歡迎頁面
3. 訪問`https://your-service-name.onrender.com/health`，應該會看到健康狀態JSON
4. 在LINE開發者控制台中設置Webhook URL為`https://your-service-name.onrender.com/callback`
5. 使用以下命令進行完整測試：
   ```bash
   python src/line_webhook_test.py --url https://your-service-name.onrender.com/callback --text "AI: 測試訊息"
   ```

## 故障排除

如果部署失敗，請檢查以下幾點：

1. 查看Render日誌，尋找任何錯誤訊息
2. 確保所有環境變數都正確設置
3. 確認`app.py`在倉庫根目錄，並且可以被正確執行
4. 確保`requirements.txt`包含所有必要的依賴

## 更新和維護

要更新已部署的服務：

1. 在本地對代碼進行更改
2. 提交並推送到GitHub：
   ```bash
   git add .
   git commit -m "更新描述"
   git push origin main
   ```
3. Render將自動檢測更改並重新部署（如果啟用了自動部署）
4. 手動部署：在Render控制台點擊"Manual Deploy" > "Deploy latest commit"
