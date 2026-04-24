"""工具函数模块 —— 用于测试 AI 编码助手"""

import json
import hashlib
import re
from pathlib import Path


def load_config(path: str) -> dict:
    """加载 YAML/JSON 配置文件"""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")

    raw = p.read_text(encoding="utf-8")

    if p.suffix in (".yaml", ".yml"):
        # 简化 YAML 解析（仅支持 flat key-value）
        return parse_simple_yaml(raw)
    elif p.suffix == ".json":
        return json.loads(raw)
    else:
        raise ValueError(f"不支持的配置格式: {p.suffix}")


def parse_simple_yaml(raw: str) -> dict:
    """简易 YAML 解析器（仅支持顶级 key: value）"""
    result = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def format_bytes(num_bytes: int) -> str:
    """将字节数转换为人类可读格式"""
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def hash_file(file_path: str, algorithm: str = "sha256") -> str:
    """计算文件哈希"""
    h = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(directory: str) -> list[tuple[str, str]]:
    """查找目录中的重复文件（基于 SHA256）"""
    hashes: dict[str, str] = {}
    duplicates: list[tuple[str, str]] = []

    for file_path in Path(directory).rglob("*"):
        if not file_path.is_file():
            continue
        try:
            file_hash = hash_file(str(file_path))
            if file_hash in hashes:
                duplicates.append((hashes[file_hash], str(file_path)))
            else:
                hashes[file_hash] = str(file_path)
        except OSError:
            continue

    return duplicates


def slugify(text: str) -> str:
    """将文本转换为 URL 友好的 slug"""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")
