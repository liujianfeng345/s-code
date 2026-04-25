from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_name: str = "deepseek-chat"
    workspace_root: str = "./workspace"

    # HITL 配置
    hitl_confirm_write: bool = True        # 写文件是否需要确认
    hitl_confirm_delete: bool = True       # 删除文件是否需要确认
    hitl_confirm_command: bool = True      # 执行命令是否需要确认
    hitl_auto_approve_readonly: bool = True  # 只读操作自动批准

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"