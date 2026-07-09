"""问题改写模块。

两种策略：
    策略1（子问题生成）：用户原问题 + LLM 生成的3个相关子问题，共4个问题分别检索，结果汇总。
    策略2（语义压缩）：通过提示词提取问题关键字，压缩冗余语义，提升检索精准度。

提示词工程：
    - 子问题生成提示词：要求 LLM 从不同角度拆解用户问题。
    - 语义压缩提示词：提取核心实体与意图关键词。
"""
import os
from typing import List

# DeepSeek 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"


class QueryRewriter:
    """问题改写器：子问题生成 + 语义压缩。"""

    # 子问题生成提示词
    SUB_QUERY_PROMPT = """你是一个智能问答系统的查询改写助手。
请根据用户的问题，从不同角度生成3个相关的子问题，用于多路召回提升检索覆盖率。

要求：
1. 子问题应覆盖原问题的不同方面（定义、原理、应用、对比等）。
2. 子问题必须简洁、语义独立，可直接用于检索。
3. 只输出3个子问题，每行一个，不要编号、不要额外解释。

用户问题：{question}

生成的3个子问题："""

    # 语义压缩提示词
    COMPRESS_PROMPT = """请从以下问题中提取核心关键词和语义要点，压缩为简洁的检索query。
要求：去除口语化表达，保留专业术语，输出不超过30字。

原始问题：{question}

压缩后的检索query："""

    def __init__(self):
        self._llm = None

    def _get_llm(self):
        """懒加载 LLM 实例。"""
        if self._llm is None:
            from llama_index.llms.openai_like import OpenAILike
            self._llm = OpenAILike(
                model=DEEPSEEK_MODEL,
                api_base=DEEPSEEK_API_BASE,
                api_key=DEEPSEEK_API_KEY,
                is_chat_model=True,
                temperature=0.3,
                max_tokens=500,
            )
        return self._llm

    def generate_sub_queries(self, question: str) -> List[str]:
        """策略1：生成子问题列表（原问题 + 3个子问题，共4个）。

        Args:
            question: 用户原始问题。

        Returns:
            List[str]: 包含原问题和3个子问题的列表。
        """
        try:
            llm = self._get_llm()
            prompt = self.SUB_QUERY_PROMPT.format(question=question)
            response = llm.complete(prompt)
            sub_queries = [q.strip() for q in str(response).strip().split("\n") if q.strip()][:3]
            # 原问题 + 3个子问题
            return [question] + sub_queries
        except Exception as e:
            print(f"[QueryRewriter] 子问题生成失败，降级为原问题: {e}")
            return [question]

    def compress_query(self, question: str) -> str:
        """策略2：语义压缩，提取关键词。

        Args:
            question: 用户原始问题。

        Returns:
            str: 压缩后的检索query。
        """
        try:
            llm = self._get_llm()
            prompt = self.COMPRESS_PROMPT.format(question=question)
            response = llm.complete(prompt)
            return str(response).strip()
        except Exception as e:
            print(f"[QueryRewriter] 语义压缩失败，降级为原问题: {e}")
            return question
