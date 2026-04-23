from langchain_core.tools import tool
from pathlib import Path
from ..utils.security import validate_path

@tool
def read_file(file_path: str) -> str:
    """读取指定路径的文件内容（最大10MB）"""
    try:
        abs_path = validate_path(file_path)
        if not abs_path.exists():
            return f"错误：文件 {file_path} 不存在。"
        if abs_path.stat().st_size > 10 * 1024 * 1024:
            return "错误：文件超过10MB限制。"
        return abs_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"读取失败：{str(e)}"

@tool
def list_files(directory: str = "") -> str:
    """列出工作区内指定目录 (默认根目录) 下的文件和子目录"""
    try:
        abs_dir = validate_path(directory if directory else ".")
        if not abs_dir.is_dir():
            return f"错误：路径 {directory} 不是目录。"
        items = sorted(abs_dir.iterdir())
        if not items:
            return "目录为空。"
        lines = []
        for item in items:
            typ = "📁" if item.is_dir() else "📄"
            lines.append(f"{typ} {item.name}")
        return "\n".join(lines)
    except Exception as e:
        return f"列出目录失败：{str(e)}"

# 导出工具列表
tools = [read_file, list_files]