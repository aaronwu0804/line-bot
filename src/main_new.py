"""
早安貼文自動發送程式
功能：
1. 每日自動發送早安圖片和天氣預報到 LINE
2. 週一至週五 7:00、週六日 8:00 發送
3. 支持備用天氣資料避免網路問題
4. 智慧化問候語根據天氣變化
"""

from datetime import datetime
import os
import logging
import random
import time
import sys
import requests
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    ImageMessage,
    PushMessageRequest
)
import schedule

# 設置 Python Path 以便能夠導入其他模組
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 設定日誌
log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'morning_post.log')
# 確保 logs 資料夾存在
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 從其他模組導入功能
from test_pinterest import get_pinterest_image
try:
    # 優先使用增強版天氣服務
    from weather_service_enhanced import WeatherService
    logger.info("使用增強版天氣服務")
except ImportError:
    # 如果找不到增強版，則使用原始版本
    from weather_service import WeatherService
    logger.info("使用原始版天氣服務")

# 載入環境變數
load_dotenv()

def generate_greeting_message(weather_info=None):
    """根據天氣狀況生成早安問候語"""
    # 基本問候語
    basic_greetings = [
        "早安！今天又是嶄新的一天！",
        "早安！願你擁有美好的一天！",
        "早安！讓我們以微笑迎接今天！",
        "早安！新的一天充滿無限可能！",
        "早安！今天也要加油喔！",
        "早安！每一天都是新的開始！",
        "早安！祝你有個愉快的一天！",
        "早安！讓我們懷著感恩的心開始新的一天！",
        "早安！今天你最棒！",
        "早安！美好的一天從現在開始！"
    ]
    
    if not weather_info:
        return random.choice(basic_greetings)
        
    # 根據天氣狀況的特殊問候語
    weather = weather_info.get('weather', '')
    rain_prob = float(weather_info.get('rain_prob', 0))
    temp = float(weather_info.get('temp', 20))
    
    weather_greetings = []
    
    # 依據天氣現象選擇問候語
    if "雨" in weather:
        weather_greetings.extend([
            "早安！今天要記得帶傘喔！☔",
            "早安！雨天也要保持好心情！🌧️",
            "早安！下雨天要特別小心路滑！",
            "早安！窗外有雨滴，別忘了雨傘！"
        ])
    elif "陰" in weather:
        weather_greetings.extend([
            "早安！陰天也不減美好的心情！☁️",
            "早安！灰濛濛的天空也有它的美！",
            "早安！陰天更要用笑容照亮身邊的人！",
            "早安！雖是陰天，但心情要晴朗！"
        ])
    elif "晴" in weather:
        weather_greetings.extend([
            "早安！和煦的陽光已經準備好了！☀️",
            "早安！讓我們迎接燦爛的陽光！",
            "早安！晴朗的天氣配上燦爛的笑容！",
            "早安！藍天白雲，心情也晴朗！"
        ])
    
    # 依據溫度選擇額外問候語
    if temp < 15:
        weather_greetings.extend([
            "早安！天氣很涼，記得添加衣物！🧥",
            "早安！別忘了多穿一件外套！",
            "早安！天氣轉涼，注意保暖喔！"
        ])
    elif temp > 28:
        weather_greetings.extend([
            "早安！天氣較熱，記得補充水分！💧",
            "早安！請做好防曬措施！🧴",
            "早安！炎熱天氣，請多喝水！"
        ])
        
    # 如果有特殊天氣問候語，從中選擇，否則使用基本問候語
    if weather_greetings:
        return random.choice(weather_greetings)
    else:
        return random.choice(basic_greetings)

