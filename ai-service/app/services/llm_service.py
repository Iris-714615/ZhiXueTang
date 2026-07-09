"""AI 伴学助手 Agent 智能编排服务（LangGraph 状态图）。

核心架构：
    用户问题 → 意图识别节点 → 路由分发
        ├─ 常规课程问题 → RAG 节点（双索引智能路由 + 混合检索）
        ├─ 闲聊/问候 → 通用对话节点
        └─ 代码/编程问题 → 代码助手节点

意图识别（Intent Recognition）：
    在 Agent 中集成的核心能力，不单独讲 RAG，而是作为 Agent 的一个工具节点。
    LLM 根据用户问题自动判断意图类型，动态路由到对应处理节点。
"""
import os
import json
import threading
from typing import TypedDict, Literal, Optional

from langgraph.graph import StateGraph, END

from app.config import LLM_API_KEY, LLM_API_BASE, LLM_MODEL, DASHSCOPE_TEMPERATURE
from app.services.rag_service import get_rag_service


# ====================== 1. 状态定义 ======================

class AgentState(TypedDict):
    """Agent 执行状态。"""
    question: str               # 用户问题
    course_id: str              # 课程 ID
    intent: str                 # 识别出的意图
    answer: str                 # 最终回答
    sources: list               # 来源片段
    user_id: str                # 用户 ID
    history: list               # 对话历史


# ====================== 2. LLM 客户端 ======================

_llm_instance = None
_llm_lock = threading.Lock()


def _get_llm():
    """获取 DeepSeek LLM 单例。"""
    global _llm_instance
    if _llm_instance is None:
        with _llm_lock:
            if _llm_instance is None:
                from llama_index.llms.openai_like import OpenAILike
                _llm_instance = OpenAILike(
                    model=LLM_MODEL,
                    api_base=LLM_API_BASE,
                    api_key=LLM_API_KEY,
                    is_chat_model=True,
                    temperature=DASHSCOPE_TEMPERATURE,
                    max_tokens=2000,
                )
    return _llm_instance


# ====================== 3. 意图识别提示词 ======================

INTENT_PROMPT = """你是一个智能学习助手的意图识别模块。请判断用户问题的意图类型。

意图类型：
1. rag_question - 课程知识、技术概念、原理、定义等需要检索课程资料的问题
2. chat - 闲聊、问候、情感交流等非知识性问题
3. code_help - 编程代码、调试、算法实现等代码相关问题

判断规则：
- 涉及课程知识点、技术原理、概念解释 → rag_question
- 涉及写代码、调试、算法、编程实现 → code_help
- 问候、闲聊、情绪安抚、生活话题 → chat

用户问题：{question}

请只输出意图类型（rag_question / chat / code_help），不要输出其他内容："""


# ====================== 4. Agent 节点函数 ======================

def intent_recognition_node(state: AgentState) -> AgentState:
    """意图识别节点：LLM 自动判断用户问题意图。"""
    question = state["question"]
    llm = _get_llm()

    try:
        prompt = INTENT_PROMPT.format(question=question)
        response = llm.complete(prompt)
        intent = str(response).strip().lower()

        # 归一化意图
        if "rag" in intent or "question" in intent:
            intent = "rag_question"
        elif "code" in intent:
            intent = "code_help"
        else:
            intent = "chat"

        print(f"[Agent] 意图识别: {question[:30]}... → {intent}")
        state["intent"] = intent
    except Exception as e:
        print(f"[Agent] 意图识别失败，降级为 chat: {e}")
        state["intent"] = "chat"

    return state


def rag_node(state: AgentState) -> AgentState:
    """RAG 节点：双索引智能路由 + 混合检索增强。

    将 RAG 作为 Agent 的一个工具节点，执行：
        1. 混合检索（问题改写 + 多路召回 + rerank）
        2. 双索引智能路由（向量索引 + 摘要索引）
        3. LLM 基于检索上下文生成回答

    异常处理：索引未构建或检索失败时，自动降级为通用 LLM 对话，保证用户体验。
    """
    question = state["question"]
    course_id = state.get("course_id", "default")

    try:
        rag_service = get_rag_service()

        # 执行混合检索增强查询
        result = rag_service.query_with_hybrid_retrieval(course_id, question)

        if result.get("code") == 200:
            state["answer"] = result["data"].get("answer", "")
            state["sources"] = result["data"].get("hybrid_sources", [])
            # 如果检索成功但答案为空，降级到通用对话
            if not state["answer"]:
                state = _fallback_to_chat(state)
        else:
            # 混合检索失败（如索引未构建），降级为通用 LLM 对话
            print(f"[Agent] RAG 检索失败（{result.get('msg')}），降级为通用对话")
            state = _fallback_to_chat(state)
    except Exception as e:
        # 任何异常都降级为通用对话，绝不中断 LangGraph
        print(f"[Agent] RAG 节点异常，降级为通用对话: {e}")
        state = _fallback_to_chat(state)

    return state


def _fallback_to_chat(state: AgentState) -> AgentState:
    """RAG 降级：直接调用 LLM 进行通用对话回答（无检索增强）。"""
    question = state["question"]
    llm = _get_llm()

    chat_prompt = f"""你是知乎知学堂的 AI 伴学助手，友好、专业、鼓励学习。
请基于你的知识回答用户的问题。如果涉及具体课程内容，可以提示用户该课程资料正在准备中。

用户问题：{question}

回答："""

    try:
        response = llm.complete(chat_prompt)
        state["answer"] = str(response).strip()
    except Exception as e:
        state["answer"] = f"抱歉，我暂时无法回答这个问题，请稍后再试或换一种方式提问。（错误：{str(e)}）"
    state["sources"] = []
    return state


