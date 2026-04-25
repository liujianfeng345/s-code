from langgraph.types import Command

class InterruptHandler:
    """通用中断处理器，支持多种工具的中断确认"""

    # 各工具的确认配置
    CONFIG = {
        "write_file": {
            "prompt": "[⚠️ 安全警告] 助手请求写入文件",
            "preview_attrs": ["file_path", "content"],
            "preview_max_len": 500,
            "require_confirmation": True,
        },
    }

    @classmethod
    async def handle(cls, tool_call: dict, graph, config) -> Command | None:
        """处理单个中断调用，返回恢复命令或 None"""
        tool_name = tool_call["name"]
        cfg = cls.CONFIG.get(tool_name)
        if cfg is None:
            return None  # 未注册的中断类型，跳过

        # 展示中断信息
        cls._display_interrupt(tool_call, cfg)

        # 如果不需要确认，直接通过
        if not cfg.get("require_confirmation", True):
            return Command(resume="yes")

        # 获取用户确认
        decision = await cls._get_user_decision(cfg)
        return Command(resume=decision)

    @classmethod
    def _display_interrupt(cls, tool_call: dict, cfg: dict):
        print(f"\n{cfg['prompt']}")
        for attr in cfg.get("preview_attrs", []):
            value = tool_call["args"].get(attr, "")
            max_len = cfg.get("preview_max_len", 500)
            if max_len > 0 and len(value) > max_len:
                value = value[:max_len] + "..."
            print(f"  {attr}: {value}")

    @classmethod
    async def _get_user_decision(cls, cfg: dict) -> str:
        while True:
            decision = input("确认执行? (yes/no) ").strip().lower()
            if decision in ("yes", "y", "ok"):
                if cfg.get("double_confirm"):
                    second = input("再次确认? (yes/no) ").strip().lower()
                    if second not in ("yes", "y"):
                        return "no"
                return "yes"
            if decision in ("no", "n"):
                return "no"
            print("请输入 yes 或 no。")
