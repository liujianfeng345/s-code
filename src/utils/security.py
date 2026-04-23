from pathlib import Path
import os

# 工作区根路径（在加载配置后初始化）
_workspace_root: Path = None

def set_workspace_root(root: str):
    global _workspace_root
    _workspace_root = Path(root).resolve()
    print(f"工作目录已设置为: {_workspace_root}")

def get_workspace_root() -> Path:
    if _workspace_root is None:
        raise RuntimeError("工作区根路径未初始化，请先调用 set_workspace_root()")
    return _workspace_root

def validate_path(user_path: str) -> Path:
    """校验并返回绝对路径，确保在 workspace 内"""
    root = get_workspace_root()
    abs_path = (root / user_path).resolve()
    if not str(abs_path).startswith(str(root)):
        raise ValueError(f"安全限制：拒绝访问 workspace 外的路径 {user_path}")
    return abs_path
