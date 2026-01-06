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
    使用 Stable Diffusion 生成圖片 (透過 Hugging Face API)
    
    Args:
        prompt: 圖片描述提示詞
        
    Returns:
        圖片本地路徑 或 None
    """
    try:
        # 使用 Hugging Face 的 Stable Diffusion API
        hf_token = os.getenv('HUGGINGFACE_TOKEN')
        
        # 使用新的 Hugging Face 推理端點
        api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        
        headers = {}
        if hf_token:
            headers["Authorization"] = f"Bearer {hf_token}"
            logger.info("使用 Hugging Face Token")
        else:
            logger.info("使用 Hugging Face 公開推理 API")
        
        logger.info(f"開始生成圖片，提示詞: {prompt[:50]}...")
        
        # 發送請求
        response = requests.post(
            api_url,
            headers=headers,
            json={"inputs": prompt},
            timeout=60
        )
        
        # 如果 API 返回 410 或其他錯誤，嘗試使用備用端點
        if response.status_code == 410 or response.status_code >= 400:
            logger.warning(f"主要端點失敗 ({response.status_code}): {response.text}")
            logger.info("嘗試使用 Black Forest Labs FLUX 模型")
            
            # 使用更新且免費的 FLUX 模型
            api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
            
            response = requests.post(
                api_url,
                headers=headers,
                json={"inputs": prompt},
                timeout=60
            )
        
        if response.status_code == 200:
            # 保存圖片到臨時目錄
            temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            import time
            timestamp = int(time.time())
            image_filename = f"generated_{timestamp}.png"
            image_path = os.path.join(temp_dir, image_filename)
            
            # 保存圖片
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"圖片已生成並保存到: {image_path}")
            return image_path
        else:
            logger.error(f"API 請求失敗: {response.status_code} - {response.text}")
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
