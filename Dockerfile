FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴清單
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式代碼
COPY . .

# 添加可執行權限到腳本
RUN chmod +x start_bot.py start_webhook.py

# 默認命令 (將在 docker-compose 中被覆蓋)
CMD ["python", "start_bot.py"]
