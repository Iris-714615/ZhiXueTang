"""数据处理抽象基类。

定义统一的数据处理接口，所有具体处理器（PDF/Word/网页）均需实现该接口。
符合"依赖倒置原则"，工厂模式基于该抽象创建具体处理器实例。
"""
from abc import ABC, abstractmethod
from typing import List
from llama_index.core import Document


class BaseDataProcessor(ABC):
    """数据处理器抽象基类。

    所有数据源处理器必须实现 `load_and_split` 方法，
    负责从对应数据源读取内容、清洗文本、按语义切片并返回 LlamaIndex Document 列表。
    """

    @abstractmethod
    def load_and_split(self, source: str, chunk_size: int = 512, chunk_overlap: int = 100) -> List[Document]:
        """加载并分片数据源。

        Args:
            source: 数据源路径或 URL。
            chunk_size: 分片大小（字符数）。
            chunk_overlap: 分片重叠量，保证上下文连贯。

        Returns:
            List[Document]: LlamaIndex Document 对象列表。
        """
        raise NotImplementedError

    def clean_text(self, text: str) -> str:
        """文本清洗：去除多余空白、特殊字符等。"""
        if not text:
            return ""
        import re
        # 去除多余空白字符
        text = re.sub(r'\s+', ' ', text)
        # 去除非法控制字符
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        return text.strip()
