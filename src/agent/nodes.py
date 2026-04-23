from langchain_core.messages import SystemMessage
from langchain.chat_models import BaseChatModel
from .state import AgentState

SYSTEM_PROMPT = """
你是一个AI编码助手，运行在用户指定的 workspace 沙箱中。
可以使用 read_file 读取文件内容，使用 list_files 浏览目录。
回答问题时尽量引用已读取的代码，给出清晰、具体的建议。
"""

def call_llm(state: AgentState, llm_with_tools: BaseChatModel):
    """调用LLM并返回新的AI消息"""
    # TODO: 系统提示词的添加方式，这样加的会每次都会叠加
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}
