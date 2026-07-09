"""AI 伴学聊天路由模块（集成 Agent 意图识别 + RAG 双索引智能路由）。

提供 SSE 流式聊天接口，前端通过 fetch + ReadableStream 建立长连接，
接收大模型逐 token 输出的 data: ...\n\n 数据，实现"逐字弹出"交互效果。

流程：
    用户问题 → Agent 意图识别 → 条件路由
        ├─ 常规课程问题 → RAG 节点（双索引智能路由 + 混合检索 + rerank）
        ├─ 闲聊/问候 → 通用对话节点
        └─ 代码/编程问题 → 代码助手节点
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest
from app.services.llm_service import stream_agent_response

router = APIRouter(prefix="/api/v1/ai/assistant", tags=["AI 伴学聊天"])


@router.options("/chat")
async def chat_options():
    """CORS 预检请求处理。"""
    return StreamingResponse(iter([]), media_type="text/event-stream",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type",
        })


@router.post("/chat")
async def chat_assistant(
    req: ChatRequest,
):
    """AI 伴学助手流式聊天接口（Agent 意图识别 + RAG 双索引）。

    接收学员提问与当前课程 ID，经 JWT 鉴权后，调用 LangGraph Agent：
        1. 意图识别节点判断问题类型（rag_question / chat / code_help）
        2. 条件路由到对应处理节点
        3. RAG 节点执行双索引智能路由 + 混合检索增强

    响应：text/event-stream，SSE 格式逐字输出。

    Args:
        req: ChatRequest 请求体（prompt + course_id）。
        user: JWT 鉴权后解析出的 payload。
    """
    user_id = "anonymous"  # 中间件已校验 token，此处不再重复解析
    return StreamingResponse(
        stream_agent_response(req.prompt, req.course_id, user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
