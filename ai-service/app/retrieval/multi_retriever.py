"""多路召回模块。

并行执行：
    1. ES 向量检索（主路）：语义相似度 KNN 查询。
    2. Chroma 向量检索（副路）：HNSW 索引，补充召回。
    3. ES BM25 全文检索（关键词路）：精确关键词匹配。

三路结果合并后送入 rerank 重排，兼顾语义召回与关键词命中。
"""
from concurrent.futures import ThreadPoolExecutor
from typing import List

from app.vectorstore.es_vector_store import ESVectorStoreSingleton
from app.vectorstore.chroma_vector_store import ChromaVectorStoreSingleton
from app.vectorstore.embedding_model import get_embedding_model


class MultiRetriever:
    """多路召回器：ES向量 + Chroma向量 + ES BM25 全文。"""

    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        self._embed_model = get_embedding_model()

    def retrieve(self, course_id: str, query: str) -> List[dict]:
        """执行多路并行召回并合并结果。

        Args:
            course_id: 课程 ID。
            query: 检索 query。

        Returns:
            List[dict]: 合并去重后的召回结果列表。
        """
        with ThreadPoolExecutor(max_workers=3) as executor:
            fut_es = executor.submit(self._retrieve_es_vector, course_id, query)
            fut_chroma = executor.submit(self._retrieve_chroma, course_id, query)
            fut_bm25 = executor.submit(self._retrieve_es_bm25, course_id, query)

            es_results = fut_es.result()
            chroma_results = fut_chroma.result()
            bm25_results = fut_bm25.result()

        # 合并去重（按 text 前100字符去重）
        merged = {}
        for item in es_results + chroma_results + bm25_results:
            key = item.get("text", "")[:100]
            if key and key not in merged:
                merged[key] = item

        return list(merged.values())

    def _retrieve_es_vector(self, course_id: str, query: str) -> List[dict]:
        """ES 向量检索。"""
        try:
            from llama_index.core import VectorStoreIndex
            store = ESVectorStoreSingleton.get_store(course_id)
            index = VectorStoreIndex.from_vector_store(store, embed_model=self._embed_model)
            retriever = index.as_retriever(similarity_top_k=self.top_k)
            nodes = retriever.retrieve(query)
            return [
                {"text": n.get_content(), "score": float(n.score or 0), "source": "es_vector", "metadata": n.metadata}
                for n in nodes
            ]
        except Exception as e:
            print(f"[多路召回-ES向量] 失败: {e}")
            return []

    def _retrieve_chroma(self, course_id: str, query: str) -> List[dict]:
        """Chroma 向量检索。"""
        try:
            from llama_index.core import VectorStoreIndex
            store = ChromaVectorStoreSingleton.get_store(course_id)
            index = VectorStoreIndex.from_vector_store(store, embed_model=self._embed_model)
            retriever = index.as_retriever(similarity_top_k=self.top_k)
            nodes = retriever.retrieve(query)
            return [
                {"text": n.get_content(), "score": float(n.score or 0), "source": "chroma", "metadata": n.metadata}
                for n in nodes
            ]
        except Exception as e:
            print(f"[多路召回-Chroma] 失败: {e}")
            return []

    def _retrieve_es_bm25(self, course_id: str, query: str) -> List[dict]:
        """ES BM25 全文检索（关键词路）。

        通过 elasticsearch 客户端直接执行 match 查询，补充精确关键词命中。
        """
        try:
            from elasticsearch import Elasticsearch
            from app.config import ES_URL
            es = Elasticsearch(ES_URL)
            index_name = f"course_{course_id}_index"
            if not es.indices.exists(index=index_name):
                return []
            resp = es.search(
                index=index_name,
                body={
                    "query": {"match": {"text": query}},
                    "size": self.top_k,
                },
            )
            results = []
            for hit in resp["hits"]["hits"]:
                results.append({
                    "text": hit["_source"].get("text", ""),
                    "score": float(hit.get("_score", 0)),
                    "source": "es_bm25",
                    "metadata": hit["_source"].get("metadata", {}),
                })
            return results
        except Exception as e:
            print(f"[多路召回-BM25] 失败: {e}")
            return []
