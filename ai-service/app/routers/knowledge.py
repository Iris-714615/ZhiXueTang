"""知识库管理路由模块（双索引智能路由构建）。

提供课程双索引（向量索引 + 摘要索引）构建与智能检索接口。
基于 LlamaIndex RouterQueryEngine 实现 LLM 自动路由：
    - 细节查询 → 向量索引
    - 全局概括 → 摘要索引
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import verify_token
from app.models.schemas import BuildIndexRequest, SearchRequest
from app.services.rag_service import get_rag_service

router = APIRouter(prefix="/api/v1/ai/knowledge", tags=["知识库管理"])


@router.post("/build_index")
async def build_index(
    req: BuildIndexRequest,
    user: dict = Depends(verify_token),
):
    """构建课程双索引（向量索引 + 摘要索引 + LLM 智能路由）。

    读取指定课程目录下的文档（PDF / Word / 字幕 / 讲义），
    经分片向量化后并行构建 VectorStoreIndex 与 SummaryIndex，
    并挂载 RouterQueryEngine 实现 LLM 自动路由。

    Args:
        req: BuildIndexRequest 请求体（course_id + document_dir）。
        user: JWT 鉴权后的 payload。
    """
    try:
        rag_service = get_rag_service()
        result = rag_service.build_indexes(req.course_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"双索引构建失败: {e}",
        )


@router.post("/search")
async def search(
    req: SearchRequest,
    user: dict = Depends(verify_token),
):
    """双索引智能路由检索接口。

    RouterQueryEngine 自动判断问题类型：
        - 细节查询 → 向量索引（语义相似度 KNN）
        - 全局概括 → 摘要索引（全文层级汇总）

    Args:
        req: SearchRequest 请求体（query + course_id + top_k）。
        user: JWT 鉴权后的 payload。
    """
    try:
        rag_service = get_rag_service()
        result = rag_service.query(req.course_id, req.query)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"智能路由检索失败: {e}",
        )


@router.post("/hybrid_search")
async def hybrid_search(
    req: SearchRequest,
    user: dict = Depends(verify_token),
):
    """混合检索增强接口（问题改写 + 多路召回 + rerank + 双索引路由）。

    完整工业级 RAG 流水线：
        1. 问题改写生成4个子问题
        2. 多路并行召回（ES向量 + Chroma + BM25）
        3. 分数归一化加权融合
        4. BGE-reranker 重排取 top_n
        5. 双索引智能路由生成最终回答

    Args:
        req: SearchRequest 请求体。
        user: JWT 鉴权后的 payload。
    """
    try:
        rag_service = get_rag_service()
        result = rag_service.query_with_hybrid_retrieval(req.course_id, req.query)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"混合检索失败: {e}",
        )
