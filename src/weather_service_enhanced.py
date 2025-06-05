"""
增強版天氣服務模組
- 添加重試機制
- 改進錯誤處理
- 添加網路可達性檢查
- 添加結果快取
"""

import requests
import logging
import time
import socket
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WeatherService:
    """增強版天氣服務類"""
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore"
        self._cache = {}  # 使用內部快取儲存天氣資料
        self._cache_expiry = {}  # 快取過期時間
        
    def _check_internet_connection(self, host="8.8.8.8", port=53, timeout=3):
        """檢查網路連接是否可用"""
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error:
            return False
            
    def _is_cache_valid(self, cache_key):
        """檢查快取是否有效"""
        if cache_key in self._cache and cache_key in self._cache_expiry:
            if datetime.now() < self._cache_expiry[cache_key]:
                return True
        return False
        
    def get_taoyuan_weather(self, max_retries=3, timeout=10, cache_ttl=3600):
        """
        獲取桃園市天氣預報 (使用 F-D0047-091 API)
        
        參數:
            max_retries: 最大重試次數
            timeout: 請求超時時間 (秒)
            cache_ttl: 快取有效時間 (秒)
        """
        cache_key = "taoyuan_weather"
        
        # 檢查快取是否有效
        if self._is_cache_valid(cache_key):
            logger.info("從快取中讀取天氣資料")
            return self._cache[cache_key]
            
        # 檢查網路連接
        if not self._check_internet_connection():
            logger.error("無法連接網路，請檢查網路設定")
            return None
            
        retry_count = 0
        retry_delay = 2  # 初始重試延遲 (秒)
        
        while retry_count < max_retries:
            try:
                # 使用天氣預報API F-D0047-091
                url = f"{self.base_url}/F-D0047-091"
                params = {
                    "Authorization": self.api_key,
                    "locationName": "桃園市",
                    "elementName": "MinT,MaxT,PoP12h,T,RH,MinCI,Wx,WeatherDescription",
                    "sort": "time"
                }
                
                # 添加超時設定，避免請求卡住太久
                logger.info(f"嘗試獲取天氣資料 (嘗試 {retry_count + 1}/{max_retries})...")
                response = requests.get(url, params=params, timeout=timeout)
                
                if response.status_code != 200:
                    logger.error(f"獲取天氣資料失敗: HTTP {response.status_code}")
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指數退避重試策略
                    continue
                
                data = response.json()
                if "records" not in data or "locations" not in data["records"]:
                    logger.error("回應資料格式錯誤")
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(retry_delay)
                    continue
                
                # 解析天氣資料
                locations = data["records"]["locations"][0]["location"]
                if not locations:
                    logger.error("找不到桃園市的天氣資料")
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(retry_delay)
                    continue
                
                # 取得第一個行政區的資料（通常是桃園區）
                weather_elements = locations[0]["weatherElement"]
                
                result = {
                    "district": locations[0]["locationName"],
                    "lat": locations[0]["lat"],
                    "lon": locations[0]["lon"]
                }
                
                # 遍歷所有天氣要素
                for element in weather_elements:
                    element_name = element["elementName"]
                    if element_name == "MinT":  # 最低溫度
                        result["min_temp"] = element["time"][0]["elementValue"][0]["value"]
                    elif element_name == "MaxT":  # 最高溫度
                        result["max_temp"] = element["time"][0]["elementValue"][0]["value"]
                    elif element_name == "T":  # 平均溫度
                        result["temp"] = element["time"][0]["elementValue"][0]["value"]
                    elif element_name == "PoP12h":  # 12小時降雨機率
                        result["rain_prob"] = element["time"][0]["elementValue"][0]["value"]
                    elif element_name == "RH":  # 相對濕度
                        result["humidity"] = element["time"][0]["elementValue"][0]["value"]
                    elif element_name == "Wx":  # 天氣現象
                        result["weather"] = element["time"][0]["elementValue"][0]["value"]
                    elif element_name == "MinCI":  # 最小舒適度指數
                        result["comfort"] = element["time"][0]["elementValue"][0]["value"]
                    elif element_name == "WeatherDescription":  # 天氣預報綜合描述
                        result["description"] = element["time"][0]["elementValue"][0]["value"]
                
                if all(k in result for k in ["min_temp", "max_temp", "rain_prob", "weather"]):
                    logger.info(f"成功獲取桃園市天氣資料: {result}")
                    
                    # 儲存到快取
                    self._cache[cache_key] = result
                    self._cache_expiry[cache_key] = datetime.now() + timedelta(seconds=cache_ttl)
                    logger.info(f"天氣資料已快取，有效期至 {self._cache_expiry[cache_key]}")
                    
                    return result
                else:
                    logger.error("天氣資料不完整")
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(retry_delay)
                    continue
                    
            except requests.exceptions.RequestException as e:
                error_message = str(e)
                logger.error(f"請求異常: {error_message}")
                
                # 檢查是否為 DNS 解析錯誤或連接問題
                if "NameResolution" in error_message or "ConnectionError" in error_message:
                    logger.error("DNS 解析錯誤或網路連接問題，請確認網路和 DNS 設定")
                
                retry_count += 1
                if retry_count < max_retries:
                    logger.info(f"將在 {retry_delay} 秒後重試...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    
            except Exception as e:
                logger.error(f"獲取天氣資料時發生未知錯誤: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(retry_delay)
                    retry_delay *= 2
        
        logger.error(f"在 {max_retries} 次嘗試後仍無法獲取天氣資料")
        return None
        
    def get_backup_weather(self):
        """
        當無法從 API 獲取天氣資料時，提供基本預設值
        作為備用方案，以確保用戶至少能看到一些天氣資訊
        """
        today = datetime.now().strftime("%Y-%m-%d")
        logger.info("使用備用天氣資料")
        
        return {
            "district": "桃園區",
            "min_temp": "25",
            "max_temp": "30",
            "temp": "28",
            "rain_prob": "20",
            "humidity": "70",
            "weather": "多雲時晴",
            "comfort": "舒適",
            "description": "今日天氣多雲時晴，氣溫介於 25°C 至 30°C，降雨機率 20%。"
        }

if __name__ == "__main__":
    # 測試天氣服務
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    weather_service = WeatherService(os.getenv('CWB_API_KEY'))
    
    # 嘗試獲取真實天氣資料
    weather = weather_service.get_taoyuan_weather()
    
    # 如果無法獲取真實天氣數據，使用備用數據
    if not weather:
        weather = weather_service.get_backup_weather()
    
    if weather:
        print(f"桃園市今日天氣:")
        print(f"地區: {weather['district']}")
        print(f"溫度: {weather['min_temp']}°C - {weather['max_temp']}°C")
        print(f"降雨機率: {weather['rain_prob']}%")
        print(f"天氣狀況: {weather['weather']}")
        print(f"描述: {weather['description']}")
    else:
        print("無法提供天氣資料")
