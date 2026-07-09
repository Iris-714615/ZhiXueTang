"""向量化模型模块（单例模式）。

模型选型：BAAI/bge-small-zh-v1.5（中文场景）

模型优势：
    1. 中文语义理解强：BGE 系列在 C-MTEB 中文检索基准上长期 Top3。
    2. 轻量高效：bge-small 仅 ~95MB，CPU 即可推理，适合中小型知识库。
    3. 与 OpenAI text-embedding-3 对比：
       - BGE 开源免费、可离线部署，数据不出域。
       - OpenAI 维度 1536/3072，存储成本高；BGE-small-zh 维度 512，性价比更优。
       - 在中文场景，BGE 检索准确率优于 OpenAI ada-002。
    4. 向量维度：512（bge-small-zh），兼顾检索精度与存储成本。

向量索引：
    - ES: 使用 dense_vector 字段 + KNN 查询（cosine 相似度）。
    - Chroma: 内置 HNSW 索引，默认 L2 距离，可切换 cosine。
"""
import os
import threading
from typing import Optional

# 设置 HuggingFace 国内镜像加速
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

_embedding_instance = None
_embedding_lock = threading.Lock()


def get_embedding_model():
    """获取 BGE Embedding 模型单例（线程安全）。

    使用双重检查锁保证多线程下只初始化一次，避免重复加载模型占用内存。

    Returns:
        HuggingFaceEmbedding: BGE 向量化模型实例。
    """
    global _embedding_instance
    if _embedding_instance is None:
        with _embedding_lock:
            if _embedding_instance is None:
                from llama_index.embeddings.huggingface import HuggingFaceEmbedding
                _embedding_instance = HuggingFaceEmbedding(
                    model_name="BAAI/bge-small-zh-v1.5",
                    device="cpu",
                )
                print("[Embedding] BGE-small-zh 模型加载完成（维度 512）")
    return _embedding_instance
