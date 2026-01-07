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
    使用圖片生成 API 生成圖片
    
    Args:
        prompt: 圖片描述提示詞
        
    Returns:
        圖片 URL
    """
    try:
        logger.info(f"開始生成圖片，提示詞: {prompt[:50]}...")
        
        # 優先使用 Hugging Face Inference API (免費,高品質)
        logger.info("使用 Hugging Face Inference API...")
        image_url = generate_with_huggingface(prompt)
        if image_url:
            return image_url
        
        # 備用方案: Craiyon (免費無需認證)
        logger.info("Hugging Face 失敗,嘗試 Craiyon...")
        image_url = generate_with_craiyon(prompt)
        if image_url:
            return image_url
        
        # 最後備用: Pollinations
        logger.info("Craiyon 失敗,嘗試 Pollinations...")
        image_url = generate_with_pollinations(prompt)
        if image_url:
            return image_url
        
        logger.error("所有圖片生成服務均失敗")
        return None
            
    except Exception as e:
        logger.error(f"生成圖片時發生錯誤: {str(e)}")
        return None


def generate_with_replicate(prompt: str) -> Optional[str]:
    """
    使用 Replicate API 生成高品質圖片 (FLUX schnell)
    """
    try:
        # Replicate 的公開預測 API
        api_url = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
        
        payload = {
            "input": {
                "prompt": prompt,
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_format": "jpg",
                "output_quality": 90
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Prefer": "wait"  # 等待結果返回
        }
        
        logger.info("發送請求到 Replicate...")
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            
            # 獲取圖片 URL
            if 'output' in result and result['output']:
                image_url = result['output'][0] if isinstance(result['output'], list) else result['output']
                logger.info(f"Replicate 生成成功: {image_url}")
                return image_url
        
        logger.warning(f"Replicate API 失敗: {response.status_code}")
        return None
        
    except Exception as e:
        logger.error(f"Replicate 生成失敗: {str(e)}")
        return None


def generate_with_segmind(prompt: str) -> Optional[str]:
    """
    使用 Segmind API 生成圖片 (SDXL)
    """
    try:
        api_url = "https://api.segmind.com/v1/sdxl1.0-txt2img"
        
        payload = {
            "prompt": prompt,
            "negative_prompt": "ugly, blurry, low quality",
            "samples": 1,
            "scheduler": "UniPC",
            "num_inference_steps": 25,
            "guidance_scale": 7.5,
            "seed": -1,
            "img_width": 1024,
            "img_height": 1024,
            "base64": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": "free"  # 免費額度
        }
        
        logger.info("發送請求到 Segmind...")
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            # Segmind 直接返回圖片數據，上傳到 Imgur
            imgur_url = upload_image_to_imgur_from_bytes(response.content)
            if imgur_url:
                logger.info(f"Segmind 生成成功，已上傳到 Imgur: {imgur_url}")
                return imgur_url
        
        logger.warning(f"Segmind API 失敗: {response.status_code}")
        return None
        
    except Exception as e:
        logger.error(f"Segmind 生成失敗: {str(e)}")
        return None


def generate_with_huggingface(prompt: str) -> Optional[str]:
    """
    使用 Hugging Face Inference API 生成圖片
    使用 stable-diffusion-xl-base-1.0 模型
    """
    try:
        api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 30,
                "guidance_scale": 7.5
            }
        }
        
        logger.info("發送請求到 Hugging Face...")
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            # Hugging Face 返回圖片二進制數據
            imgur_url = upload_image_to_imgur_from_bytes(response.content)
            if imgur_url:
                logger.info(f"Hugging Face 生成成功,已上傳到 Imgur: {imgur_url}")
                return imgur_url
        
        logger.warning(f"Hugging Face API 失敗: {response.status_code}, {response.text[:200]}")
        return None
        
    except Exception as e:
        logger.error(f"Hugging Face 生成失敗: {str(e)}")
        return None


def generate_with_craiyon(prompt: str) -> Optional[str]:
    """
    使用 Craiyon (DALL-E mini) 生成圖片
    """
    try:
        api_url = "https://api.craiyon.com/v3"
        
        payload = {
            "prompt": prompt,
            "version": "35s5hfwn9n78gb06",  # v3 模型
            "negative_prompt": "ugly, blurry, low quality"
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        logger.info("發送請求到 Craiyon...")
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=90
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Craiyon 返回 base64 編碼的圖片列表
            if 'images' in result and len(result['images']) > 0:
                import base64
                image_data = base64.b64decode(result['images'][0])
                
                imgur_url = upload_image_to_imgur_from_bytes(image_data)
                if imgur_url:
                    logger.info(f"Craiyon 生成成功,已上傳到 Imgur: {imgur_url}")
                    return imgur_url
        
        logger.warning(f"Craiyon API 失敗: {response.status_code}")
        return None
        
    except Exception as e:
        logger.error(f"Craiyon 生成失敗: {str(e)}")
        return None


def generate_with_pollinations(prompt: str) -> Optional[str]:
    """
    使用 Pollinations AI 生成圖片 (免費無需認證)
    Pollinations 提供多種模型,包括 FLUX 等高品質模型
    """
    try:
        import urllib.parse
        
        # 使用 turbo 模式加快生成速度,使用 flux 模型提升品質
        if len(prompt) > 500:
            prompt = prompt[:500]
        
        encoded_prompt = urllib.parse.quote(prompt)
        # 使用 flux 模型並指定高品質參數
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux&width=1024&height=1024&enhance=true&nologo=true"
        
        logger.info(f"使用 Pollinations AI (FLUX 模型): {image_url[:100]}...")
        
        # 下載圖片並上傳到 Imgur 獲得永久連結
        response = requests.get(image_url, timeout=90)
        
        if response.status_code == 200:
            imgur_url = upload_image_to_imgur_from_bytes(response.content)
            if imgur_url:
                logger.info(f"圖片已生成並上傳到 Imgur: {imgur_url}")
                return imgur_url
        
        logger.warning(f"Pollinations API 失敗: {response.status_code}")
        return None
        
    except Exception as e:
        logger.error(f"Pollinations 生成失敗: {str(e)}")
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
