"""检索优化模块包初始化。

包含：
    - query_rewriter: 问题改写（生成多角度子问题，提升召回率）
    - multi_retriever: 多路召回（ES + Chroma 并行检索）
    - reranker: rerank 重排（BGE-reranker 对召回结果二次打分）
    - hybrid_retriever: 混合检索归一化（BM25 + 向量 加权融合）
    - cache_manager: Redis 缓存（常见问题直接返回，节约 token）
"""
from app.retrieval.query_rewriter import QueryRewriter
from app.retrieval.multi_retriever import MultiRetriever
from app.retrieval.reranker import Reranker
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.cache_manager import CacheManager

__all__ = [
    "QueryRewriter",
    "MultiRetriever",
    "Reranker",
    "HybridRetriever",
    "CacheManager",
]