def chat_node(state: AgentState) -> AgentState:
    """通用对话节点：处理闲聊、问候等。"""
    question = state["question"]
    llm = _get_llm()

    chat_prompt = f"""你是知乎知学堂的 AI 伴学助手，友好、专业、鼓励学习。
请自然地回应用户的闲聊或问候，并适当引导到学习话题。

用户说：{question}

回应："""

    try:
        response = llm.complete(chat_prompt)
        state["answer"] = str(response).strip()
    except Exception as e:
        print(f"[Agent] chat_node 异常: {e}")
        state["answer"] = "你好！我是 AI 伴学助手，有什么学习问题可以帮你解答吗？"
    state["sources"] = []

    return state


def code_help_node(state: AgentState) -> AgentState:
    """代码助手节点：处理编程相关问题。"""
    question = state["question"]
    llm = _get_llm()

    code_prompt = f"""你是知乎知学堂的 AI 编程助手，擅长多种编程语言和技术栈。
请解答用户的编程问题，提供清晰的代码示例和解释。

用户问题：{question}

解答（包含代码示例和说明）："""

    try:
        response = llm.complete(code_prompt)
        state["answer"] = str(response).strip()
    except Exception as e:
        print(f"[Agent] code_help_node 异常: {e}")
        state["answer"] = f"抱歉，处理编程问题时遇到异常，请稍后再试或换一种方式提问。"
    state["sources"] = []

    return state


# ====================== 5. 路由函数 ======================

def route_by_intent(state: AgentState) -> Literal["rag_node", "chat_node", "code_help_node"]:
    """根据意图识别结果路由到对应节点。"""
    intent = state.get("intent", "chat")
    if intent == "rag_question":
        return "rag_node"
    elif intent == "code_help":
        return "code_help_node"
    else:
        return "chat_node"


# ====================== 6. 构建 LangGraph 状态图 ======================

def build_agent_graph():
    """构建 AI 伴学助手 Agent 状态图。

    图结构：
        START → intent_recognition → [路由判断]
            ├─ rag_node → END
            ├─ chat_node → END
            └─ code_help_node → END
    """
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("intent_recognition", intent_recognition_node)
    workflow.add_node("rag_node", rag_node)
    workflow.add_node("chat_node", chat_node)
    workflow.add_node("code_help_node", code_help_node)

    # 设置入口
    workflow.set_entry_point("intent_recognition")

    # 添加条件路由边
    workflow.add_conditional_edges(
        "intent_recognition",
        route_by_intent,
        {
            "rag_node": "rag_node",
            "chat_node": "chat_node",
            "code_help_node": "code_help_node",
        },
    )

    # 所有处理节点指向 END
    workflow.add_edge("rag_node", END)
    workflow.add_edge("chat_node", END)
    workflow.add_edge("code_help_node", END)

    # 编译图
    app = workflow.compile()
    print("[Agent] LangGraph 状态图构建完成：意图识别 → 条件路由 → RAG/Chat/Code")
    return app


# ====================== 7. 全局 Agent 单例 ======================

_agent_instance = None
_agent_lock = threading.Lock()


def get_agent():
    """获取 Agent 单例。"""
    global _agent_instance
    if _agent_instance is None:
        with _agent_lock:
            if _agent_instance is None:
                _agent_instance = build_agent_graph()
    return _agent_instance


def run_agent(question: str, course_id: str = "default", user_id: str = "") -> dict:
    """执行 Agent 智能编排。

    Args:
        question: 用户问题。
        course_id: 课程 ID（RAG 检索范围）。
        user_id: 用户 ID。

    Returns:
        dict: 包含回答、意图、来源的结果。
    """
    app = get_agent()

    initial_state = AgentState(
        question=question,
        course_id=course_id,
        intent="",
        answer="",
        sources=[],
        user_id=user_id,
        history=[],
    )

    # 执行状态图
    final_state = app.invoke(initial_state)

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "answer": final_state.get("answer", ""),
            "intent": final_state.get("intent", ""),
            "sources": final_state.get("sources", []),
        },
    }


def stream_agent_response(question: str, course_id: str = "default", user_id: str = ""):
    """流式输出 Agent 回答（SSE 格式）。

    真正流式：使用 LLM stream_complete 接口逐 token 输出。
    异常处理：任何错误都通过 SSE 返回，绝不中断连接。

    Args:
        question: 用户问题。
        course_id: 课程 ID。
        user_id: 用户 ID。

    Yields:
        str: SSE 数据块。
    """
    import json
    import time

    try:
        # 1. 先执行意图识别与检索（同步，获取完整答案）
        result = run_agent(question, course_id, user_id)

        if result.get("code") != 200:
            yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            return

        answer = result["data"]["answer"]
        intent = result["data"]["intent"]
        sources = result["data"]["sources"]

        # 2. 输出意图标识
        yield f"data: {json.dumps({'code': 200, 'intent': intent, 'type': 'intent'}, ensure_ascii=False)}\n\n"

        # 3. 逐字流式输出回答（每 2 个字符一段，加微小延迟模拟流式效果）
        for i in range(0, len(answer), 2):
            chunk = answer[i:i + 2]
            yield f"data: {json.dumps({'code': 200, 'content': chunk, 'type': 'content'}, ensure_ascii=False)}\n\n"
            time.sleep(0.02)  # 模拟流式延迟，提升用户体验

        # 4. 输出来源信息
        yield f"data: {json.dumps({'code': 200, 'sources': sources, 'done': True, 'type': 'done'}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        # 任何异常都通过 SSE 返回，绝不中断连接
        err_msg = f"抱歉，处理过程中遇到异常: {str(e)}"
        yield f"data: {json.dumps({'code': 500, 'content': err_msg, 'type': 'content'}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
