# LINE Bot 部署問題排解指南

## 當前問題
根據Render日誌，我們發現Render嘗試運行以下命令：
```
==> Running 'cd examples/flask-echo;gunicorn app:app'
```

這表明Render正在執行LINE SDK包含的範例程式碼，而非我們的自定義LINE Bot程式碼。

## 解決步驟

### 1. 登入Render控制台

訪問 [Render Dashboard](https://dashboard.render.com/) 並登入您的帳號。

### 2. 找到您的服務

找到名為`line-bot-python-flask-pulo`(或類似名稱)的服務。

### 3. 修改服務設定

點擊服務，然後點擊「Settings」。需要修改以下設定：

- **Build Command**: 將其改為 `./build.sh`
- **Start Command**: 將其改為 `./start.sh`

確保這兩個腳本有執行權限(chmod +x)。

### 4. 確認環境變數

在「Environment」部分，確保以下環境變數已正確設定：

- `LINE_CHANNEL_SECRET`
- `LINE_CHANNEL_ACCESS_TOKEN`
- `GEMINI_API_KEY`
- `RENDER_SERVICE_URL` (設為您的服務URL，如 https://line-bot-python-flask-pulo.onrender.com)

### 5. 重新部署

點擊「Manual Deploy」→「Clear build cache & deploy」來重新部署您的服務。

### 6. 檢查部署日誌

觀察部署過程是否有錯誤，特別注意是否看到我們在`build.sh`中添加的特殊日誌：
```
=== LINE Bot 構建腳本開始 ===
```

以及`start.sh`中的：
```
=== LINE Bot 啟動腳本執行 ===
```

### 7. 測試服務

部署完成後，使用以下命令測試服務是否正常：

```bash
curl https://line-bot-python-flask-pulo.onrender.com/
```

應該會看到我們定製的HTML頁面，而不是404錯誤。

## 如果問題仍然存在

如果上述步驟無效，請考慮以下方案：

1. **建立新服務**：在Render上創建一個全新的服務，而不是修改現有服務

2. **檢查源代碼存儲庫**：確認Render使用的是最新的代碼，包含我們的`build.sh`和`start.sh`

3. **檢查root目錄**：確認沒有意外包含LINE的示例代碼目錄`examples`

4. **嘗試直接指定Web服務類型**：在Render設定中明確指定這是一個Web Service，而不是其他類型

5. **比較您的本地代碼與Render部署的代碼**：確保所有修改都已正確上傳
