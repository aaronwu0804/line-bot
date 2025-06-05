import os
import logging
from datetime import datetime
import requests
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pinterest_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_pinterest_image():
    """從 Pinterest 獲取早安圖片"""
    try:
        # 設定 Chrome 選項
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 無頭模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')  # 設置更大的窗口尺寸

        # 初始化瀏覽器
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        # 定義搜索關鍵字列表（包含中英文）
        search_terms = [
            "早安 日出 美景",
            "早安 花朵 春天",
            "早安 自然風景",
            "早安 陽光 光芒",
            "早安 藍天 白雲",
            "早安 勵志 加油",
            "早安 山水 風景",
            "早安 湖泊 寧靜",
            "早安 海邊 日出",
            "早安 櫻花 春天",
            "早安 森林 陽光",
            "早安 花海 美景",
            "早安 海洋 日出",
            "早安 花園 美景",
            "早安 山嵐 霧景",
            "早安 禪意 花園",
            "早安 咖啡 小語",
            "早安 彩虹 自然",
            "早安 瀑布 寧靜",
            "早安 正能量 語錄",
            "早安 蓮花 禪意",
            "早安 櫻花 日本",
            "早安 楓葉 秋天",
            "早安 雲海 山景",
            "早安 薰衣草 花海",
            # 保留一些英文關鍵字作為備選
            "good morning sunrise beautiful",
            "good morning nature peaceful",
            "morning cherry blossom",
            "morning zen garden",
            "morning lotus flower"
        ]
        
        # 隨機選擇一個搜索詞
        search_term = random.choice(search_terms)
        encoded_search = requests.utils.quote(search_term)
        url = f"https://www.pinterest.com/search/pins/?q={encoded_search}"
        
        logger.info(f"正在搜索 Pinterest 圖片: {search_term}")
        logger.info(f"訪問 URL: {url}")
        
        # 訪問頁面
        driver.get(url)
        
        # 滾動頁面以加載更多圖片
        for _ in range(3):  # 滾動3次
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # 每次滾動後等待3秒
        
        # 最後再等待一下確保圖片都加載完成
        time.sleep(5)
        
        # 尋找所有圖片元素
        images = driver.find_elements(By.CSS_SELECTOR, 'img[src*="pinimg.com"]')
        logger.info(f"找到 {len(images)} 張圖片")
        
        # 過濾並獲取高質量圖片，放寬條件
        image_urls = []
        for img in images:
            src = img.get_attribute('src')
            logger.debug(f"檢查圖片 URL: {src}")
            if src and 'pinimg.com' in src:
                # 圖片大小檢查
                is_tiny = any(size in src for size in ['60x60', '150x150', '75x75'])
                if not is_tiny:
                    # 優先選擇原始大小的圖片
                    orig_src = src
                    if '236x' in src:
                        orig_src = src.replace('/236x/', '/736x/')
                    elif '474x' in src:
                        orig_src = src.replace('/474x/', '/originals/')
                    elif '736x' in src:
                        orig_src = src.replace('/736x/', '/originals/')
                    
                    # 檢查圖片質量並避免重複
                    if orig_src not in image_urls:
                        image_urls.append(orig_src)
                        logger.debug(f"添加合格圖片: {orig_src}")
        
        logger.info(f"找到 {len(image_urls)} 張合格圖片")
        
        if image_urls:
            # 隨機選擇一張圖片
            image_url = random.choice(image_urls)
            logger.info(f"選中的圖片 URL: {image_url}")
            
            # 下載圖片
            response = requests.get(image_url, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"morning_image_{timestamp}.png"
                filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images', filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                logger.info(f"圖片已保存為: {filepath}")
                return image_url
            else:
                logger.error(f"下載圖片失敗: {response.status_code}")
                return None
        else:
            logger.error("沒有找到合適的圖片")
            return None
            
    except Exception as e:
        logger.error(f"獲取圖片時發生錯誤: {str(e)}")
        return None
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    image_url = get_pinterest_image()
    if image_url:
        print(f"成功獲取圖片: {image_url}")
    else:
        print("獲取圖片失敗")
