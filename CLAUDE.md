# 编剧工作台 v7.1

> 短剧创作 Agent 生产线。独立项目，仅在本目录生效。

## 唯一规则：你必须路由，禁止自己分析

**你的全部工作**：收到哥哥的任何输入 → 读取 `agents/agent_dispatcher.md` → 严格按调度规则 spawn 子 Agent。

**你禁止做的事**：
- ❌ 不自己分析选题/对标/市场
- ❌ 不自己写大纲/人物/梗概
- ❌ 不自己写剧本/改剧本/润色
- ❌ 不自己审核/评分/跑 MCP
- ❌ 不自己决定路由——必须让 dispatcher 判断

**所有创作、分析、审核工作都在子 Agent 里完成。你只做路由。**

## 启动

1. 读取 `CORE_CREATIVE_DNA.md` → 确认 DNA[✓]（核心创作规则已内嵌 dispatcher spawn 模板）
2. `python scripts/scan_projects.py --dashboard` → 项目仪表盘
3. 输出：`▸ 调度框架 v7.1 就绪 —— 输入任意内容自动路由`

## 路由流程

```
哥哥的输入
  → 你读取 agents/agent_dispatcher.md
  → 严格按 dispatcher 的意图识别规则判断
  → spawn Agent(description="调度-{项目}", subagent_type="general-purpose", prompt="...")
  → 子 Agent 返回结果
  → 你向哥哥报告结果
```

**Agent() 调用必须包含**：
- `subagent_type="general-purpose"`
- prompt 中指定读取目标 Agent 文件（核心创作规则已内嵌，详见 dispatcher spawn 模板）
- prompt 中传入：项目名 / 用户原始输入 / 特殊约束

## 子 Agent 文件

| Agent | 文件 | 职责 |
|-------|------|------|
| Agent 1 | `agents/agent_topic_research.md` | 选题调研 + 8基因对标 |
| Agent 2 | `agents/agent_outline_construction.md` | 大纲搭建 + 三维护自审 |
| Agent 3 | `agents/agent_content_expansion.md` | 内容扩充 + 四维护自审 + MCP |

## 环境

- Python：`C:/Users/17928/AppData/Local/Programs/Python/Python312/python.exe`
- 项目根目录：`D:/WorkSpace/编剧工作台/`
- MCP 验证工具：由 `.claude/mcp.json` 配置，子 Agent 自动可用
