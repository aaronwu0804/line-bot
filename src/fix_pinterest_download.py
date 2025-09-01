#!/usr/bin/env python3
# filepath: /Users/al02451008/Documents/code/morning-post/src/fix_pinterest_download.py
"""
修復 Pinterest 圖片下載功能，使用更穩定的方法
"""

import os
import sys
import logging
import random
import requests
import time
from datetime import datetime
import shutil

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pinterest 搜索關鍵詞列表
SEARCH_TERMS = [
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

# 使用 Unsplash API 獲取相關圖片的替代方案
def get_unsplash_image(search_term):
    """使用 Unsplash API 獲取圖片"""
    try:
        # 使用 Unsplash 無需 API key 的搜索方式
        url = f"https://source.unsplash.com/1200x800/?{requests.utils.quote(search_term)}"
        logger.info(f"使用 Unsplash 搜索圖片: {search_term}")
        
        response = requests.get(url, allow_redirects=True, timeout=15)
        final_url = response.url
        logger.info(f"獲取到 Unsplash 圖片 URL: {final_url}")
        
        # 下載圖片
        if response.status_code == 200:
            # 確保 images 目錄存在
            images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images')
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
                logger.info(f"創建圖片目錄: {images_dir}")
                
            # 保存圖片
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"morning_image_{timestamp}.jpg"
            filepath = os.path.join(images_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
                
            logger.info(f"圖片已保存為: {filepath}")
            return filepath
        else:
            logger.error(f"下載圖片失敗，狀態碼: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"從 Unsplash 獲取圖片時發生錯誤: {str(e)}")
        return None

# 使用 Pixabay API 獲取相關圖片的替代方案
def get_pixabay_image(search_term):
    """使用 Pixabay API 獲取圖片"""
    try:
        # 使用免費 Pixabay API
        # 免費 API key，僅用於測試，正式環境請申請自己的 key
        api_key = "35803601-a6c569c424a9e57ec5f2e0f4f"
        url = f"https://pixabay.com/api/?key={api_key}&q={requests.utils.quote(search_term)}&image_type=photo&orientation=horizontal&min_width=800"
        
        logger.info(f"使用 Pixabay 搜索圖片: {search_term}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['totalHits'] > 0:
                # 隨機選擇一張圖片
                image = random.choice(data['hits'])
                image_url = image['largeImageURL']
                
                logger.info(f"獲取到 Pixabay 圖片 URL: {image_url}")
                
                # 下載圖片
                img_response = requests.get(image_url, timeout=10)
                if img_response.status_code == 200:
                    # 確保 images 目錄存在
                    images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images')
                    if not os.path.exists(images_dir):
                        os.makedirs(images_dir)
                        logger.info(f"創建圖片目錄: {images_dir}")
                    
                    # 保存圖片
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"morning_image_{timestamp}.jpg"
                    filepath = os.path.join(images_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                        
                    logger.info(f"圖片已保存為: {filepath}")
                    return filepath
                else:
                    logger.error(f"下載圖片失敗，狀態碼: {img_response.status_code}")
            else:
                logger.warning(f"未找到匹配的圖片: {search_term}")
        else:
            logger.error(f"API 請求失敗，狀態碼: {response.status_code}")
            
        return None
    except Exception as e:
        logger.error(f"從 Pixabay 獲取圖片時發生錯誤: {str(e)}")
        return None

def get_pinterest_image_new():
    """獲取 Pinterest 圖片（改進版）"""
    # 隨機選擇搜索詞
    search_term = random.choice(SEARCH_TERMS)
    logger.info(f"選擇了搜索詞: {search_term}")
    
    # 先嘗試從 Unsplash 獲取
    img_path = get_unsplash_image(search_term)
    if img_path and os.path.isfile(img_path) and os.path.getsize(img_path) > 10000:  # 確保文件大於 10KB
        logger.info(f"成功從 Unsplash 獲取圖片: {img_path}")
        return img_path
        
    # 如果 Unsplash 失敗，嘗試從 Pixabay 獲取
    logger.info("Unsplash 獲取失敗，嘗試從 Pixabay 獲取")
    img_path = get_pixabay_image(search_term)
    if img_path and os.path.isfile(img_path) and os.path.getsize(img_path) > 10000:
        logger.info(f"成功從 Pixabay 獲取圖片: {img_path}")
        return img_path
    
    # 所有嘗試都失敗
    logger.error("所有圖片獲取方式都失敗")
    return None

def update_pinterest_module():
    """更新 test_pinterest.py 模組，使用新的圖片獲取方法"""
    src_dir = os.path.dirname(os.path.abspath(__file__))
    pinterest_py = os.path.join(src_dir, 'test_pinterest.py')
    
    # 如果文件存在，先備份
    if os.path.exists(pinterest_py):
        backup_path = f"{pinterest_py}.bak.{int(time.time())}"
        shutil.copy2(pinterest_py, backup_path)
        logger.info(f"原 test_pinterest.py 已備份到 {backup_path}")
    
    # 讀取當前文件內容
    with open(__file__, 'r', encoding='utf-8') as f:
        this_content = f.read()
    
    # 提取所需函數
    import re
    functions = []
    functions.append("# filepath: /Users/al02451008/Documents/code/morning-post/src/test_pinterest.py")
    functions.append('"""')
    functions.append("從網絡獲取早安圖片 (改進版)")
    functions.append('"""')
    functions.append("")
    functions.append("import os")
    functions.append("import logging")
    functions.append("from datetime import datetime")
    functions.append("import requests")
    functions.append("import random")
    functions.append("import time")
    functions.append("")
    
    # 添加日誌設置
    functions.append("""# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pinterest_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
""")
    
    # 提取搜索詞列表
    search_terms_pattern = r"SEARCH_TERMS = \[(.*?)\]"
    search_terms_match = re.search(search_terms_pattern, this_content, re.DOTALL)
    if search_terms_match:
        functions.append(f"SEARCH_TERMS = [{search_terms_match.group(1)}]")
    
    # 提取 Unsplash 函數
    unsplash_pattern = r"def get_unsplash_image\(.*?\):(.*?)(?=def |$)"
    unsplash_match = re.search(unsplash_pattern, this_content, re.DOTALL)
    if unsplash_match:
        functions.append(f"def get_unsplash_image(search_term):{unsplash_match.group(1)}")
    
    # 提取 Pixabay 函數
    pixabay_pattern = r"def get_pixabay_image\(.*?\):(.*?)(?=def |$)"
    pixabay_match = re.search(pixabay_pattern, this_content, re.DOTALL)
    if pixabay_match:
        functions.append(f"def get_pixabay_image(search_term):{pixabay_match.group(1)}")
    
    # 重命名主函數
    new_func_pattern = r"def get_pinterest_image_new\(.*?\):(.*?)(?=def |$)"
    new_func_match = re.search(new_func_pattern, this_content, re.DOTALL)
    if new_func_match:
        functions.append(f"def get_pinterest_image():{new_func_match.group(1)}")
    
    # 添加主程式區塊
    functions.append("""
if __name__ == "__main__":
    image_url = get_pinterest_image()
    if image_url:
        print(f"成功獲取圖片: {image_url}")
    else:
        print("獲取圖片失敗")
""")
    
    # 寫入新檔案
    with open(pinterest_py, 'w', encoding='utf-8') as f:
        f.write("\n".join(functions))
    
    logger.info(f"已更新 {pinterest_py}")
    return True

if __name__ == "__main__":
    logger.info("開始修復 Pinterest 圖片下載功能...")
    
    # 測試新的圖片獲取方法
    logger.info("測試新的圖片獲取方法...")
    image_path = get_pinterest_image_new()
    
    if image_path:
        logger.info(f"測試成功！圖片已保存到: {image_path}")
        logger.info(f"檔案大小: {os.path.getsize(image_path)/1024:.2f} KB")
        
        # 更新模組
        if update_pinterest_module():
            logger.info("成功更新 test_pinterest.py 模組")
            print("\n修復成功！Pinterest 圖片下載功能已更新為使用 Unsplash 和 Pixabay API。")
            print(f"測試圖片已保存到: {image_path}")
        else:
            logger.error("更新 test_pinterest.py 模組失敗")
    else:
        logger.error("測試失敗，無法獲取圖片")
