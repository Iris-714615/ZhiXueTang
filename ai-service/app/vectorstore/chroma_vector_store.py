"""Chroma 向量存储单例模块（用于混合检索）。

作为 ES 的补充：Chroma 嵌入式部署、纯内存/HNSW 索引，
在多路召回阶段提供第二路向量检索结果，与 ES 结果归一化后送入 rerank。
"""
import os
import threading

_chroma_instances = {}
_chroma_lock = threading.Lock()

# Chroma 数据持久化目录
CHROMA_PERSIST_DIR = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db")


class ChromaVectorStoreSingleton:
    """Chroma 向量存储单例管理器。"""

    @classmethod
    def get_store(cls, course_id: str):
        """获取指定课程的 Chroma 向量存储实例（单例）。

        Args:
            course_id: 课程唯一标识。

        Returns:
            ChromaVectorStore: LlamaIndex Chroma 向量存储实例。
        """
        if course_id not in _chroma_instances:
            with _chroma_lock:
                if course_id not in _chroma_instances:
                    import chromadb
                    from llama_index.vector_stores.chroma import ChromaVectorStore

                    db = chromadb.PersistentClient(path=os.path.join(CHROMA_PERSIST_DIR, course_id))
                    chroma_collection = db.get_or_create_collection(f"course_{course_id}")
                    _chroma_instances[course_id] = ChromaVectorStore(chroma_collection=chroma_collection)
                    print(f"[Chroma] 课程 {course_id} 向量存储实例已创建")
        return _chroma_instances[course_id]

    @classmethod
    def clear_cache(cls) -> None:
        """清空单例缓存。"""
        with _chroma_lock:
            _chroma_instances.clear()
