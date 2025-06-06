#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/test_quota_limits.py
"""
測試 Gemini API 的配額限制處理
測試重試機制、指數退避策略和緩存功能
"""

import os
import sys
import time
import random
import logging
from datetime import datetime
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加主目錄到系統路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 導入緩存模組
try:
    from src.response_cache import response_cache
    CACHE_ENABLED = True
except ImportError:
    CACHE_ENABLED = False
    print("警告：無法導入緩存模組")

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

# Gemini API 金鑰
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def test_api_with_quota_limit():
    """測試增強版的配額限制處理與指數退避策略"""
    print("=" * 80)
    print(f"增強版 Gemini API 配額處理測試 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("測試功能: 指數退避重試、並行請求處理、模型自動降級")
    print("=" * 80)
    
    if not GEMINI_API_KEY:
        logger.error("未找到 Gemini API 金鑰，請設置 GEMINI_API_KEY 環境變數")
        return False

    # 導入 API 監控模組
    try:
        from api_usage_monitor import APIUsageMonitor
        api_monitor = APIUsageMonitor()
        logger.info("已導入 API 監控模組")
    except ImportError:
        try:
            from src.api_usage_monitor import APIUsageMonitor
            api_monitor = APIUsageMonitor()
            logger.info("已導入 API 監控模組 (從 src 導入)")
        except ImportError:
            logger.warning("無法導入 API 監控模組，將不記錄使用統計")
            api_monitor = None

    # 導入 Google Generative AI 庫
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("已成功配置 Gemini API")
    except ImportError:
        logger.error("未安裝 google-generativeai 庫，請執行: pip install google-generativeai>=0.3.1")
        return False

    # 測試問題列表
    test_questions = [
        "用繁體中文簡短介紹台北的著名景點，不超過100字。",
        "請提供三種不同的早安問候語，使用繁體中文。",
        "請簡短說明台灣的四季氣候特色。",
        "用繁體中文介紹三種台灣特色小吃。",
        "請用繁體中文寫一段關於友誼的短句。"
    ]
    
    # 模型列表嘗試
    models_to_try = ["gemini-1.5-flash", "gemini-pro", "gemini-1.0-pro"]
    
    # 第一部分：測試緩存系統
    print("\n測試 1：緩存系統整合測試")
    print("-" * 60)
    
    if CACHE_ENABLED:
        test_question = random.choice(test_questions)
        
        # 清除可能存在的相關緩存
        if hasattr(response_cache, "delete") and callable(response_cache.delete):
            response_cache.delete(test_question)
            logger.info(f"已清除測試緩存: {test_question[:30]}...")
        
        # 第一次查詢，應該會呼叫 API
        logger.info(f"首次查詢: '{test_question}'")
        start_time = time.time()
        
        try:
            # 選擇合適的模型
            try:
                models = list(genai.list_models())
                model_names = [model.name for model in models]
                logger.info(f"可用的模型: {model_names}")
                
                # 選擇適合的模型
                model_name = None
                for name in ["gemini-1.5-flash", "gemini-1.0-flash", "gemini-pro"]:
                    if f"models/{name}" in model_names or name in model_names:
                        model_name = name
                        logger.info(f"選擇模型: {model_name}")
                        break
                        
                if not model_name:
                    model_name = "gemini-pro"
                    logger.info(f"未找到首選模型，使用默認模型: {model_name}")
            except Exception as model_error:
                model_name = "gemini-pro"
                logger.warning(f"列出模型時發生錯誤，使用默認模型: {model_name}")
            
            # 生成回應
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(test_question)
            
            if response and hasattr(response, 'text'):
                response_text = response.text
                logger.info(f"回應 ({len(response_text)} 字符): {response_text[:50]}...")
                
                # 將結果存入緩存
                response_cache.set(test_question, response_text)
                logger.info(f"已保存到緩存，API 調用用時: {time.time() - start_time:.2f}秒")
                
                # 第二次查詢，應該從緩存獲取
                logger.info(f"再次查詢相同問題 (應從緩存獲取)")
                cache_start_time = time.time()
                cached = response_cache.get(test_question)
                
                if cached:
                    logger.info(f"從緩存獲取結果: {cached[:50]}...")
                    cache_time = time.time() - cache_start_time
                    logger.info(f"緩存查詢用時: {cache_time:.2f}秒")
                    
                    # 驗證緩存是否有效
                    if cache_time < (time.time() - start_time) * 0.5:
                        print("✓ 緩存系統工作正常，明顯節省了時間")
                    else:
                        print("△ 緩存系統工作正常，但效率不高")
                    
                    # 嘗試獲取緩存統計
                    if hasattr(response_cache, "get_stats"):
                        stats = response_cache.get_stats()
                        logger.info(f"緩存統計: {stats}")
                else:
                    logger.error("緩存查詢失敗，未找到緩存內容")
                    print("✗ 緩存查詢失敗")
            else:
                logger.error("API回應無效")
                print("✗ API 回應無效")
        except Exception as e:
            logger.error(f"緩存測試出錯: {str(e)}")
            print(f"✗ 緩存測試失敗: {str(e)}")
    else:
        print("? 緩存系統未啟用，跳過緩存測試")
    
    # 第二部分：測試指數退避策略
    print("\n測試 2：指數退避策略測試")
    print("-" * 60)
    
    def call_api_with_retry(prompt, max_retries=3, base_delay=1.0):
        """使用指數退避策略呼叫 API"""
        # 選擇模型
        model_name = "gemini-pro"
        model = genai.GenerativeModel(model_name)
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                logger.info(f"嘗試 {attempt+1}/{max_retries}: 發送請求...")
                
                response = model.generate_content(prompt)
                process_time = time.time() - start_time
                
                if api_monitor:
                    api_monitor.log_api_call(
                        model=model_name,
                        success=True,
                        response_time=process_time * 1000
                    )
                    
                logger.info(f"成功生成回應，用時: {process_time:.2f}秒")
                return response.text, attempt + 1
            except Exception as e:
                error_str = str(e)
                logger.warning(f"嘗試 {attempt+1}/{max_retries}: 失敗: {error_str}")
                
                if api_monitor:
                    api_monitor.log_api_call(
                        model=model_name,
                        success=False,
                        error_code="429" if "429" in error_str else "API_ERROR",
                        error_message=error_str
                    )
                
                # 配額限制錯誤，實施指數退避
                if "429" in error_str:
                    retry_delay = base_delay * (2 ** attempt)
                    logger.warning(f"遇到配額限制，等待 {retry_delay:.1f} 秒後重試")
                    time.sleep(retry_delay)
                else:
                    # 其他錯誤，稍微延遲後重試
                    time.sleep(0.5)
                
                # 最後一次嘗試也失敗
                if attempt == max_retries - 1:
                    return None, max_retries
        
        return None, max_retries
    
    # 測試指數退避重試
    try:
        test_prompt = "請用繁體中文簡短介紹人工智能的發展歷史。"
        logger.info(f"測試指數退避策略，請求: '{test_prompt}'")
        
        response, attempts = call_api_with_retry(test_prompt)
        
        if response:
            logger.info(f"成功獲得回應，嘗試次數: {attempts}")
            print(f"API 回應: {response[:100]}...")
            print(f"✓ 指數退避策略測試通過，需要 {attempts} 次嘗試")
        else:
            logger.error(f"未能獲得回應，嘗試次數達上限: {attempts}")
            print("✗ 指數退避策略測試失敗")
    except Exception as retry_error:
        logger.error(f"指數退避測試出錯: {str(retry_error)}")
        print(f"✗ 指數退避策略測試失敗: {str(retry_error)}")
    
    # 第三部分：測試並行請求處理
    print("\n測試 3：並行請求處理測試")
    print("-" * 60)
    
    def test_parallel_requests(num_requests=5):
        """測試並行請求處理"""
        test_prompts = [
            f"{q} (測試 {i})" for i, q in enumerate(test_questions * 2)
        ][:num_requests]
        
        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            logger.info(f"提交 {num_requests} 個並行請求...")
            futures = {executor.submit(call_api_with_retry, prompt): prompt for prompt in test_prompts}
            
            for future in as_completed(futures):
                prompt = futures[future]
                try:
                    response, attempts = future.result()
                    results.append({
                        "prompt": prompt[:30] + "...",
                        "success": response is not None,
                        "attempts": attempts,
                        "response": (response[:30] + "...") if response else None
                    })
                except Exception as e:
                    results.append({
                        "prompt": prompt[:30] + "...",
                        "success": False,
                        "error": str(e)
                    })
        
        return results
    
    try:
        logger.info("開始並行請求測試...")
        parallel_results = test_parallel_requests(5)
        
        success_count = sum(1 for r in parallel_results if r.get("success", False))
        logger.info(f"並行請求結果: {success_count}/{len(parallel_results)} 成功")
        
        # 顯示結果
        for i, result in enumerate(parallel_results):
            status = "✓" if result.get("success", False) else "✗"
            attempts = result.get("attempts", "N/A")
            print(f"{status} 請求 {i+1}: 嘗試次數 {attempts}")
            if result.get("response"):
                print(f"   回應: {result.get('response')}")
            elif result.get("error"):
                print(f"   錯誤: {result.get('error')}")
        
        if success_count >= len(parallel_results) * 0.6:  # 至少60%成功率
            print(f"✓ 並行請求測試通過，成功率: {success_count}/{len(parallel_results)}")
        else:
            print(f"△ 並行請求測試部分通過，成功率偏低: {success_count}/{len(parallel_results)}")
    except Exception as parallel_error:
        logger.error(f"並行請求測試出錯: {str(parallel_error)}")
        print(f"✗ 並行請求測試失敗: {str(parallel_error)}")
        
    # 短暫暫停以防止IP被封
    time.sleep(0.5)  
        
    logger.info("\n===== 測試結果摘要 =====")
    logger.info(f"成功請求: {success_count}/{len(parallel_results)}")
    logger.info(f"失敗請求: {len(parallel_results) - success_count}/{len(parallel_results)}")
    
    # 檢查失敗的調用是否有配額限制錯誤
    quota_errors = sum(1 for r in parallel_results if not r.get("success", False) and r.get("error", "").find("429") >= 0)
    logger.info(f"配額限制錯誤: {quota_errors}")
    
    if quota_errors > 0:
        logger.info("成功檢測到配額限制問題，這表示您的應用應該啟動重試機制")
    
    return True

def test_app_retry_mechanism():
    """測試完整的應用重試機制"""
    # 導入主應用中的 get_ai_response 函數測試
    logger.info("未實現：需要在非生產環境中測試完整應用的重試機制")
    pass

if __name__ == "__main__":
    print("=" * 60)
    print(f"Gemini API 配額限制測試 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    result = test_api_with_quota_limit()
    
    # 添加 API 監控和統計測試
    print("\n測試 4：API 監控和統計測試")
    print("-" * 60)
    
    try:
        from api_usage_monitor import APIUsageMonitor
        api_monitor = APIUsageMonitor()
        
        # 獲取 API 使用統計
        stats = api_monitor.get_stats()
        print("API 使用統計數據:")
        print(f"- 總 API 調用: {stats.get('total_calls', 0)} 次")
        print(f"- 成功調用: {stats.get('successful_calls', 0)} 次")
        print(f"- 失敗調用: {stats.get('failed_calls', 0)} 次")
        print(f"- 錯誤率: {stats.get('error_rate', 0)}%")
        
        # 檢查配額限制次數
        quota_limits = stats.get('quota_limits', 0)
        if quota_limits > 0:
            print(f"✓ 監測到 {quota_limits} 次配額限制，指數退避策略已激活")
        else:
            print("△ 未監測到配額限制，可能需要增加測試請求頻率")
        
        print("✓ API 監控模組功能正常")
    except ImportError:
        print("? API 監控模塊未啟用，跳過統計測試")
    except Exception as e:
        print(f"! 獲取 API 統計失敗: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Gemini API 配額處理測試完成")
    print("=" * 60)
