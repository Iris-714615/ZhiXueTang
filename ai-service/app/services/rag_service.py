"""双索引智能路由 RAG 服务（核心模块）。

基于 LlamaIndex 实现 VectorStoreIndex + SummaryIndex 双索引并行构建，
通过 RouterQueryEngine 实现 LLM 智能路由：
    - 细节查询（定义、原理、参数）→ 向量索引（语义相似度 KNN 检索）
    - 全局概括（总结、框架、要点）→ 摘要索引（全文层级汇总）

双索引互补机制：
    向量索引擅长局部细节精准检索，适合用户针对性知识点提问；
    摘要索引擅长全局逻辑梳理、全文概括，适合总结、架构分析类问题。
    双索引彻底解决单一索引场景局限性。

工业级落地价值：
    该多索引混合架构是企业知识库、文档问答、智能客服 RAG 项目的标准高阶方案，
    相比传统单向量 RAG，问答准确率、场景适配性、逻辑完整性大幅提升。
"""
import os
import threading
from typing import Optional, List

from llama_index.core import (
    Settings, VectorStoreIndex, SummaryIndex, SimpleDirectoryReader,
    get_response_synthesizer, Document,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.tools import QueryEngineTool

from app.config import (
    LLM_API_KEY, LLM_API_BASE, LLM_MODEL, DASHSCOPE_TEMPERATURE,
    EMBEDDING_MODEL_NAME, CHUNK_SIZE, CHUNK_OVERLAP,
)
from app.vectorstore.embedding_model import get_embedding_model
from app.retrieval.hybrid_retriever import HybridRetriever

# 全局配置只初始化一次（线程安全）
_settings_initialized = False
_settings_lock = threading.Lock()

# 课程级路由引擎缓存：{course_id: RouterQueryEngine}
_router_engines = {}
_router_lock = threading.Lock()


def _init_global_settings():
    """初始化 LlamaIndex 全局配置（LLM + Embedding + 分块器）。

    使用双重检查锁保证多线程下只初始化一次。
    """
    global _settings_initialized
    if _settings_initialized:
        return
    with _settings_lock:
        if _settings_initialized:
            return

        # LLM 配置：千问（Qwen）对话模型（DashScope OpenAI 兼容接口）
        Settings.llm = OpenAILike(
            model=LLM_MODEL,
            api_base=LLM_API_BASE,
            api_key=LLM_API_KEY,
            is_chat_model=True,
            temperature=DASHSCOPE_TEMPERATURE,  # 路由决策温度
            max_tokens=2000,
        )

        # Embedding 配置：BGE 向量模型
        Settings.embed_model = get_embedding_model()

        # 文档分块器：优化长文档层级上下文，解决信息缺失
        Settings.node_parser = SentenceSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,  # 块重叠，保证上下文连贯
        )

        _settings_initialized = True
        print("[RAG] LLM/Embedding/分块器全局配置完成")


