"""混合检索模块（归一化处理）。

将多路召回的分数进行 min-max 归一化，消除不同检索源分值量纲差异，
再按加权策略融合排序，输出最终候选集交由 rerank。

归一化公式：
    score_norm = (score - min) / (max - min + 1e-6)

加权策略：
    - ES向量：0.4（语义精准）
    - Chroma：0.3（补充召回）
    - BM25：0.3（关键词精确）
"""
from typing import List

from app.retrieval.multi_retriever import MultiRetriever
from app.retrieval.reranker import Reranker
from app.retrieval.query_rewriter import QueryRewriter
from app.retrieval.cache_manager import CacheManager


class HybridRetriever:
    """混合检索器：问题改写 → 多路召回 → 归一化融合 → rerank 重排。"""

    # 各路检索权重
    WEIGHTS = {
        "es_vector": 0.4,
        "chroma": 0.3,
        "es_bm25": 0.3,
    }

    def __init__(self, top_k: int = 5, top_n: int = 4):
        self.rewriter = QueryRewriter()
        self.multi_retriever = MultiRetriever(top_k=top_k)
        self.reranker = Reranker()
        self.cache = CacheManager()
        self.top_n = top_n

    def retrieve(self, course_id: str, query: str) -> List[dict]:
        """完整混合检索流水线。

        流程：
            1. 缓存命中检查（常见问题直接返回）。
            2. 问题改写（子问题生成）。
            3. 多路并行召回（ES向量+Chroma+BM25）。
            4. 分数归一化加权融合。
            5. rerank 重排取 top_n。

        Args:
            course_id: 课程 ID。
            query: 用户查询。

        Returns:
            List[dict]: 最终检索结果列表。
        """
        # 1. 缓存检查
        cached = self.cache.get(course_id, query)
        if cached:
            print(f"[HybridRetriever] 缓存命中: {query[:30]}...")
            return cached

        # 2. 问题改写：生成4个子问题
        sub_queries = self.rewriter.generate_sub_queries(query)
        print(f"[HybridRetriever] 问题改写生成 {len(sub_queries)} 个查询")

        # 3. 多路召回（每个子问题都召回）
        all_results = []
        for sq in sub_queries:
            results = self.multi_retriever.retrieve(course_id, sq)
            all_results.extend(results)

        # 去重
        merged = {}
        for item in all_results:
            key = item.get("text", "")[:100]
            if key and key not in merged:
                merged[key] = item
        all_results = list(merged.values())

        if not all_results:
            return []

        # 4. 分数归一化加权
        normalized = self._normalize_and_weight(all_results)

        # 5. rerank 重排
        final = self.reranker.rerank(query, normalized, top_n=self.top_n)

        # 6. 写入缓存
        self.cache.set(course_id, query, final)

        return final

    def _normalize_and_weight(self, results: List[dict]) -> List[dict]:
        """对各路召回分数进行 min-max 归一化并加权融合。"""
        # 按来源分组
        groups = {}
        for item in results:
            src = item.get("source", "unknown")
            groups.setdefault(src, []).append(item)

        # 每组归一化
        normalized = []
        for src, items in groups.items():
            scores = [it.get("score", 0) for it in items]
            min_s, max_s = min(scores), max(scores)
            denom = max_s - min_s + 1e-6
            weight = self.WEIGHTS.get(src, 0.3)
            for it in items:
                norm_score = (it.get("score", 0) - min_s) / denom
                it["normalized_score"] = norm_score * weight
                normalized.append(it)

        # 按归一化分数排序
        normalized.sort(key=lambda x: x.get("normalized_score", 0), reverse=True)
        return normalized
