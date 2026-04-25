from langchain_core.messages import HumanMessage, AIMessage, AnyMessage
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command

from ..agent.interrupt import InterruptHandler


class CodingAssistantCLI:
    def __init__(self, graph: CompiledStateGraph, config: dict):
        self.graph = graph
        self.config = config

    # ───────────── 主入口，只负责交互循环 ─────────────
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

            await self._process_user_input(user_input)

    # ───────────── 单次用户交互的完整处理 ─────────────
    async def _process_user_input(self, user_input: str):
        """处理一条用户输入：执行图并处理可能的中断"""
        inputs = {"messages": [HumanMessage(content=user_input)]}
        await self._astream_and_print(inputs)          # 正常执行
        await self._handle_pending_interrupts()        # 处理遗留挂起

    # ───────────── 流式执行并打印消息 ─────────────
    async def _astream_and_print(self, inputs=None, resume_command: Command = None):
        """
        执行图的流式输出，将包含文本的 AIMessage 打印到终端。
        inputs 和 resume_command 择一传入（普通执行传 inputs，中断恢复传 command）。
        """
        if resume_command is not None:
            stream = self.graph.astream(
                resume_command, config=self.config, stream_mode="values"
            )
        else:
            stream = self.graph.astream(
                inputs, config=self.config, stream_mode="values"
            )

        async for event in stream:
            last_msg = event["messages"][-1]
            self.safe_print_ai_message(last_msg)

    # ───────────── 处理图中断挂起 ─────────────
    async def _handle_pending_interrupts(self):
        """循环检查并处理图挂起，使用 InterruptHandler 统一调度"""
        state = await self.graph.aget_state(self.config)
        while state.next:                       # 图处于挂起状态
            last_msg = state.values["messages"][-1]
            if not (isinstance(last_msg, AIMessage) and last_msg.tool_calls):
                break                           # 非预期的挂起，直接退出

            handled = False
            for tool_call in last_msg.tool_calls:
                command = await InterruptHandler.handle(
                    tool_call, self.graph, self.config
                )
                if command is not None:
                    await self._astream_and_print(resume_command=command)
                    handled = True
                    break                       # 一次只处理一个中断

            if not handled:
                # 未注册中断类型的工具，跳过并继续
                break

            # 恢复执行后，刷新状态，继续检查是否还有挂起
            state = await self.graph.aget_state(self.config)

    # ───────────── 辅助：安全打印 AI 消息 ─────────────
    def safe_print_ai_message(self, msg: AnyMessage):
        """只打印有实际文本内容的 AIMessage，忽略工具调用等中间消息"""
        if (
            isinstance(msg, AIMessage)
            and hasattr(msg, "content")
            and msg.content
            and not getattr(msg, "tool_calls", None)
        ):
            print(f"\n助手: {msg.content}")