class RAGService:
    """双索引智能路由 RAG 服务。

    核心能力：
        1. build_indexes: 构建向量索引 + 摘要索引（双索引并行）
        2. get_router_engine: 获取 LLM 智能路由查询引擎（带缓存）
        3. query: 执行智能路由查询，自动选择最优索引
        4. query_with_hybrid_retrieval: 混合检索 + rerank 增强查询
    """

    def __init__(self, data_dir: str = "data"):
        """初始化 RAG 服务。

        Args:
            data_dir: 知识库文档目录路径。
        """
        _init_global_settings()
        self.data_dir = data_dir
        self.hybrid_retriever = HybridRetriever(top_k=5, top_n=4)

    def build_indexes(self, course_id: str, documents: Optional[List[Document]] = None) -> dict:
        """为指定课程构建双索引（向量索引 + 摘要索引）。

        Args:
            course_id: 课程唯一标识。
            documents: 可选，已加载的文档列表。未提供则从 data_dir 加载。

        Returns:
            dict: 构建结果信息。
        """
        # 1. 加载文档
        if documents is None:
            docs_path = os.path.join(self.data_dir, course_id)
            if not os.path.exists(docs_path):
                return {"code": 400, "msg": f"课程文档目录不存在: {docs_path}"}
            documents = SimpleDirectoryReader(docs_path).load_data()

        if not documents:
            return {"code": 400, "msg": "无可用文档"}

        # 2. 文档分块
        nodes = Settings.node_parser.get_nodes_from_documents(documents)
        print(f"[RAG] 课程 {course_id} 加载文档 {len(documents)} 个，分块节点 {len(nodes)} 个")

        # 3.1 构建向量索引（细节语义检索）
        vector_index = VectorStoreIndex(nodes)
        vector_synthesizer = get_response_synthesizer(
            response_mode="compact",  # 紧凑上下文拼接，减少冗余
            use_async=True,
        )
        vector_query_engine = vector_index.as_query_engine(
            response_synthesizer=vector_synthesizer,
            similarity_top_k=4,  # 检索4个最相关细节片段
        )

        # 3.2 构建摘要索引（全局整体概括）
        summary_index = SummaryIndex(nodes)
        summary_synthesizer = get_response_synthesizer(
            response_mode="tree_summarize",  # 树形层级汇总，长文本全局上下文补全
            use_async=True,
        )
        summary_query_engine = summary_index.as_query_engine(
            response_synthesizer=summary_synthesizer,
        )

        # 4. 构建 LLM 智能路由引擎
        router_engine = self._build_router_engine(vector_query_engine, summary_query_engine)

        # 缓存路由引擎
        with _router_lock:
            _router_engines[course_id] = {
                "router": router_engine,
                "vector_engine": vector_query_engine,
                "summary_engine": summary_query_engine,
                "node_count": len(nodes),
            }

        print(f"[RAG] 课程 {course_id} Vector向量索引 + Summary摘要索引 构建完成")
        return {
            "code": 200,
            "msg": "双索引构建成功",
            "data": {
                "course_id": course_id,
                "document_count": len(documents),
                "node_count": len(nodes),
            },
        }

    def _build_router_engine(self, vector_query_engine, summary_query_engine) -> RouterQueryEngine:
        """构建 LLM 智能路由查询引擎。

        将两个查询引擎封装为路由工具，给 LLM 明确选择规则，
        LLMSingleSelector 自动判断问题类型并选择最优索引。
        """
        # 向量检索工具：适合细节查询
        vector_tool = QueryEngineTool.from_defaults(
            query_engine=vector_query_engine,
            description=(
                "【向量检索工具】适合查询具体细节、技术参数、局部知识点、流程步骤、定义解释类问题。"
                "例：向量索引工作原理是什么？混合检索有什么优势？"
            ),
        )

        # 全文摘要工具：适合全局概括
        summary_tool = QueryEngineTool.from_defaults(
            query_engine=summary_query_engine,
            description=(
                "【全文摘要工具】适合查询文档整体总结、全部核心要点、全局框架、整体概述类问题。"
                "例：这份手册讲了哪些核心内容？LlamaIndex有哪些索引类型？全文整体介绍一下。"
            ),
        )

        # 路由引擎：LLM 自动判断问题，选择最优索引检索
        router_query_engine = RouterQueryEngine(
            selector=LLMSingleSelector.from_defaults(),
            query_engine_tools=[summary_tool, vector_tool],
            verbose=True,  # 打印路由决策日志
        )
        return router_query_engine

    def get_router_engine(self, course_id: str) -> Optional[RouterQueryEngine]:
        """获取指定课程的路由查询引擎（带缓存）。

        Args:
            course_id: 课程 ID。

        Returns:
            RouterQueryEngine 或 None（未构建索引时）。
        """
        with _router_lock:
            cache = _router_engines.get(course_id)
        return cache["router"] if cache else None

    def query(self, course_id: str, question: str) -> dict:
        """执行智能路由查询。

        RouterQueryEngine 自动理解用户提问意图，动态选择最优查询引擎：
            细节问题 → 向量检索
            总结问题 → 摘要检索
        无需人工干预路由逻辑。

        Args:
            course_id: 课程 ID。
            question: 用户问题。

        Returns:
            dict: 包含回答、来源片段、路由决策的查询结果。
        """
        router = self.get_router_engine(course_id)
        if router is None:
            return {"code": 400, "msg": f"课程 {course_id} 索引未构建，请先调用 build_indexes"}

        try:
            response = router.query(question)

            # 收集答案溯源参考片段
            source_nodes = []
            for node in response.source_nodes:
                source_nodes.append({
                    "file_name": node.metadata.get("file_name", "未知"),
                    "score": float(node.score or 0),
                    "content": node.text[:300],
                })

            return {
                "code": 200,
                "msg": "success",
                "data": {
                    "answer": str(response),
                    "sources": source_nodes,
                    "router_decision": getattr(response, "metadata", {}).get("selector_result", ""),
                },
            }
        except Exception as e:
            return {"code": 500, "msg": f"查询异常: {str(e)}"}

    def query_with_hybrid_retrieval(self, course_id: str, question: str) -> dict:
        """混合检索增强查询（问题改写 + 多路召回 + rerank + 双索引路由）。

        流程：
            1. HybridRetriever 执行混合检索获取精确上下文片段。
            2. 将检索结果作为上下文注入 LLM 提示词。
            3. RouterQueryEngine 执行双索引智能路由生成最终回答。

        Args:
            course_id: 课程 ID。
            question: 用户问题。

        Returns:
            dict: 增强查询结果。
        """
        # 1. 混合检索获取精确上下文
        retrieved_docs = self.hybrid_retriever.retrieve(course_id, question)

        if not retrieved_docs:
            # 降级为纯双索引路由
            return self.query(course_id, question)

        # 2. 拼接检索上下文
        context = "\n\n".join([doc.get("text", "") for doc in retrieved_docs[:4]])

        # 3. 重写提示词：基于检索上下文生成回答
        enhanced_question = f"""基于以下检索到的课程资料，回答用户问题。

【检索资料】
{context}

【用户问题】
{question}

【回答要求】
1. 严格基于检索资料回答，不要编造未提及的内容。
2. 如果资料不足，明确告知用户并建议补充提问。
3. 回答需结构清晰，分点阐述。"""

        # 4. 执行双索引路由查询
        result = self.query(course_id, enhanced_question)

        # 5. 附加混合检索来源信息
        if result.get("code") == 200:
            result["data"]["hybrid_sources"] = [
                {
                    "text": doc.get("text", "")[:200],
                    "rerank_score": doc.get("rerank_score", 0),
                    "source": doc.get("source", ""),
                }
                for doc in retrieved_docs[:4]
            ]

        return result

    def stream_query(self, course_id: str, question: str):
        """流式查询（SSE 逐字输出）。

        Args:
            course_id: 课程 ID。
            question: 用户问题。

        Yields:
            str: SSE 格式的数据块。
        """
        router = self.get_router_engine(course_id)
        if router is None:
            yield f"data: {__import__('json').dumps({'code': 400, 'msg': '索引未构建'}, ensure_ascii=False)}\n\n"
            return

        try:
            # 使用路由引擎流式查询
            response = router.query(question)
            answer = str(response)

            # 模拟逐字流式输出
            import json
            for i in range(0, len(answer), 2):
                chunk = answer[i:i + 2]
                yield f"data: {json.dumps({'code': 200, 'content': chunk}, ensure_ascii=False)}\n\n"

            # 输出来源信息
            sources = []
            for node in response.source_nodes:
                sources.append({
                    "file_name": node.metadata.get("file_name", "未知"),
                    "score": float(node.score or 0),
                    "content": node.text[:200],
                })
            yield f"data: {json.dumps({'code': 200, 'sources': sources, 'done': True}, ensure_ascii=False)}\n\n"
        except Exception as e:
            import json
            yield f"data: {json.dumps({'code': 500, 'msg': str(e)}, ensure_ascii=False)}\n\n"


# 全局单例
_rag_service_instance = None
_rag_lock = threading.Lock()


def get_rag_service() -> RAGService:
    """获取 RAG 服务单例（线程安全）。"""
    global _rag_service_instance
    if _rag_service_instance is None:
        with _rag_lock:
            if _rag_service_instance is None:
                _rag_service_instance = RAGService()
    return _rag_service_instance
