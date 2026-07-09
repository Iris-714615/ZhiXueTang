"""数据处理模块包初始化。

工厂模式封装 RAG 数据处理流水线：
    数据源（PDF/Word/网页/数据库）→ 多线程分片读取 → 文本清洗
    → 向量化 → 持久化至向量数据库
"""
from app.data_processing.document_factory import DataProcessorFactory
from app.data_processing.pdf_processor import PDFProcessor
from app.data_processing.word_processor import WordProcessor
from app.data_processing.web_crawler import WebCrawlerProcessor

__all__ = [
    "DataProcessorFactory",
    "PDFProcessor",
    "WordProcessor",
    "WebCrawlerProcessor",
]
