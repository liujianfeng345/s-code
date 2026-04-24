"""主应用入口 —— 用于测试 AI 编码助手"""

import json
from pathlib import Path
from typing import Optional

from utils import load_config, format_bytes

VERSION = "0.1.0"
DEFAULT_CONFIG = "config.yaml"


class App:
    """应用主类"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or DEFAULT_CONFIG
        self.config = {}
        self.cache: dict[str, bytes] = {}

    def load_config(self) -> dict:
        """加载配置文件"""
        self.config = load_config(self.config_path)
        return self.config

    def get_cache_size(self) -> str:
        """获取缓存大小（人类可读格式）"""
        total = sum(len(v) for v in self.cache.values())
        return format_bytes(total)

    def clear_cache(self) -> None:
        """清空缓存"""
        self.cache.clear()

    def run(self):
        """启动应用"""
        self.load_config()
        print(f"App v{VERSION} 已启动")
        print(f"配置: {json.dumps(self.config, indent=2, ensure_ascii=False)}")
        print(f"缓存条目: {len(self.cache)}")


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
