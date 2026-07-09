"""AI 伴学微服务全局配置模块。

集中管理 JWT 密钥、Elasticsearch 向量库地址、Redis 缓存地址等关键配置项，
便于在不同环境（开发 / 测试 / 生产）间切换。
"""
import os


# JWT 鉴权密钥（与主业务后端 Golang / Django 服务保持一致，实现跨服务统一鉴权）
JWT_SECRET = os.getenv("JWT_SECRET", "ZhiHu-ZhiXueTang-Secret-Key")

# JWT 签名算法
JWT_ALGORITHM = "HS256"

# Elasticsearch 服务地址，用于存储课程文档向量并支撑 RAG 语义检索
ES_URL = os.getenv("ES_URL", "http://localhost:9200")

# Redis 服务地址，用于会话缓存、分布式锁及 Celery 消息队列Broker
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Celery 消息队列 Broker 地址（异步任务：PDF OCR、字幕提取、向量构建等）
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

# 前端开发服务器地址，用于 CORS 跨域白名单配置
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# ====================== LLM / Embedding 模型配置 ======================

# 千问（Qwen）对话模型配置（通过 DashScope OpenAI 兼容接口调用）
# 用于 LLM 智能路由决策 + 答案合成 + Agent 意图识别
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-310108a8f49a425087fc65d0d939564e")
DASHSCOPE_API_BASE = os.getenv("DASHSCOPE_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
DASHSCOPE_MODEL = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
DASHSCOPE_TEMPERATURE = float(os.getenv("DASHSCOPE_TEMPERATURE", "0.7"))

# 向后兼容别名（保持原有代码无需大规模改动）
LLM_API_KEY = DASHSCOPE_API_KEY
LLM_API_BASE = DASHSCOPE_API_BASE
LLM_MODEL = DASHSCOPE_MODEL

# BGE 向量化模型名称（中文场景，512 维度）
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-zh-v1.5")

# BGE Reranker 重排模型名称
RERANKER_MODEL_NAME = os.getenv("RERANKER_MODEL_NAME", "BAAI/bge-reranker-base")

# 文档分块参数
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# RabbitMQ 消息队列配置（数据同步）
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

# MySQL Binlog 监听配置（数据同步）
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
MYSQL_DB = os.getenv("MYSQL_DB", "zhixuetang")

# HuggingFace 国内镜像加速
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
