"""工厂模式：数据处理器工厂。

根据数据源类型（文件扩展名 / URL 协议）自动选择对应处理器。
新增数据源只需扩展工厂方法，符合"开闭原则"。
"""
import os
from typing import Optional

from app.data_processing.base import BaseDataProcessor
from app.data_processing.pdf_processor import PDFProcessor
from app.data_processing.word_processor import WordProcessor
from app.data_processing.web_crawler import WebCrawlerProcessor


class DataProcessorFactory:
    """数据处理器工厂类。

    根据输入的数据源特征（文件后缀 / URL 协议头）自动实例化对应处理器。
    """

    # 处理器注册表：支持扩展
    _registry = {
        "pdf": PDFProcessor,
        "docx": WordProcessor,
        "doc": WordProcessor,
        "web": WebCrawlerProcessor,
    }

    @classmethod
    def create(cls, source: str) -> BaseDataProcessor:
        """根据数据源创建对应处理器实例。

        Args:
            source: 文件路径或 URL。

        Returns:
            BaseDataProcessor: 对应的处理器实例。

        Raises:
            ValueError: 不支持的数据源类型。
        """
        source_lower = source.lower()
        if source_lower.startswith(("http://", "https://")):
            return cls._registry["web"]()

        ext = os.path.splitext(source_lower)[1].lstrip(".")
        processor_cls = cls._registry.get(ext)
        if processor_cls is None:
            raise ValueError(f"不支持的数据源类型: {ext}，支持的类型: {list(cls._registry.keys())}")
        return processor_cls()

    @classmethod
    def register(cls, ext: str, processor_cls: type) -> None:
        """注册新的处理器类型（扩展点）。

        Args:
            ext: 数据源扩展名。
            processor_cls: 处理器类（须实现 BaseDataProcessor）。
        """
        cls._registry[ext] = processor_cls

    @classmethod
    def process_source(cls, source: str, chunk_size: int = 512, chunk_overlap: int = 100) -> list:
        """便捷方法：直接创建处理器并执行处理。

        Args:
            source: 数据源路径或 URL。
            chunk_size: 分片大小。
            chunk_overlap: 分片重叠量。

        Returns:
            list: LlamaIndex Document 列表。
        """
        processor = cls.create(source)
        return processor.load_and_split(source, chunk_size, chunk_overlap)
