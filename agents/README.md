# 编剧工作台 — Agent 调度框架 v8.0

> **v8.0：主编+写手分工模式。DeepSeek Agent 只创作，念念主编负责审查+修改提示词。**
> **目标**：红果短剧 下沉赛道 男频/女频爽文

---

## 系统架构

```
哥哥说话 → 念念（主编）
              │
              ├── 简单任务 → 念念自己做
              │
              ├── 重任务 → spawn DeepSeek Agent（写手）
              │     ├── Agent 1: 选题调研（联网搜索+竞品分析）
              │     ├── Agent 2: 大纲搭建（ANCHOR+分段大纲）
              │     └── Agent 3: 剧本写作（v5.0格式剧本）
              │
              └── Agent产出 → 念念审查 → ✅过/⚠改/❌重写 → 正循环
```

**核心变化（v7.x → v8.0）**：
- Agent 不再自审、不再打分——念念独立审查
- 简单任务念念直接做，不 spawn
- spawn prompt 规则从 150+ 条砍到 ~25 条
- 负向禁令全部转为正向指令
- 用户指令放在 prompt 最前面

---

## Agent 清单

| Agent | 文件 | 角色 | 产出 |
|-------|------|------|------|
| **Agent 1** — 选题 | `agent_topic_research.md` | 市场情报分析 | 调研报告 |
| **Agent 2** — 大纲 | `agent_outline_construction.md` | 结构架构师 | ANCHOR.md + 分段大纲 |
| **Agent 3** — 剧本 | `agent_content_expansion.md` | 制片编剧 | v5.0格式剧本 |

---

## 文件结构

```
agents/
├── README.md
├── agent_dispatcher.md        ← 调度框架 + spawn prompt 模板 + 念念审查清单
├── agent_topic_research.md    ← Agent 1: 选题调研
├── agent_outline_construction.md ← Agent 2: 大纲搭建
├── agent_content_expansion.md ← Agent 3: 剧本写作
└── references/                ← 参考文件（按需加载）
    ├── evaluation_rubric.md   ← 竞品评估标准
    └── gene_8_criteria.md     ← 对标拆解标准

scripts/
├── scan_projects.py           ← 项目扫描（SessionStart自动运行）
├── save_checkpoint.py         ← 会话检查点（Stop自动运行）
├── sync_to_obsidian.py        ← Obsidian同步（手动触发）
└── create_shortcut.py         ← 桌面快捷方式（一次性工具）
```

---

## 工作流

### 新项目完整流水线

```
哥哥「我想写战神归来题材」
  → 念念 spawn Agent 1 → 调研报告
    → 哥哥确认方向
      → 念念 spawn Agent 2 → ANCHOR + 大纲
        → 念念审查大纲
          → 哥哥确认
            → 念念 spawn Agent 3 → 剧本
              → 念念逐集审查 → 过/改
```

### 修改已有剧本

```
哥哥「改第5集对白，太文绉绉了」
  → 念念直接读文件 → 改 → 写回 → 告诉哥哥改了什么
```

## 设计原则

1. **主编独立审查** — 写手不管质量，主编独立判断
2. **正向指令** — 告诉模型做什么，不是不做什么
3. **用户指令优先** — prompt结构：用户要什么 → 上下文 → 规则 → 格式
4. **简单直接** — 能念念自己干的就自己干，不 spawn
