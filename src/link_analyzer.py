#!/usr/bin/env python3
"""
連結分析工具模組
使用 Gemini API 的 URL Context 功能分析網頁連結
支援網頁內容提取、摘要和 Google Search Grounding
"""

import os
import json
import logging
import re
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

# 導入 Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Gemini API 未安裝，連結分析功能將受限")


class LinkAnalyzer:
    """連結分析器"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化連結分析器
        
        Args:
            api_key: Gemini API 金鑰
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        self.enabled = False
        
        if self.api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                
                # 使用支援 URL Context 的模型
                self.model = genai.GenerativeModel(
                    'gemini-2.0-flash-exp',
                    tools=[
                        {'google_search': {}},  # 啟用 Google 搜尋
                        {
                            'url_context': {
                                'max_urls': 5,
                                'supported_mime_types': ['text/html', 'application/pdf']
                            }
                        }
                    ]
                )
                self.enabled = True
                logger.info("連結分析器已使用 Gemini API + URL Context 初始化")
            except Exception as e:
                logger.error(f"初始化 Gemini API 失敗: {e}")
                self.enabled = False
        else:
            logger.warning("Gemini API 未設定或不可用，連結分析功能將受限")
    
    def extract_urls(self, text: str) -> List[str]:
        """
        從文字中提取 URL
        
        Args:
            text: 文字內容
            
        Returns:
            List[str]: URL 列表
        """
        # URL 正則表達式
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        return urls
    
    async def analyze_link(self, url: str, user_query: Optional[str] = None) -> Dict:
        """
        分析連結內容
        
        Args:
            url: 要分析的網址
            user_query: 用戶的查詢或問題（可選）
            
        Returns:
            Dict: 分析結果
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "連結分析功能未啟用",
                "url": url
            }
        
        try:
            # 構建提示詞
            if user_query:
                prompt = f"""請分析以下網址的內容，並根據用戶的問題提供回答：

網址：{url}

用戶問題：{user_query}

請提供：
1. 網頁的主要內容摘要
2. 針對用戶問題的具體回答
3. 相關的重點資訊

請用繁體中文回答。"""
            else:
                prompt = f"""請分析以下網址的內容：

網址：{url}

請提供：
1. 網頁標題
2. 主要內容摘要（200字以內）
3. 關鍵要點（3-5點）
4. 內容類型（例如：新聞、教學、部落格文章等）

請用繁體中文回答。"""
            
            # 使用 Gemini API 分析
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=1.0  # 使用建議的溫度設定
                )
            )
            
            result_text = response.text.strip()
            
            logger.info(f"連結分析完成: url={url}")
            
            return {
                "success": True,
                "url": url,
                "analysis": result_text,
                "query": user_query
            }
        
        except Exception as e:
            logger.error(f"分析連結時發生錯誤: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    async def analyze_multiple_links(self, urls: List[str], user_query: Optional[str] = None) -> Dict:
        """
        分析多個連結
        
        Args:
            urls: URL 列表
            user_query: 用戶的查詢或問題（可選）
            
        Returns:
            Dict: 分析結果
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "連結分析功能未啟用",
                "urls": urls
            }
        
        # 限制處理的連結數量
        urls = urls[:5]  # 最多處理 5 個連結
        
        try:
            # 構建提示詞
            urls_text = "\n".join([f"{i+1}. {url}" for i, url in enumerate(urls)])
            
            if user_query:
                prompt = f"""請分析以下網址的內容，並根據用戶的問題提供綜合回答：

網址列表：
{urls_text}

用戶問題：{user_query}

請提供：
1. 各網頁的簡要摘要
2. 針對用戶問題的綜合回答
3. 來自不同來源的相關資訊比較

請用繁體中文回答。"""
            else:
                prompt = f"""請分析以下網址的內容並提供綜合摘要：

網址列表：
{urls_text}

請提供：
1. 各網頁的主要內容摘要
2. 共同主題或關聯性
3. 值得注意的重點資訊

請用繁體中文回答。"""
            
            # 使用 Gemini API 分析
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=1.0
                )
            )
            
            result_text = response.text.strip()
            
            logger.info(f"多連結分析完成: count={len(urls)}")
            
            return {
                "success": True,
                "urls": urls,
                "analysis": result_text,
                "query": user_query
            }
        
        except Exception as e:
            logger.error(f"分析多個連結時發生錯誤: {e}")
            return {
                "success": False,
                "error": str(e),
                "urls": urls
            }
    
    def format_analysis_for_display(self, analysis_result: Dict) -> str:
        """
        格式化分析結果為顯示文字
        
        Args:
            analysis_result: 分析結果
            
        Returns:
            str: 格式化的文字
        """
        if not analysis_result.get("success"):
            error = analysis_result.get("error", "未知錯誤")
            return f"❌ 連結分析失敗：{error}"
        
        lines = ["🔗 連結分析結果：\n"]
        
        # 顯示分析的網址
        if "urls" in analysis_result:
            lines.append("📌 分析的網址：")
            for url in analysis_result["urls"]:
                lines.append(f"  • {url}")
            lines.append("")
        elif "url" in analysis_result:
            lines.append(f"📌 網址：{analysis_result['url']}\n")
        
        # 顯示分析內容
        analysis = analysis_result.get("analysis", "")
        if analysis:
            lines.append(analysis)
        
        return "\n".join(lines)


# 建立全域實例
link_analyzer = LinkAnalyzer()


# 連結儲存管理
class LinkStorage:
    """連結儲存管理器"""
    
    def __init__(self, storage_dir: str = ".cache/links"):
        """
        初始化連結儲存管理器
        
        Args:
            storage_dir: 連結儲存目錄
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        logger.info(f"連結儲存管理器已初始化，儲存目錄: {storage_dir}")
    
    def _get_user_file(self, user_id: str) -> str:
        """獲取用戶連結檔案路徑"""
        return os.path.join(self.storage_dir, f"{user_id}_links.json")
    
    def _load_links(self, user_id: str) -> List[Dict]:
        """載入用戶的連結"""
        file_path = self._get_user_file(user_id)
        
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入連結失敗: {e}")
            return []
    
    def _save_links(self, user_id: str, links: List[Dict]) -> bool:
        """儲存用戶的連結"""
        file_path = self._get_user_file(user_id)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(links, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"儲存連結失敗: {e}")
            return False
    
    def save_link(self, user_id: str, url: str, title: Optional[str] = None,
                 summary: Optional[str] = None, tags: Optional[List[str]] = None) -> Dict:
        """
        儲存連結
        
        Args:
            user_id: 用戶 ID
            url: 網址
            title: 標題（可選）
            summary: 摘要（可選）
            tags: 標籤（可選）
            
        Returns:
            Dict: 儲存結果
        """
        from datetime import datetime
        
        links = self._load_links(user_id)
        
        new_link = {
            "id": f"link_{len(links) + 1}_{datetime.now().timestamp()}",
            "url": url,
            "title": title or url,
            "summary": summary,
            "tags": tags or [],
            "saved_at": datetime.now().isoformat()
        }
        
        links.append(new_link)
        
        if self._save_links(user_id, links):
            logger.info(f"連結儲存成功: user_id={user_id}, url={url}")
            return {"success": True, "link": new_link}
        else:
            return {"success": False, "error": "儲存失敗"}
    
    def query_links(self, user_id: str, keyword: Optional[str] = None, limit: int = 10) -> Dict:
        """
        查詢連結
        
        Args:
            user_id: 用戶 ID
            keyword: 搜尋關鍵字（可選）
            limit: 返回結果數量限制
            
        Returns:
            Dict: 查詢結果
        """
        links = self._load_links(user_id)
        
        # 過濾條件
        if keyword:
            keyword_lower = keyword.lower()
            links = [
                link for link in links
                if keyword_lower in link.get("title", "").lower() or
                   keyword_lower in link.get("summary", "").lower() or
                   keyword_lower in link.get("url", "").lower() or
                   keyword_lower in " ".join(link.get("tags", [])).lower()
            ]
        
        # 按時間排序（最新的在前）
        links.sort(key=lambda x: x.get("saved_at", ""), reverse=True)
        
        # 限制數量
        links = links[:limit]
        
        logger.info(f"連結查詢完成: user_id={user_id}, found={len(links)}")
        return {"success": True, "links": links, "count": len(links)}


# 建立連結儲存管理器實例
link_storage = LinkStorage()


# 測試函數
if __name__ == "__main__":
    import asyncio
    
    # 測試連結提取
    test_text = "請看這篇文章 https://example.com/article 和 https://test.com/page"
    urls = link_analyzer.extract_urls(test_text)
    print(f"提取的 URL: {urls}")
    
    # 測試連結儲存
    test_user_id = "test_user_123"
    result = link_storage.save_link(
        test_user_id,
        "https://example.com/article",
        title="範例文章",
        summary="這是一篇範例文章的摘要",
        tags=["範例", "測試"]
    )
    print(f"儲存連結: {result}")
    
    # 查詢連結
    result = link_storage.query_links(test_user_id)
    print(f"查詢連結: {result}")
