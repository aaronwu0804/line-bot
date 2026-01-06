#!/usr/bin/env python3
"""
圖片生成服務
使用 Gemini 的 Imagen 3 模型生成圖片
"""

import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

def generate_image_with_gemini(prompt: str) -> Optional[str]:
    """
    使用 Gemini Imagen 3 生成圖片
    
    Args:
        prompt: 圖片描述提示詞
        
    Returns:
        圖片 URL 或 None
    """
    try:
        import google.generativeai as genai
        
        # 初始化 Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("未設定 GEMINI_API_KEY 環境變數")
            return None
            
        genai.configure(api_key=api_key)
        
        # 使用 Imagen 3 模型
        model = genai.GenerativeModel('imagen-3.0-generate-001')
        
        logger.info(f"開始生成圖片，提示詞: {prompt[:50]}...")
        
        # 生成圖片
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            safety_filter_level="block_only_high",
            person_generation="allow_adult",
            aspect_ratio="1:1"
        )
        
        # 獲取圖片
        if response.images:
            image = response.images[0]
            
            # 將圖片保存到臨時文件
            temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            import time
            timestamp = int(time.time())
            image_filename = f"generated_{timestamp}.png"
            image_path = os.path.join(temp_dir, image_filename)
            
            # 保存圖片
            image._pil_image.save(image_path)
            logger.info(f"圖片已保存到: {image_path}")
            
            return image_path
        else:
            logger.error("API 返回但沒有生成圖片")
            return None
            
    except Exception as e:
        logger.error(f"生成圖片時發生錯誤: {str(e)}")
        return None


def upload_image_to_imgur(image_path: str) -> Optional[str]:
    """
    上傳圖片到 Imgur
    
    Args:
        image_path: 本地圖片路徑
        
    Returns:
        Imgur 圖片 URL 或 None
    """
    try:
        imgur_client_id = os.getenv('IMGUR_CLIENT_ID')
        if not imgur_client_id:
            logger.warning("未設定 IMGUR_CLIENT_ID，將返回本地路徑")
            return None
        
        headers = {'Authorization': f'Client-ID {imgur_client_id}'}
        
        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}
            response = requests.post(
                'https://api.imgur.com/3/image',
                headers=headers,
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            image_url = data['data']['link']
            logger.info(f"圖片已上傳到 Imgur: {image_url}")
            return image_url
        else:
            logger.error(f"上傳到 Imgur 失敗: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"上傳圖片到 Imgur 時發生錯誤: {str(e)}")
        return None


# 測試功能
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    test_prompt = "A cute cat playing with a ball of yarn"
    print(f"測試生成圖片: {test_prompt}")
    
    image_path = generate_image_with_gemini(test_prompt)
    if image_path:
        print(f"✅ 圖片生成成功: {image_path}")
        
        # 嘗試上傳到 Imgur
        image_url = upload_image_to_imgur(image_path)
        if image_url:
            print(f"✅ 圖片已上傳: {image_url}")
    else:
        print("❌ 圖片生成失敗")
