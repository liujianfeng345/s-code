# s-code — AI 编码助手

基于 **LangGraph** + **LangChain** 构建的 AI 编码助手 CLI 工具，由 **DeepSeek Chat** 模型驱动，具备安全的文件操作沙箱能力。

## 功能特性

- **智能对话** — 通过命令行与 AI 对话，获取代码分析、解释和生成建议
- **文件读取** — 安全地读取工作区内的文件内容（限制 10MB）
- **目录浏览** — 列出工作区目录结构，快速了解项目布局
- **安全沙箱** — 所有文件操作限制在 `workspace` 目录内，防止路径穿越攻击
- **工具调用** — 基于 LangGraph 原生的 `ToolNode` 和 `tools_condition`，实现 LLM 自动决策与工具调用

## 技术栈

| 组件 | 技术 |
|------|------|
| 核心框架 | LangGraph, LangChain Core |
| 语言模型 | DeepSeek Chat（OpenAI 兼容 API） |
| 运行环境 | Python 3.11+ |
| 包管理器 | uv |
| 配置管理 | pydantic-settings |

## 快速开始

### 前置要求

- Python 3.11+
- uv 包管理器
- DeepSeek API Key

### 安装

```bash
# 1. 克隆项目
git clone <repository-url>
cd s-code

# 2. 创建虚拟环境并安装依赖
uv sync

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 DEEPSEEK_API_KEY

# 4. 创建工作区目录
mkdir -p workspace
```

### 运行

```bash
uv run python -m src.main
```

启动后进入交互模式，输入问题即可开始对话。输入 `quit` 或 `exit` 退出。

## 项目结构

```
s-code/
├── src/
│   ├── main.py                # CLI 入口
│   ├── agent/
│   │   ├── graph.py           # LangGraph 图定义
│   │   ├── state.py           # 状态定义（基于 add_messages）
│   │   ├── nodes.py           # LLM 推理节点
│   │   └── tools.py           # 工具函数（读文件、列目录）
│   ├── cli/
│   │   └── interface.py       # 交互式 CLI 界面
│   └── utils/
│       ├── settings.py        # 配置管理（环境变量）
│       └── security.py        # 路径安全校验
├── workspace/                 # 安全操作沙箱目录
├── pyproject.toml             # 项目配置与依赖
├── .env.example               # 环境变量示例
└── README.md
```

## 工作流程

```
用户输入 → LLM 推理 & 决策
                   ↓
            ┌ 需要工具？
            ↓          ↓
           是          否
            ↓          ↓
        工具执行     生成响应
            ↓          ↓
        更新状态 →  LLM 推理
```

- **agent 节点**: 将用户消息和系统提示词送入 LLM，LLM 可自主决定是否调用工具
- **tools 节点**: 自动解析 LLM 返回的 `tool_calls` 并执行对应工具
- **条件边**: `tools_condition` 根据 LLM 输出自动路由——有工具调用则走向 tools，否则结束

## 安全机制

- **路径沙箱**: 所有文件操作路径经 `Path.resolve()` 规范化后，强制前缀匹配 `workspace_root`
- **大小限制**: 读取文件限制最大 10MB，防止内存溢出
- **目录穿越防御**: 拒绝 `../../../etc/passwd` 等越权路径访问

## 扩展路线图

- [ ] 文件写入工具（含用户确认机制）
- [ ] 代码搜索工具（正则/grep）
- [ ] 对话历史持久化（langgraph-checkpoint-sqlite）
- [ ] RAG 代码库检索（向量数据库）
- [ ] Docker 沙箱代码执行
- [ ] 更多工具集成（Git 操作、代码格式化等）

## 许可证

MIT
