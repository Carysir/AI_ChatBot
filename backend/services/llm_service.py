"""LLM 大模型调用服务"""
from openai import OpenAI

from backend.config import settings

# 各厂商 API 基础地址
PROVIDER_BASE_URLS = {
    "zhipu": "https://open.bigmodel.cn/api/paas/v4/",
    "openai": "https://api.openai.com/v1",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
}

# 默认模型
PROVIDER_MODELS = {
    "zhipu": "glm-4-flash",
    "openai": "gpt-3.5-turbo",
    "qwen": "qwen-turbo",
}


class LLMService:
    """大模型调用服务（兼容 OpenAI 接口格式）"""

    def __init__(self):
        provider = settings.LLM_PROVIDER
        base_url = settings.LLM_BASE_URL or PROVIDER_BASE_URLS.get(provider, "")
        model = settings.LLM_MODEL or PROVIDER_MODELS.get(provider, "")

        self.model = model
        self.client = OpenAI(api_key=settings.LLM_API_KEY, base_url=base_url)

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """调用大模型聊天接口"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"调用大模型失败: {str(e)}"

    def chat_with_context(
        self,
        query: str,
        context_docs: list[dict],
        history: list[dict] = None,
    ) -> str:
        """带知识库上下文的问答"""
        # 构建上下文
        context_text = "\n\n".join(
            [f"【文档片段 {i+1}】\n{doc['content']}" for i, doc in enumerate(context_docs)]
        )

        system_prompt = f"""你是一个智能问答助手。请根据以下参考资料回答用户的问题。
如果参考资料中没有相关信息，请如实告知用户你无法从知识库中找到答案，但可以尝试根据自己的知识回答。
回答时请标注信息来源（如"根据文档片段X"）。

参考资料：
{context_text}
"""

        messages = [{"role": "system", "content": system_prompt}]

        # 添加历史对话
        if history:
            messages.extend(history[-6:])  # 最近3轮对话

        messages.append({"role": "user", "content": query})

        return self.chat(messages)

    def classify_intent(self, query: str) -> str:
        """意图识别"""
        system_prompt = """你是一个意图分类器。请将用户的输入分类为以下意图之一，只返回意图标签：
- chat: 闲聊、打招呼、日常对话
- qa: 知识问答、信息查询
- task: 任务指令（如翻译、总结、写作等）

只返回标签，不要其他内容。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        result = self.chat(messages, temperature=0.1, max_tokens=10)
        result = result.strip().lower()

        if result in ("chat", "qa", "task"):
            return result
        # 简单规则兜底
        if any(w in query for w in ["你好", "嗨", "在吗", "你是谁"]):
            return "chat"
        return "qa"


# 全局实例
llm_service = LLMService()
