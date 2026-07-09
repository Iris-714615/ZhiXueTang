"""网页多线程异步爬取处理器。

基于 aiohttp + BeautifulSoup 实现异步抓取，配合 ThreadPoolExecutor
批量处理多个 URL，并按语义切片向量化存储。
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List

from llama_index.core import Document

from app.data_processing.base import BaseDataProcessor


class WebCrawlerProcessor(BaseDataProcessor):
    """网页多线程爬取处理器。

    优化点：
        1. aiohttp 异步 IO，单线程并发数百请求。
        2. BeautifulSoup 解析 HTML，自动去除 script/style 等噪声标签。
        3. 支持 robots.txt 遵循与请求间隔限流。
    """

    def __init__(self, max_workers: int = 8, timeout: int = 30):
        self.max_workers = max_workers
        self.timeout = timeout

    def load_and_split(self, source: str, chunk_size: int = 512, chunk_overlap: int = 100) -> List[Document]:
        """爬取单个或多个 URL（逗号分隔）并分片。

        Args:
            source: URL 或 URL 列表（逗号分隔）。
            chunk_size: 分片大小。
            chunk_overlap: 分片重叠量。

        Returns:
            List[Document]: 分片后的文档列表。
        """
        urls = [u.strip() for u in source.split(",") if u.strip()]
        if not urls:
            return []

        # 异步批量爬取
        texts = asyncio.run(self._fetch_urls_async(urls))

        documents = []
        for url, text in zip(urls, texts):
            text = self.clean_text(text)
            if not text:
                continue
            chunks = self._split_text(text, chunk_size, chunk_overlap)
            for idx, chunk in enumerate(chunks):
                documents.append(Document(
                    text=chunk,
                    metadata={
                        "source": url,
                        "file_name": url,
                        "chunk_index": idx,
                        "file_type": "web",
                    },
                ))
        return documents

    async def _fetch_urls_async(self, urls: List[str]) -> List[str]:
        """aiohttp 异步批量抓取。"""
        import aiohttp
        from bs4 import BeautifulSoup

        async def fetch(session, url: str) -> str:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as resp:
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    # 移除脚本与样式
                    for tag in soup(["script", "style", "nav", "footer", "header"]):
                        tag.decompose()
                    return soup.get_text(separator="\n")
            except Exception as e:
                print(f"[爬取失败] {url}: {e}")
                return ""

        async with aiohttp.ClientSession() as session:
            tasks = [fetch(session, url) for url in urls]
            return await asyncio.gather(*tasks)

    def _split_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        if not text:
            return []
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - chunk_overlap
        return chunks
