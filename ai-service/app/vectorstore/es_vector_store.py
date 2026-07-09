"""Elasticsearch 向量存储单例模块。

三类主流向量数据库对比：
    ┌──────────────────┬─────────────────────┬──────────────────────┬──────────────────────┐
    │ 特性             │ Elasticsearch       │ Chroma               │ Milvus               │
    ├──────────────────┼─────────────────────┼──────────────────────┼──────────────────────┤
    │ 全文+向量混合检索 │ 原生支持（BM25+KNN）│ 仅向量                │ 仅向量                │
    │ 部署复杂度       │ 中等                │ 极低（嵌入式）        │ 高（分布式）          │
    │ 海量数据扩展性   │ 优秀                │ 一般                  │ 极佳（十亿级）        │
    │ 事务与过滤       │ 强                  │ 弱                    │ 中                    │
    │ 适合场景         │ 生产级混合检索       │ 原型/小规模            │ 超大规模向量检索       │
    └──────────────────┴─────────────────────┴──────────────────────┴──────────────────────┘

本项目选型：
    - ES 作为主向量库：复用已有 ES 集群，支持 BM25+向量混合检索，事务与权限完善。
    - Chroma 作为辅助库：用于 rerank 前的多路召回，轻量高效。
"""
import threading
from typing import Optional

from app.config import ES_URL

_es_store_instances = {}
_es_lock = threading.Lock()


class ESVectorStoreSingleton:
    """Elasticsearch 向量存储单例管理器。

    每个 course_id 对应一个独立的 ES 索引（course_<id>_index），
    单例缓存避免重复创建连接，降低 ES 连接数压力。
    """

    @classmethod
    def get_store(cls, course_id: str):
        """获取指定课程的 ES 向量存储实例（单例）。

        Args:
            course_id: 课程唯一标识。

        Returns:
            ElasticsearchStore: LlamaIndex ES 向量存储实例。
        """
        if course_id not in _es_store_instances:
            with _es_lock:
                if course_id not in _es_store_instances:
                    from llama_index.vector_stores.elasticsearch import ElasticsearchStore
                    _es_store_instances[course_id] = ElasticsearchStore(
                        index_name=f"course_{course_id}_index",
                        es_url=ES_URL,
                    )
                    print(f"[ES] 课程 {course_id} 向量存储实例已创建")
        return _es_store_instances[course_id]

    @classmethod
    def clear_cache(cls) -> None:
        """清空单例缓存（用于索引重建场景）。"""
        with _es_lock:
            _es_store_instances.clear()
