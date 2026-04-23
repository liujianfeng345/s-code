from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain.chat_models import BaseChatModel
from .state import AgentState
from .nodes import call_llm
from .tools import tools

def build_graph(llm: BaseChatModel):
    workflow = StateGraph(AgentState)

    llm_with_tools = llm.bind_tools(tools)

    # 添加节点
    workflow.add_node("agent", lambda state: call_llm(state, llm_with_tools))
    workflow.add_node("tools", ToolNode(tools))

    # 控制流
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
