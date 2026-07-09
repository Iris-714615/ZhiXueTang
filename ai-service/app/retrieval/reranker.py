"""Rerank 重排模块。

使用 BGE-reranker 对多路召回结果进行二次打分排序：
    - 召回阶段追求覆盖率（top_k=5×3路=15条），可能含噪声。
    - rerank 阶段用更精细的 cross-encoder 模型对 query-doc 对打分，取 top_n。

模型选型：BAAI/bge-reranker-base
    - Cross-Encoder 架构，比双塔向量更准确。
    - 中文场景表现优异，开源免费。
"""
import os
from typing import List

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"


class Reranker:
    """BGE-reranker 重排器。"""

    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        self.model_name = model_name
        self._pipe = None

    def _get_pipe(self):
        """懒加载 reranker 模型。"""
        if self._pipe is None:
            from sentence_transformers import CrossEncoder
            self._pipe = CrossEncoder(self.model_name)
            print(f"[Reranker] bge-reranker-base 模型加载完成")
        return self._pipe

    def rerank(self, query: str, documents: List[dict], top_n: int = 4) -> List[dict]:
        """对召回结果进行 rerank 重排。

        Args:
            query: 用户查询。
            documents: 多路召回的文档列表。
            top_n: 重排后保留的 top N 数量。

        Returns:
            List[dict]: 重排后的 top_n 文档列表（带 rerank_score）。
        """
        if not documents:
            return []

        try:
            pipe = self._get_pipe()
            # 构建 query-doc 对
            pairs = [(query, doc.get("text", "")) for doc in documents]
            scores = pipe.predict(pairs)

            # 注入 rerank_score 并排序
            for doc, score in zip(documents, scores):
                doc["rerank_score"] = float(score)

            # 按 rerank_score 降序取 top_n
            sorted_docs = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
            return sorted_docs[:top_n]
        except Exception as e:
            print(f"[Reranker] 重排失败，降级为原始排序: {e}")
            return documents[:top_n]
