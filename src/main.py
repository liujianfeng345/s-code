import asyncio
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from .agent.graph import build_graph
from .cli.interface import CodingAssistantCLI
from .utils.settings import Settings
from .utils.security import set_workspace_root

async def main():
    # 加载配置
    settings = Settings()
    set_workspace_root(settings.workspace_root)

    # 初始化 LLM
    llm = init_chat_model(settings.model_name)

    db_path = "db/checkpoints.db"
    async with AsyncSqliteSaver.from_conn_string(db_path) as checkpointer:
        # 构建图
        graph = build_graph(llm, checkpointer)

        # 配置（用于后续持久化，第一周使用空配置）
        config = {"configurable": {"thread_id": "session-1"}}

        # 启动 CLI
        cli = CodingAssistantCLI(graph, config)
        await cli.run_interactive()

if __name__ == "__main__":
    asyncio.run(main())
