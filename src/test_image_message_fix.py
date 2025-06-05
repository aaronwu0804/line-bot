#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/test_image_message_fix.py
"""
使用備用天氣資料發送包含圖片的早安訊息的測試腳本
這個腳本修復了模組導入問題
"""

from datetime import datetime
import os
import logging
import sys
import socket
import requests  # 用於測試圖片URL
import time
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    ImageMessage,
    PushMessageRequest
)

# 設定 Python Path 以便能夠導入其他模組
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(current_dir)  # 同時加入當前目錄

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

# 從相關模組導入功能
try:
    # 嘗試直接導入
    from test_pinterest import get_pinterest_image
    logger.info("成功導入 get_pinterest_image 函數")
except ImportError:
    try:
        # 嘗試從 src 目錄導入
        from src.test_pinterest import get_pinterest_image
        logger.info("成功從 src 導入 get_pinterest_image 函數")
    except ImportError:
        logger.error("無法導入 Pinterest 圖片模組，將使用備用圖片")
        # 提供備用圖片 URL，確保測試能夠繼續
        def get_pinterest_image():
            logger.warning("使用備用圖片函數")
            return None

# 導入備用圖片服務
try:
    # 嘗試直接導入
    from backup_image_service import get_backup_image
    logger.info("成功導入備用圖片服務")
except ImportError:
    try:
        # 嘗試從 src 目錄導入
        from src.backup_image_service import get_backup_image
        logger.info("成功從 src 導入備用圖片服務")
    except ImportError:
        logger.error("無法導入備用圖片服務，將使用固定 URL")
        # 提供固定的備用圖片 URL
        def get_backup_image():
            logger.warning("使用固定備用圖片 URL")
            return "https://i.pinimg.com/originals/e5/73/7c/e5737c44dd061635766b6682a3e42d69.jpg"

# 從天氣服務模組導入
try:
    # 優先使用增強版天氣服務
    try:
        from weather_service_enhanced import WeatherService
        logger.info("使用增強版天氣服務")
    except ImportError:
        from src.weather_service_enhanced import WeatherService
        logger.info("使用增強版天氣服務 (從 src 導入)")
except ImportError:
    try:
        from weather_service import WeatherService
        logger.info("使用原始版天氣服務")
    except ImportError:
        from src.weather_service import WeatherService
        logger.info("使用原始版天氣服務 (從 src 導入)")

def test_image_url(url):
    """測試圖片 URL 是否可訪問"""
    if not url:
        return False
    
    try:
        # 檢查圖片 URL 格式
        if not (url.startswith('http://') or url.startswith('https://')):
            logger.error(f"圖片 URL 格式無效: {url}")
            return False
        
        # 確保圖片 URL 是 HTTPS (LINE 只接受 HTTPS)
        if url.startswith('http:'):
            url = url.replace('http:', 'https:')
            logger.info(f"URL 已轉換為 HTTPS: {url}")
        
        # 檢查圖片 URL 是否可以訪問
        response = requests.head(url, timeout=10)
        logger.info(f"圖片 URL 檢查: 狀態碼 {response.status_code}")
        
        if response.status_code != 200:
            logger.warning(f"圖片 URL 可能無效，狀態碼: {response.status_code}")
            return False
            
        return url
    except Exception as url_check_error:
        logger.warning(f"檢查圖片 URL 時出錯: {str(url_check_error)}")
        return False