def send_morning_message():
    """發送早安訊息和天氣預報"""
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
        
        # 獲取天氣資訊
        logger.info("開始獲取天氣資訊...")
        weather_service = WeatherService(os.getenv('CWB_API_KEY'))
        weather = weather_service.get_taoyuan_weather()
        
        # 如果無法獲取天氣資料，使用備用資料
        if not weather and hasattr(weather_service, 'get_backup_weather'):
            logger.info("使用備用天氣資料")
            weather = weather_service.get_backup_weather()
        
        # 生成天氣相關的問候語
        current_time = datetime.now().strftime('%Y年%m月%d日')
        greeting = generate_greeting_message(weather if weather else None)
        
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
                f"{greeting}\n"
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
            message_text = f"{greeting}\n{current_time}\n\n抱歉，暫時無法獲取天氣資訊。"
            
        # 4. 添加文字訊息
        text_message = TextMessage(text=message_text)
        messages.append(text_message)
        
        # 5. 獲取並添加圖片
        try:
            logger.info("正在獲取 Pinterest 圖片...")
            image_url = get_pinterest_image()
            if image_url:
                logger.info(f"成功獲取圖片 URL: {image_url}")
                
                # 檢查圖片 URL 格式
                if not (image_url.startswith('http://') or image_url.startswith('https://')):
                    logger.error(f"圖片 URL 格式無效: {image_url}")
                    raise ValueError(f"圖片 URL 格式無效: {image_url}")
                
                # 確保圖片 URL 是 HTTPS (LINE 只接受 HTTPS)
                if image_url.startswith('http:'):
                    image_url = image_url.replace('http:', 'https:')
                    logger.info(f"URL 已轉換為 HTTPS: {image_url}")
                
                # 檢查圖片 URL 是否可以訪問
                try:
                    response = requests.head(image_url, timeout=10)
                    logger.info(f"圖片 URL 檢查: 狀態碼 {response.status_code}")
                    if response.status_code != 200:
                        logger.warning(f"圖片 URL 可能無效，狀態碼: {response.status_code}")
                except Exception as url_check_error:
                    logger.warning(f"檢查圖片 URL 時出錯: {str(url_check_error)}")
                
                # 創建圖片訊息
                image_message = ImageMessage(
                    originalContentUrl=image_url,
                    previewImageUrl=image_url
                )
                messages.append(image_message)
                logger.info("已將圖片訊息添加到發送隊列")
            else:
                logger.warning("未能獲取圖片，將只發送文字訊息")
        except Exception as img_error:
            logger.error(f"處理圖片時發生錯誤: {str(img_error)}")
            logger.error(f"詳細錯誤: {repr(img_error)}")
            # 繼續執行，即使沒有圖片也至少發送文字訊息
        
        # 6. 發送訊息
        try:
            if messages:
                # LINE 訊息有數量限制（最多 5 則），這裡限制為最多 2 則（文字 + 圖片）
                if len(messages) > 2:
                    logger.warning(f"訊息數量超過限制，原始數量 {len(messages)}，將截取前 2 則")
                    messages = messages[:2]
                
                logger.info(f"即將發送 {len(messages)} 則訊息到 LINE，類型: {[type(m).__name__ for m in messages]}")
                
                # 確保每個訊息物件都是有效的
                valid_messages = []
                for msg in messages:
                    if isinstance(msg, (TextMessage, ImageMessage)):
                        valid_messages.append(msg)
                    else:
                        logger.warning(f"忽略無效的訊息類型: {type(msg)}")
                
                if valid_messages:
                    # 檢查訊息格式是否符合 LINE API 要求
                    try:
                        # 確保每個圖片訊息的 URL 以 HTTPS 開頭
                        for i, msg in enumerate(valid_messages):
                            if isinstance(msg, ImageMessage):
                                if not msg.originalContentUrl.startswith('https://'):
                                    logger.warning(f"圖片 URL 不是 HTTPS: {msg.originalContentUrl}")
                                    # 嘗試轉換為 HTTPS
                                    msg.originalContentUrl = msg.originalContentUrl.replace('http://', 'https://')
                                    msg.previewImageUrl = msg.previewImageUrl.replace('http://', 'https://')
                                    valid_messages[i] = msg
                    
                        # 發送訊息
                        logger.info(f"發送訊息到用戶: {LINE_USER_ID}")
                        line_bot_api.push_message(
                            PushMessageRequest(
                                to=LINE_USER_ID,
                                messages=valid_messages
                            )
                        )
                        logger.info(f"成功發送 {len(valid_messages)} 則訊息到 LINE")
                        logger.info(f"成功發送早安貼文，時間: {datetime.now()}")
                    except Exception as format_error:
                        logger.error(f"訊息格式錯誤: {str(format_error)}")
                        # 嘗試只發送文字訊息
                        text_only = [msg for msg in valid_messages if isinstance(msg, TextMessage)]
                        if text_only:
                            logger.info("嘗試只發送文字訊息...")
                            line_bot_api.push_message(
                                PushMessageRequest(
                                    to=LINE_USER_ID,
                                    messages=text_only
                                )
                            )
                            logger.info(f"成功發送 {len(text_only)} 則文字訊息到 LINE")
                else:
                    logger.error("沒有有效的訊息可發送")
            else:
                logger.error("沒有可發送的訊息")
        except Exception as send_error:
            logger.error(f"發送 LINE 訊息時發生錯誤: {str(send_error)}")
            logger.error(f"詳細錯誤內容: {repr(send_error)}")
            # 嘗試使用備用方法發送文字訊息
            try:
                fallback_message = TextMessage(text=f"早安！{current_time}\n\n今天的圖片無法顯示，但仍祝您有美好的一天！")
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=LINE_USER_ID,
                        messages=[fallback_message]
                    )
                )
                logger.info("成功發送備用文字訊息")
            except Exception as fallback_error:
                logger.error(f"發送備用訊息也失敗了: {str(fallback_error)}")
            # 不要在這裡拋出異常，讓程式能夠繼續執行
        
    except Exception as e:
        logger.error(f"發送早安訊息失敗：{str(e)}")

def main():
    """主程式"""
    # 設定週一至週五早上 7 點發送訊息
    schedule.every().monday.at("07:00").do(send_morning_message)
    schedule.every().tuesday.at("07:00").do(send_morning_message)
    schedule.every().wednesday.at("07:00").do(send_morning_message)
    schedule.every().thursday.at("07:00").do(send_morning_message)
    schedule.every().friday.at("07:00").do(send_morning_message)
    
    # 設定週六和週日早上 8 點發送訊息
    schedule.every().saturday.at("08:00").do(send_morning_message)
    schedule.every().sunday.at("08:00").do(send_morning_message)
    
    logger.info("排程已啟動：平日 07:00、週末 08:00")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    try:
        logger.info("程式開始執行...")
        logger.info("==== 開始發送早安訊息 ====")
        # 立即發送一次測試訊息
        send_morning_message()
        logger.info("==== 早安訊息發送完成，開始設置排程 ====")
        # 啟動排程
        main()
    except KeyboardInterrupt:
        logger.info("程式已停止")
    except Exception as e:
        logger.error(f"程式執行時發生錯誤: {str(e)}")
        logger.exception("詳細錯誤追蹤：")  # 這會記錄完整的堆棧追蹤
