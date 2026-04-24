from langchain_core.tools import tool
from langgraph.types import interrupt
from ..utils.security import validate_path
from ..utils.security import get_workspace_root

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
    
@tool
def write_file(file_path: str, content: str) -> str:
    """写入指定路径的文件内容"""
    abs_path = validate_path(file_path)
    if abs_path.exists() and not abs_path.is_file():
        return f"错误：{file_path} 已存在且不是一个文件。"
    if not abs_path.parent.exists():
        return f"错误：父目录 {abs_path.parent} 不存在。"
    user_decision = interrupt({
        "action": "write_file",
        "path": str(abs_path),
        "preview": content[:500] + ("..." if len(content) > 500 else "")
    })

    # 图恢复后，user_decision 的值是 CLI 传入的 resume 值
    if user_decision.lower() in ['yes', 'y', 'ok']:
        try:
            abs_path.write_text(content, encoding='utf-8')
            return f"成功写入 {file_path}"
        except Exception as e:
            return f"写入失败1：{str(e)}"
    else:
        return "用户取消了文件写入操作。"
    
@tool
def search_code(pattern: str, path: str = ".") -> str:
    """在指定目录下搜索匹配正则的内容（最多返回 50 条）"""
    import re
    from pathlib import Path

    target = validate_path(path)
    if not target.is_dir():
        return f"错误：{path} 不是目录。"

    results = []
    try:
        for file_path in target.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix not in {".py", ".ts", ".js", ".tsx", ".go",
                                         ".rs", ".java", ".yaml", ".yml", ".toml",
                                         ".json", ".md", ".txt"}:
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue
            for i, line in enumerate(content.splitlines(), 1):
                if re.search(pattern, line):
                    results.append(f"{file_path}:{i}: {line.strip()}")
                    if len(results) >= 50:
                        return "\n".join(results)
    except Exception as e:
        return f"搜索出错：{str(e)}"

    return "\n".join(results) if results else "未找到匹配项。"

@tool
def get_file_info(file_path: str) -> str:
    """获取文件元信息：大小、修改时间、行数等"""
    import datetime
    abs_path = validate_path(file_path)
    if not abs_path.exists():
        return f"错误：{file_path} 不存在。"

    stat = abs_path.stat()
    info = {
        "大小": f"{stat.st_size:,} 字节",
        "修改时间": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "是否为文件": abs_path.is_file(),
    }
    if abs_path.is_file():
        try:
            lines = abs_path.read_text(encoding="utf-8").count("\n") + 1
            info["行数"] = lines
        except Exception:
            info["行数"] = "无法读取"
    return "\n".join(f"{k}: {v}" for k, v in info.items())

@tool
def glob_search(pattern: str) -> str:
    """按 glob 模式搜索文件，如 '**/*.py' 或 'src/**/*.ts'"""
    target = get_workspace_root()
    matches = sorted(target.glob(pattern))
    if not matches:
        return f"未找到匹配 '{pattern}' 的文件。"
    # 排除 .venv, node_modules, __pycache__ 等
    exclude_dirs = {".venv", "node_modules", "__pycache__", ".git"}
    filtered = [
        str(m.relative_to(target))
        for m in matches
        if not set(m.parts).intersection(exclude_dirs)
    ]
    return "\n".join(filtered[:100]) if filtered else "所有匹配项均被过滤。"

# 导出工具列表
tools = [read_file, list_files, write_file, search_code, get_file_info, glob_search]