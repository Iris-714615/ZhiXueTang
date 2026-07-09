"""Pydantic 请求 / 响应数据模型定义。

集中声明 AI 伴学微服务对外暴露接口的入参结构，由 FastAPI 自动完成
参数校验与 OpenAPI 文档生成。
"""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """AI 伴学聊天请求体。

    Attributes:
        prompt: 学员输入的提问文本（注意：字段类型为 str）。
        course_id: 当前学习课程的唯一标识，用于 RAG 上下文检索。
    """
    prompt: str = Field(..., description="学员提问内容")
    course_id: str = Field(..., description="当前学习课程 ID")


class SearchRequest(BaseModel):
    """知识库语义检索请求体。

    Attributes:
        query: 语义检索 query 文本。
        course_id: 目标课程 ID，限定检索的索引范围。
        top_k: 返回的最相似文档片段数量，默认 5。
    """
    query: str = Field(..., description="语义检索 query")
    course_id: str = Field(..., description="目标课程 ID")
    top_k: int = Field(default=5, ge=1, le=50, description="返回的最相似片段数量")


class BuildIndexRequest(BaseModel):
    """课程向量索引构建请求体。

    Attributes:
        course_id: 待构建索引的课程 ID。
        document_dir: 课程文档（PDF / 字幕 / 讲义）所在本地目录路径。
    """
    course_id: str = Field(..., description="课程 ID")
    document_dir: str = Field(..., description="课程文档目录路径")


class SearchResponse(BaseModel):
    """语义检索响应体。"""
    course_id: str = Field(..., description="课程 ID")
    query: str = Field(..., description="检索 query")
    results: list = Field(default_factory=list, description="检索结果列表")


class BuildIndexResponse(BaseModel):
    """索引构建响应体。"""
    course_id: str = Field(..., description="课程 ID")
    status: str = Field(..., description="构建状态")
    chunks_created: int = Field(default=0, description="生成的文档分片数量")