def send_test_image_message():
    """使用備用天氣資料發送測試圖片訊息"""
    try:
        # 設定 LINE Bot API
        configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
        if not configuration.access_token:
            raise ValueError("未設定 LINE_CHANNEL_ACCESS_TOKEN")

        api_client = ApiClient(configuration)
        line_bot_api = MessagingApi(api_client)
        
        LINE_USER_ID = os.getenv('LINE_USER_ID')
        if not LINE_USER_ID:
            raise ValueError("未設定 LINE_USER_ID")
        
        # 準備訊息
        messages = []

        # 取得備用天氣資料
        weather_service = WeatherService(os.getenv('CWB_API_KEY'))
        try:
            weather = weather_service.get_taoyuan_weather()
            if not weather:
                logger.info("使用備用天氣資料")
                weather = weather_service.get_backup_weather()
        except Exception as weather_error:
            logger.error(f"獲取天氣資料錯誤: {str(weather_error)}")
            weather = weather_service.get_backup_weather()
        
        # 生成訊息文字
        current_time = datetime.now().strftime('%Y年%m月%d日')
        
        if weather:
            # 根據天氣狀況添加適當的表情符號
            weather_emoji = "🌞"  # 預設晴天
            if "雨" in weather['weather']:
                weather_emoji = "🌧️"
            elif "陰" in weather['weather']:
                weather_emoji = "☁️"
            elif "多雲" in weather['weather']:
                weather_emoji = "⛅"
                
            message_text = (
                f"早安！今天又是嶄新的一天！\n"
                f"{current_time}\n\n"
                f"📍 {weather['district']}天氣報報 {weather_emoji}\n"
                f"天氣狀況：{weather['weather']}\n"
                f"溫度：{weather['min_temp']}°C - {weather['max_temp']}°C\n"
                f"降雨機率：{weather['rain_prob']}%\n"
                f"相對濕度：{weather['humidity']}%\n"
                f"舒適度：{weather['comfort']}\n\n"
                f"👉 {weather['description']}"
            )
        else:
            message_text = f"早安！\n{current_time}\n\n抱歉，暫時無法獲取天氣資訊。"
        
        # 添加標記，表示這是測試訊息
        message_text = "【測試訊息】\n" + message_text
            
        # 添加文字訊息
        text_message = TextMessage(text=message_text)
        messages.append(text_message)
        
        # 獲取並添加圖片
        try:
            time_start = time.time()
            logger.info("正在獲取 Pinterest 圖片...")
            image_url = get_pinterest_image()
            logger.info(f"獲取圖片耗時: {time.time() - time_start:.2f}秒")
            
            # 強制打印日誌便於調試
            print(f"取得的圖片 URL: {image_url}")
            logger.info(f"取得的圖片 URL: {image_url}")
            
            # 檢查獲取的圖片 URL 是否有效
            if not image_url or not isinstance(image_url, str) or len(image_url) < 10:
                logger.warning(f"未能獲取有效的 Pinterest 圖片 URL: '{image_url}'")
                logger.info("嘗試使用備用圖片...")
                image_url = get_backup_image()
                logger.info(f"備用圖片 URL: {image_url}")
            
            # 測試圖片 URL
            if image_url:
                valid_url = test_image_url(image_url)
                if valid_url:
                    # 創建圖片訊息
                    image_message = ImageMessage(
                        originalContentUrl=valid_url,
                        previewImageUrl=valid_url
                    )
                    messages.append(image_message)
                    logger.info(f"圖片訊息已添加: {valid_url}")
                else:
                    # 使用備用圖片
                    logger.warning("圖片 URL 無效，嘗試使用備用圖片")
                    backup_url = get_backup_image()
                    if backup_url:
                        # 創建圖片訊息
                        image_message = ImageMessage(
                            originalContentUrl=backup_url,
                            previewImageUrl=backup_url
                        )
                        messages.append(image_message)
                        logger.info(f"備用圖片訊息已添加: {backup_url}")
                    else:
                        logger.warning("備用圖片也無效，將只發送文字訊息")
            else:
                logger.warning("未能獲取圖片，將只發送文字訊息")
        except Exception as img_error:
            logger.error(f"處理圖片時發生錯誤: {str(img_error)}")
            try:
                # 使用最終備用圖片
                backup_url = "https://i.pinimg.com/originals/e5/73/7c/e5737c44dd061635766b6682a3e42d69.jpg"
                logger.info(f"使用最終備用圖片: {backup_url}")
                image_message = ImageMessage(
                    originalContentUrl=backup_url,
                    previewImageUrl=backup_url
                )
                messages.append(image_message)
                logger.info("最終備用圖片已添加")
            except Exception as e:
                logger.error(f"添加最終備用圖片時出錯: {str(e)}")
            
        # 發送訊息
        logger.info(f"準備發送 {len(messages)} 則訊息到 LINE")
        line_bot_api.push_message(
            PushMessageRequest(
                to=LINE_USER_ID,
                messages=messages
            )
        )
        logger.info(f"成功發送測試訊息，時間: {datetime.now()}")
        return True
    except Exception as e:
        logger.error(f"發送測試訊息失敗: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("====== 開始測試圖片訊息發送 ======")
    result = send_test_image_message()
    logger.info(f"測試結果: {'成功' if result else '失敗'}")
