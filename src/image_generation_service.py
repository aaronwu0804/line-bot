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
    使用圖片生成 API 生成圖片並上傳到 Imgur
    
    Args:
        prompt: 圖片描述提示詞
        
    Returns:
        Imgur 圖片 URL 或 None
    """
    try:
        # 使用 Pollinations AI 免費圖片生成 API
        logger.info(f"開始生成圖片，提示詞: {prompt[:50]}...")
        
        import urllib.parse
        
        # 縮短提示詞
        max_prompt_length = 100
        if len(prompt) > max_prompt_length:
            prompt = prompt[:max_prompt_length]
            logger.info(f"提示詞過長，已截斷為: {prompt}")
        
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        logger.info(f"請求圖片生成: {image_url[:100]}...")
        
        # 下載生成的圖片 (等待生成完成)
        response = requests.get(image_url, timeout=60)
        
        if response.status_code == 200:
            logger.info(f"圖片下載成功，大小: {len(response.content)} bytes")
            
            # 上傳到 Imgur
            imgur_url = upload_image_to_imgur_from_bytes(response.content)
            
            if imgur_url:
                logger.info(f"圖片已上傳到 Imgur: {imgur_url}")
                return imgur_url
            else:
                logger.error("上傳到 Imgur 失敗")
                return None
        else:
            logger.error(f"圖片生成失敗: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"生成圖片時發生錯誤: {str(e)}")
        return None


def upload_image_to_imgur_from_bytes(image_data: bytes) -> Optional[str]:
    """
    上傳圖片數據到 Imgur
    
    Args:
        image_data: 圖片二進制數據
        
    Returns:
        Imgur 圖片 URL 或 None
    """
    try:
        # 使用匿名上傳 (不需要 Client ID)
        import base64
        
        # 將圖片數據轉為 base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        # 使用 Imgur 的匿名上傳 API
        headers = {'Authorization': 'Client-ID 546c25a59c58ad7'}  # 公開的匿名 Client ID
        
        response = requests.post(
            'https://api.imgur.com/3/image',
            headers=headers,
            data={'image': image_b64},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            image_url = data['data']['link']
            logger.info(f"圖片已上傳到 Imgur: {image_url}")
            return image_url
        else:
            logger.error(f"上傳到 Imgur 失敗: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"上傳圖片到 Imgur 時發生錯誤: {str(e)}")
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
