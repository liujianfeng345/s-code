import asyncio
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import AIMessage

class CodingAssistantCLI:
    def __init__(self, graph: CompiledStateGraph, config: dict):
        self.graph = graph
        self.config = config

    async def run_interactive(self):
        print("AI编码助手已启动！输入 'quit' 或 'exit' 退出。")
        while True:
            try:
                user_input = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n再见！")
                break

            if user_input.lower() in ("quit", "exit"):
                break
            if not user_input:
                continue

            inputs = {"messages": [HumanMessage(content=user_input)]}
            try:
                async for event in self.graph.astream(inputs, config=self.config, stream_mode="values"):
                    last_msg = event["messages"][-1]
                    # 只打印不带 tool_calls 的 AI 消息（避免打印中间工具调用）
                    if isinstance(last_msg, AIMessage) and hasattr(last_msg, "content") and last_msg.content and not getattr(last_msg, "tool_calls", None):
                        print(f"\n助手: {last_msg.content}")
            except Exception as e:
                print(f"\n[错误] {str(e)}")