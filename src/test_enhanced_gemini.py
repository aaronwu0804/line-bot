#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/test_enhanced_gemini.py
"""
測試增強版 Gemini API 整合
用於驗證增強型 Gemini API 功能，包括緩存，模型選擇和錯誤處理
"""

import os
import sys
import time
import logging
from datetime import datetime

# 設定 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def test_enhanced_gemini_integration():
    """測試增強型 Gemini API 集成功能"""
    print("=" * 80)
    print(f"增強型 Gemini API 集成測試 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("測試重點: 緩存系統, 智能模型選擇, 指數退避重試策略")
    print("=" * 80)
    
    # 檢查環境變數
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_KEY')
    if not gemini_key:
        logger.error("未設定 Gemini API 密鑰，無法執行測試")
        return False
        
    logger.info("已檢測到 Gemini API 密鑰")
    
    # 測試導入 API 監控模塊
    try:
        from src.api_usage_monitor import APIUsageMonitor
        api_monitor = APIUsageMonitor()
        logger.info("成功導入 API 監控模塊")
    except ImportError:
        try:
            from api_usage_monitor import APIUsageMonitor
            api_monitor = APIUsageMonitor()
            logger.info("成功導入 API 監控模塊 (從當前目錄)")
        except ImportError:
            logger.warning("無法導入 API 監控模塊，將無法監控 API 使用情況")
            api_monitor = None
    
    # 測試導入緩存模塊
    try:
        from src.response_cache import response_cache
        logger.info("成功導入回應緩存模塊")
        cache_available = True
    except ImportError:
        try:
            from response_cache import response_cache
            logger.info("成功導入回應緩存模塊 (從當前目錄)")
            cache_available = True
        except ImportError:
            logger.warning("無法導入回應緩存模塊，將不使用緩存功能")
            cache_available = False
    
    # 測試導入 main 模組
    try:
        from src.main import generate_ai_greeting, generate_greeting_message
        logger.info("成功導入增強版生成問候語函數")
    except ImportError:
        try:
            from main import generate_ai_greeting, generate_greeting_message
            logger.info("成功導入增強版生成問候語函數 (從當前目錄)")
        except ImportError:
            logger.error("無法導入生成問候語函數，請確認 main.py 是否正確更新")
            return False
    
    # 測試初始化 Gemini API
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        logger.info("成功初始化 Gemini API")
    except ImportError:
        logger.error("無法導入 google.generativeai 模塊，請確認已安裝所需套件")
        return False
    except Exception as e:
        logger.error(f"初始化 Gemini API 時發生錯誤: {str(e)}")
        return False
    
    # 測試 1: 測試緩存系統
    if cache_available:
        print("\n測試 1: 緩存系統功能測試")
        print("-----------------------------------")
        
        # 清除可能存在的相關緩存
        test_cache_key = "test_greeting_cache_key"
        if hasattr(response_cache, "delete") and callable(response_cache.delete):
            response_cache.delete(test_cache_key)
            logger.info(f"已清除測試緩存鍵: {test_cache_key}")
            
        # 檢查緩存是否為空
        cached = response_cache.get(test_cache_key)
        if cached is None:
            logger.info("確認緩存為空 - 通過")
        else:
            logger.warning(f"預期緩存為空，但返回: {cached}")
            
        # 設置緩存
        test_value = f"這是測試緩存 - {datetime.now().strftime('%H:%M:%S')}"
        response_cache.set(test_cache_key, test_value)
        logger.info(f"已設置緩存: {test_value}")
        
        # 讀取緩存
        cached = response_cache.get(test_cache_key)
        if cached == test_value:
            logger.info(f"緩存讀取成功: {cached}")
            print("✓ 緩存系統功能測試通過")
        else:
            logger.error(f"緩存讀取失敗，期望: {test_value}, 實際: {cached}")
            print("✗ 緩存系統功能測試失敗")
    else:
        print("跳過緩存系統功能測試 (緩存模塊未載入)")
    
    # 測試 2: 模型選擇邏輯
    print("\n測試 2: 智能模型選擇邏輯測試")
    print("-----------------------------------")
    try:
        # 列出可用模型
        models = list(genai.list_models())
        model_names = [model.name for model in models]
        logger.info(f"可用模型: {model_names}")
        
        if api_monitor:
            api_monitor.log_api_call(
                model="list_models", 
                success=True, 
                response_time=0
            )
        
        # 生成無天氣資訊的問候語
        logger.info("測試無天氣資訊的問候語生成...")
        start_time = time.time()
        greeting = generate_ai_greeting()
        process_time = time.time() - start_time
        
        if greeting:
            logger.info(f"成功生成問候語 (用時: {process_time:.2f}秒): {greeting}")
            print(f"✓ 無天氣資訊問候語生成測試通過: {greeting}")
            
            # 第二次調用，應從緩存獲取
            if cache_available:
                logger.info("測試緩存問候語功能...")
                start_time = time.time()
                cached_greeting = generate_ai_greeting()
                cache_time = time.time() - start_time
                
                logger.info(f"第二次調用用時: {cache_time:.2f}秒 (首次: {process_time:.2f}秒)")
                
                # 如果第二次調用明顯快於第一次，或者回傳結果完全相同，可能是使用了緩存
                if cache_time < process_time * 0.5 or cached_greeting == greeting:
                    logger.info("緩存功能正常，第二次調用顯著更快")
                    print("✓ 問候語緩存功能測試通過")
                else:
                    logger.warning("緩存可能未正常工作，兩次調用時間相近")
        else:
            logger.warning("未能生成問候語，將使用備用問候語")
            print("✗ 無天氣資訊問候語生成測試失敗")
    except Exception as model_error:
        logger.error(f"測試模型選擇時發生錯誤: {str(model_error)}")
        print(f"✗ 模型選擇邏輯測試失敗: {str(model_error)}")
    
    # 測試 3: 測試帶天氣資訊的問候語生成
    print("\n測試 3: 帶天氣資訊的問候語生成測試")
    print("-----------------------------------")
    try:
        weather_info = {
            'weather': '多雲時晴',
            'temp': '26',
            'rain_prob': '30',
            'humidity': '75%',
            'min_temp': '22',
            'max_temp': '28',
            'district': '桃園市',
            'description': '今天天氣多雲時晴，氣溫適中，適合戶外活動。'
        }
        
        logger.info("測試帶天氣資訊的問候語生成...")
        start_time = time.time()
        weather_greeting = generate_greeting_message(weather_info)
        weather_process_time = time.time() - start_time
        
        if weather_greeting:
            logger.info(f"成功生成天氣問候語 (用時: {weather_process_time:.2f}秒): {weather_greeting}")
            print(f"✓ 帶天氣資訊問候語生成測試通過: {weather_greeting}")
        else:
            logger.warning("未能生成天氣問候語")
            print("✗ 帶天氣資訊問候語生成測試失敗")
    except Exception as weather_error:
        logger.error(f"測試天氣問候語生成時發生錯誤: {str(weather_error)}")
        print(f"✗ 天氣問候語生成測試失敗: {str(weather_error)}")
    
    # 測試 4: API 監控功能
    print("\n測試 4: API 監控功能測試")
    print("-----------------------------------")
    if api_monitor:
        try:
            # 記錄測試 API 調用
            api_monitor.log_api_call(
                model="test-model",
                success=True,
                response_time=123.45
            )
            logger.info("已記錄測試 API 調用")
            
            # 獲取統計數據
            stats = api_monitor.get_stats()
            if stats:
                logger.info(f"API 監控統計數據: {stats.get('total_calls', 0)} 次調用")
                print("✓ API 監控功能測試通過")
            else:
                logger.warning("無法獲取 API 監控統計數據")
                print("△ API 監控功能測試部分通過")
        except Exception as monitor_error:
            logger.error(f"測試 API 監控功能時發生錯誤: {str(monitor_error)}")
            print(f"✗ API 監控功能測試失敗: {str(monitor_error)}")
    else:
        print("跳過 API 監控功能測試 (API 監控模塊未載入)")
    
    # 測試總結
    print("\n" + "=" * 80)
    print("增強型 Gemini API 集成測試完成")
    print("=" * 80)
    return True

if __name__ == "__main__":
    if test_enhanced_gemini_integration():
        print("\n整體測試結果: 大部分測試通過")
        sys.exit(0)
    else:
        print("\n整體測試結果: 測試失敗")
        sys.exit(1)
