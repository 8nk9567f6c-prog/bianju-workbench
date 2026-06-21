# 编剧工作台 v7.1

> 短剧创作 Agent 生产线。独立项目，仅在本目录生效。
> **记忆隔离**：本工作台拥有独立记忆库 `.claude/memory/`，不加载其他智能体记忆。可搜索 Obsidian 知识库 `D:\Obsidian\剧本库\` 获取创作素材。

---

## 🎬 哥哥看这里——5 句话搞定

**无需记命令。** 你只需要用自然语言说：

| 说这句话 | 会发生什么 |
|----------|------------|
| **「写一集短剧，主题是xxx」** | 全流程：选题→大纲→剧本，一步步出 |
| **「继续上次的」** | 从上次中断处接着写 |
| **「改一下第x集，xxx」** | 只改指定集数的指定问题 |
| **「审一下这个剧本」** | 跑一遍质量审核，告诉你哪里不行 |
| **「看看我有什么项目」** | 列出所有创作中的作品和进度 |

> 不需要记 `/新项目` `/流水线` 这些东西——那是机器的内部指令。你说人话就行。

---

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

SessionStart Hook 自动运行项目仪表盘 + 就绪提示。只需确认 `CORE_CREATIVE_DNA.md` 可读即可。

## 路由

收到哥哥输入 → 读 `agents/agent_dispatcher.md` → 严格按调度规则 spawn 子 Agent。
路由框架完整说明见 `agents/README.md`。Agent 文件清单：

| Agent | 文件 | 职责 |
|-------|------|------|
| Agent 1 | `agents/agent_topic_research.md` | 选题调研 + 6维评估 |
| Agent 2 | `agents/agent_outline_construction.md` | 大纲搭建 + 三维护自审 |
| Agent 3 | `agents/agent_content_expansion.md` | 内容扩充 + 四维护自审 + MCP |

- Python：`C:/Users/17928/AppData/Local/Programs/Python/Python312/python.exe`
- MCP 验证工具：`.claude/mcp.json` 配置，子 Agent 自动可用

## 提问记录

每次交互后追加到念念跨智能体提问追踪系统（格式见全局 CLAUDE.md）。
