"""FastAPI AI 伴学微服务主入口。

职责：
    1. 创建 FastAPI 应用实例。
    2. 配置 CORS 跨域（允许前端开发服务器 localhost:5173）。
    3. 挂载 AI 伴学聊天与知识库管理路由。
    4. 注册 JWT 鉴权中间件。
    5. 启动数据同步模块（binlog 监听、RabbitMQ 消费、定时任务）。

启动方式：
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import CORS_ORIGINS, JWT_SECRET, JWT_ALGORITHM
from app.routers import chat, knowledge
from app.services.llm_service import build_agent_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。

    启动时：
        1. 预编译 LangGraph Agent 状态图。
        2. 启动数据同步模块（binlog / rabbitmq / 定时任务）。
    """
    # 1. 预热 LangGraph Agent 状态图（意图识别 → RAG/Chat/Code 路由）
    graph = build_agent_graph()
    print(f"[启动] LangGraph Agent 状态图: {'已就绪' if graph is not None else '降级模式'}")

    # 2. 数据同步模块（默认禁用，需外部 MySQL binlog / RabbitMQ / APScheduler 支持）
    #    通过环境变量 ENABLE_DATA_SYNC=1 开启
    sync_modules = []
    if os.getenv("ENABLE_DATA_SYNC", "0") == "1":
        try:
            from app.data_sync.binlog_listener import BinlogListener
            binlog = BinlogListener()
            binlog.start()
            sync_modules.append(binlog)
        except Exception as e:
            print(f"[启动] Binlog 监听未启动（非阻塞）: {e}")

        try:
            from app.data_sync.rabbitmq_consumer import RabbitMQConsumer
            consumer = RabbitMQConsumer()
            consumer.start()
            sync_modules.append(consumer)
        except Exception as e:
            print(f"[启动] RabbitMQ 消费者未启动（非阻塞）: {e}")

        try:
            from app.data_sync.scheduled_tasks import ScheduledTaskManager
            scheduler = ScheduledTaskManager()
            scheduler.start()
            sync_modules.append(scheduler)
        except Exception as e:
            print(f"[启动] 定时任务调度器未启动（非阻塞）: {e}")
    else:
        print("[启动] 数据同步模块已禁用（设置 ENABLE_DATA_SYNC=1 开启）")

    yield

    # 关闭数据同步模块
    for module in sync_modules:
        try:
            module.stop()
        except Exception:
            pass
    print("[关闭] AI 伴学微服务退出")


app = FastAPI(
    title="ZhiXueTang-AI-Service",
    description="知乎知学堂 AI 伴学微服务（FastAPI + LangGraph + LlamaIndex 双索引智能路由 RAG）",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# JWT 鉴权中间件
@app.middleware("http")
async def jwt_auth_middleware(request: Request, call_next):
    """JWT 鉴权 HTTP 中间件。

    对 /api/v1/ai 前缀的请求校验 Authorization 头中的 Bearer Token。
    """
    import jwt as pyjwt

    path = request.url.path
    method = request.method
    # CORS 预检请求直接放行
    if method == "OPTIONS":
        return await call_next(request)
    public_paths = ["/", "/health", "/docs", "/openapi.json", "/redoc"]
    if any(path == p or path.startswith(p) for p in public_paths):
        return await call_next(request)

    if path.startswith("/api/v1/ai"):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.lower().startswith("bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "未提供有效的认证信息"},
            )
        token = auth_header.split(" ", 1)[1]
        try:
            pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except pyjwt.PyJWTError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token 校验失败"},
            )

    return await call_next(request)


# 挂载业务路由
app.include_router(chat.router)
app.include_router(knowledge.router)


# 健康检查
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口，用于网关探活。"""
    return {
        "status": "ok",
        "service": "ZhiXueTang-AI-Service",
        "version": "2.0.0",
        "modules": ["LangGraph Agent", "LlamaIndex 双索引", "RAG 混合检索", "Binlog/RabbitMQ 同步"],
    }
