# Render 部署問題修復指南

## 問題描述

Render服務當前運行了LINE SDK示範程式，而非我們的自定義應用程式。這可以從Render日誌中確認：

```
==> Running 'cd examples/flask-echo;gunicorn app:app'
```

這表示Render嘗試運行`examples/flask-echo`目錄中的範例程式碼，而非我們的實際應用程式。

## 解決方案

我們已經準備了專用的構建和啟動腳本，可以防止這種情況發生：

1. `scripts/render_build.sh` - 自定義構建腳本，會安裝依賴並禁用LINE SDK範例
2. `scripts/render_start.sh` - 自定義啟動腳本，確保從正確的位置啟動應用程式

### 解決步驟

#### 方法一：修改現有服務設定

1. 登入Render儀表板：https://dashboard.render.com
2. 找到您的LINE Bot服務並點擊進入
3. 選擇「Settings」頁面
4. 在「Build & Deploy」部分，修改以下設定：
   - Build Command: `./scripts/render_build.sh`
   - Start Command: `./scripts/render_start.sh`
5. 點擊「Save Changes」並重新部署服務

#### 方法二：刪除並重新創建服務

如果修改設定後仍然有問題，您可以嘗試完全重新創建服務：

1. 在Render儀表板上刪除當前服務
2. 點擊「New +」並選擇「Web Service」
3. 連接您的GitHub存儲庫或上傳代碼
4. 在設定過程中指定：
   - Build Command: `./scripts/render_build.sh`
   - Start Command: `./scripts/render_start.sh`
5. 確保添加所有必要的環境變數：
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `GEMINI_API_KEY`
   - `RENDER_SERVICE_URL` (新服務的URL)
6. 點擊「Create Web Service」

## 驗證部署

部署後，您可以使用以下方法驗證服務是否正確運行：

1. 訪問服務主頁：`https://your-service-name.onrender.com/`
   - 應該看到我們的HTML狀態頁面，而不是404錯誤

2. 檢查健康檢查端點：`https://your-service-name.onrender.com/health`
   - 應該看到服務狀態信息

3. 使用測試腳本發送模擬訊息：
   ```
   python src/line_webhook_test.py --url https://your-service-name.onrender.com/callback --text "AI: 測試訊息"
   ```

4. 在LINE應用中實際測試Bot

## 如果仍然有問題

請檢查Render的構建和運行日誌以獲取更多信息。特別注意查看日誌中是否有以下內容：

- `=== 執行 LINE Bot Webhook 構建程序 ===` (我們的構建腳本輸出)
- `=== 啟動 LINE Bot Webhook 服務 ===` (我們的啟動腳本輸出)

如果看不到這些輸出，則可能腳本未被執行，您需要確保權限設置正確並且路徑配置無誤。
