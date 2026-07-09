"""向量数据库与向量化模型模块包初始化。

包含：
    - embedding_model: BGE 向量化模型（单例）
    - es_vector_store: Elasticsearch 向量存储（单例）
    - chroma_vector_store: Chroma 向量存储（单例，用于混合检索）
"""
from app.vectorstore.embedding_model import get_embedding_model
from app.vectorstore.es_vector_store import ESVectorStoreSingleton
from app.vectorstore.chroma_vector_store import ChromaVectorStoreSingleton

__all__ = [
    "get_embedding_model",
    "ESVectorStoreSingleton",
    "ChromaVectorStoreSingleton",
]
