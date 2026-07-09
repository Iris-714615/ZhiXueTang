"""Redis 缓存管理模块。

常见问题答案缓存：节约 token，降低响应延迟。
    - 先查询 Redis 缓存，命中则直接返回结果。
    - 未命中则执行完整 RAG 流程，结果写入缓存。
    - 缓存键：rag:{course_id}:{md5(query)}
    - 过期时间：1小时（可配置）。
"""
import hashlib
import json
import os
from typing import List, Optional

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = int(os.getenv("RAG_CACHE_TTL", "3600"))  # 默认1小时

_redis_client = None


def _get_redis():
    """懒加载 Redis 客户端（单例）。"""
    global _redis_client
    if _redis_client is None:
        try:
            import redis
            _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            _redis_client.ping()
        except Exception as e:
            print(f"[CacheManager] Redis 连接失败，缓存降级: {e}")
            _redis_client = False  # 标记不可用
    return _redis_client


class CacheManager:
    """RAG 检索结果 Redis 缓存管理器。"""

    def _make_key(self, course_id: str, query: str) -> str:
        """生成缓存键：rag:{course_id}:{md5(query)}。"""
        query_hash = hashlib.md5(query.encode("utf-8")).hexdigest()
        return f"rag:{course_id}:{query_hash}"

    def get(self, course_id: str, query: str) -> Optional[List[dict]]:
        """查询缓存。

        Args:
            course_id: 课程 ID。
            query: 用户查询。

        Returns:
            Optional[List[dict]]: 命中则返回结果列表，未命中返回 None。
        """
        client = _get_redis()
        if not client:
            return None
        try:
            key = self._make_key(course_id, query)
            data = client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"[CacheManager] 读取缓存失败: {e}")
        return None

    def set(self, course_id: str, query: str, results: List[dict], ttl: int = None) -> None:
        """写入缓存。

        Args:
            course_id: 课程 ID。
            query: 用户查询。
            results: 检索结果列表。
            ttl: 过期时间（秒），默认使用全局 CACHE_TTL。
        """
        client = _get_redis()
        if not client:
            return
        try:
            key = self._make_key(course_id, query)
            data = json.dumps(results, ensure_ascii=False)
            client.setex(key, ttl or CACHE_TTL, data)
        except Exception as e:
            print(f"[CacheManager] 写入缓存失败: {e}")

    def clear(self, course_id: str = None) -> None:
        """清空缓存。

        Args:
            course_id: 指定课程则清空该课程缓存，否则清空所有。
        """
        client = _get_redis()
        if not client:
            return
        try:
            pattern = f"rag:{course_id}:*" if course_id else "rag:*"
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
                print(f"[CacheManager] 已清空 {len(keys)} 条缓存")
        except Exception as e:
            print(f"[CacheManager] 清空缓存失败: {e}")
