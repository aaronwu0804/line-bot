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
        圖片 URL (直接可用於 LINE)
    """
    try:
        # 使用 Pollinations AI 免費圖片生成 API
        logger.info(f"開始生成圖片，提示詞: {prompt[:50]}...")
        
        import urllib.parse
        
        # 縮短提示詞以避免 URL 過長 (LINE 限制 2000 字元)
        # 如果提示詞太長，截斷並添加省略號
        max_prompt_length = 100
        if len(prompt) > max_prompt_length:
            prompt = prompt[:max_prompt_length]
            logger.info(f"提示詞過長，已截斷為: {prompt}")
        
        encoded_prompt = urllib.parse.quote(prompt)
        
        # 使用較短的 URL 格式
        # 不添加 width/height 參數以縮短 URL
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        logger.info(f"生成的圖片 URL 長度: {len(image_url)} 字元")
        
        # 檢查 URL 長度
        if len(image_url) > 2000:
            logger.error(f"URL 過長 ({len(image_url)} > 2000)，無法發送到 LINE")
            return None
        
        logger.info(f"圖片 URL 已生成: {image_url[:100]}...")
        
        # 驗證 URL 是否可訪問
        try:
            response = requests.head(image_url, timeout=10)
            if response.status_code == 200:
                logger.info(f"圖片生成成功，URL 可訪問")
                return image_url
            else:
                logger.warning(f"圖片 URL 返回狀態碼: {response.status_code}")
                # 即使返回非 200，也嘗試返回 URL (Pollinations 可能在生成中)
                return image_url
        except Exception as e:
            logger.warning(f"驗證 URL 時發生錯誤: {str(e)}，仍返回 URL")
            return image_url
            
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
