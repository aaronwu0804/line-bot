import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WeatherService:
    """天氣服務類"""
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore"
        
    def get_taoyuan_weather(self, max_retries=3, timeout=10):
        """獲取桃園市天氣預報 (使用 F-D0047-091 API)，包含重試機制"""
        retry_count = 0
        
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
                    continue
                
                data = response.json()
            if "records" not in data or "locations" not in data["records"]:
                logger.error("回應資料格式錯誤")
                return None
            
            # 解析天氣資料
            locations = data["records"]["locations"][0]["location"]
            if not locations:
                logger.error("找不到桃園市的天氣資料")
                return None
            
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
                return result
            else:
                logger.error("天氣資料不完整")
                return None
                
        except Exception as e:
            logger.error(f"獲取天氣資料時發生錯誤: {str(e)}")
            return None

if __name__ == "__main__":
    # 測試天氣服務
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    weather_service = WeatherService(os.getenv('CWB_API_KEY'))
    weather = weather_service.get_taoyuan_weather()
    
    if weather:
        print(f"桃園市今日天氣:")
        print(f"溫度: {weather['min_temp']}°C - {weather['max_temp']}°C")
        print(f"降雨機率: {weather['rain_prob']}%")
    else:
        print("無法獲取天氣資料")
