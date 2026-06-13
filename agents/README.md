# 编剧工作台 — 四 Agent 调度框架 v7.0

> **v7.0**: 收敛式修订循环 + 逐幕张力0-10量化 + 五维文学润色 + 故事圣经自动同步 + MCP 17工具。审核+对标全部内置为自审系统。
> **目标**: 红果短剧 下沉赛道 男频/女频爽文 SS/S+ 爆款（S+ ≥ 85/100）

## 系统架构

```
用户输入 → /调度 (Agent 0 — 唯一入口)
              │
              │  识别意图 → 匹配项目 → 路由
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
Agent 1   Agent 2   Agent 3
选题调研   大纲搭建   内容扩充
(市场+对标) (蓝图+自审) (剧本+自审+MCP)
```

**核心变更**：审核不再是独立 Agent 层，而是 Agent 2/3 的内置自审环节。对标不再是独立 Agent 层，而是 Agent 1 的内置分析能力。

## 四 Agent 清单

| Agent | 文件 | 角色 | 内置能力 | 门禁 |
|-------|------|------|---------|------|
| **Agent 0** — 调度 | `agent_dispatcher.md` | 唯一入口，总控框架。识别意图→匹配项目→路由 | 项目管理（新项目/导入/检测） | 路由必须经用户确认 |
| **Agent 1** — 选题 | `agent_topic_research.md` | 市场情报分析，选题爆款验证 | **8 基因对标**（钩子/节奏/情绪/人物/爽点/台词/付费/切片）+ 竞品分析 + 选题 S+ 评分 | S+ ≥ 85/100 |
| **Agent 2** — 大纲 | `agent_outline_construction.md` | 故事结构架构师，产出创作蓝图 | **三维护大纲自审**（剧情一致性 12 项/人物一致性 10 项/逻辑一致性 11 项）+ 分段/全量/局部修改 | S+ ≥ 85/100 + ANCHOR 八节完整 + 自审通过 |
| **Agent 3** — 剧本 | `agent_content_expansion.md` | 制片编剧，逐集写 v5.0 格式剧本 | **四维护剧本自审 + 收敛式修订循环**（Reader-Sim + Critic四通道） + **五维文学润色** + MCP 17工具自动验证 + 定向修改 | S+ ≥ 85/100 + 自审通过 |

## 自审系统对照（v7.0 吸收合并）

| 原独立 Agent | 原文件 | v6.0 去向 |
|-------------|--------|----------|
| 剧情大纲审核 | `review/agent_1_plot_outline.md` | → **Agent 2 自审维度一**（剧情一致性 12 项） |
| 人物设定审核 | `review/agent_2_character.md` | → **Agent 2 自审维度二**（人物一致性 10 项） |
| 已有逻辑审核（大纲级） | `review/agent_3_logic.md` | → **Agent 2 自审维度三**（逻辑一致性 11 项） |
| 已有逻辑审核（剧本级） | `review/agent_3_logic.md` | → **Agent 3 自审维度一**（写作红线+铁律 15 项） |
| 平台红线审核 | `review/agent_4_platform.md` | → **Agent 3 自审维度二**（平台红线 12 项） |
| 格式规范审核 | `review/agent_5_format.md` | → **Agent 3 自审维度三**（格式规范 15 项） |
| 8 基因对标 (×8) | `bidui/agent_gene_*.md` | → **Agent 1 专精领域知识**（竞品 8 基因对标章节） |

## 文件结构

```
agents/
├── README.md                         ← 本文件
├── FOUNDATION.md                     ← 底层创作宪法（所有 Agent 强制预加载）
├── agent_dispatcher.md               ← Agent 0: 调度框架
├── agent_topic_research.md           ← Agent 1: 选题调研（内置 8 基因对标）
├── agent_outline_construction.md     ← Agent 2: 大纲搭建（内置三维护大纲自审）
├── agent_content_expansion.md        ← Agent 3: 内容扩充（内置四维护剧本自审 + MCP 17 工具）
└── references/                       ← 按需加载参考文件（渐进披露）
    ├── gene_8_criteria.md            ← Agent 1 步骤 3 读取：8 基因完整拆解标准
    ├── outline_review_checklist.md   ← Agent 2 自审时读取：33 项大纲自审清单
    └── script_review_checklist.md    ← Agent 3 自审时读取：58 项剧本自审清单

scripts/
├── scan_projects.py                  ← 项目扫描（供 Agent 0 使用）
├── validate_handoff.py               ← 交接协议验证（供 Agent 1/2/3 Pre-flight 使用）
├── save_docx.py                      ← Word 正文导出
├── save_check.py                     ← Word 自检导出
└── sync_to_obsidian.py              ← Obsidian 自动同步
```

## 工作流

### 新项目完整流水线

```
/调度 "我想写一个战神归来题材的短剧"
  → Agent 0 识别"新项目意图" → 路由到 Agent 1
    → Agent 1: 市场扫描 → 8 基因对标 → 2-3 候选选题 → S+ 评分 → 用户确认 → 调研报告
      → 用户确认后，/调度 "开始搭大纲"
        → Agent 0 识别"大纲意图" → 路由到 Agent 2
          → Agent 2: 北极星 → 人物 → 金手指 → 分段大纲 → 每段自审 → 用户逐段确认
            → 某段确认后，/调度 "开始写剧本"
              → Agent 0 识别"剧本意图" → 路由到 Agent 3
                → Agent 3: 按段启动写剧本 → 每集 MCP 验证 → 每阶段自审 → 用户确认
```

### 定向修改（不走流水线）

```
/调度 "修改第15集大纲，结尾钩子改成悬念类型"
  → Agent 0 识别"大纲修改" → 匹配项目 → 路由到 Agent 2
    → Agent 2: 进入局部修改模式 → 单集修改 → 衔接校验 → 自审 → 完成

/调度 [粘贴一集剧本] "把这段对白改得更霸气"
  → Agent 0 识别"剧本修改" → 匹配项目 → 路由到 Agent 3
    → Agent 3: 进入定向修改 → 修改 → MCP 验证 → 完成
```

## 设计原则

1. **调度优先** — 用户不直接调用子 Agent，一切通过 `/调度` 路由
2. **自审内置** — 审核不是独立步骤，而是 Agent 2/3 工作流的内置强制环节
3. **对标融入** — 8 基因分析不是独立流程，而是 Agent 1 选题调研的组成部分
4. **门禁不妥协** — 任何阶段 S+ < 85 = 停止推进，自审有极高/高问题 = 不可交付
5. **分段迭代** — Agent 2 分段产出大纲，Agent 3 按段启动写剧本，不满意可回退
6. **Markdown 交接** — Agent 之间通过项目目录下 .md 文件传递数据（调研报告 → ANCHOR.md → 剧本）
7. **脚本配套** — 确定性操作（项目扫描/交接验证）使用 Python 脚本而非 Agent 指令，消除手工扫描的不确定性
8. **渐进披露** — 大表格（自审清单/基因标准）不内联在 Agent 文件中，而是在对应步骤按需读取 references/ 目录
