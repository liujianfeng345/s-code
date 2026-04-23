from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_name: str = "deepseek-chat"
    workspace_root: str = "./workspace"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"