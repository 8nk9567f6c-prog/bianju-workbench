---
name: bianju-workstation
description: 短剧编剧工作台 v7.0——职业下沉市场短剧创作 Agent 系统。四 Agent 调度框架(调度→选题调研→大纲搭建→内容扩充)，100集×5w+字标准化产出，SS/S+ 爆款算法，收敛式修订循环(Forge Loop: Reader-Sim+Critic四通道)，逐幕张力0-10量化，双模情绪引擎(情绪银行+情绪弹簧)，35斜杠命令，8基因对标+风格指纹，MCP 自动验证(17工具80+项)。融合救猫咪+麦基+悉德菲尔德+红果算法+drama-creator方法论+好莱坞评估标准。
version: "7.0.0"
author: "编剧工作台"
tags: [screenwriting, short-drama, content-creation, chinese, script-writing, agent-pipeline, forge-convergence-loop]
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
  - Agent
  - Skill
---

# 编剧工作台 v7.0 — 短剧创作 Skill

## 能力概述

为下沉市场（30岁以上用户，80%消费时长）创作标准化 100 集 × 5w+ 字短剧剧本。以 SS/S+ 爆款算法（10维100分制，S+≥85分）为最高优先级。v7.0 新增收敛式修订循环（Forge Loop）、逐幕张力0-10量化、五维文学润色、风格指纹漂移自动检测、故事圣经自动同步。

### v7.0 核心升级 vs 竞品

| 能力维度 | 编剧工作台 v7.0 | drama-creator v2.2 | @gonzih screenwriting |
|----------|----------------|-------------------|----------------------|
| 智能体流水线 | ★四 Agent 调度(调度→选题→大纲→内容) | — | — |
| 收敛式修订循环 | ★Forge Loop (Reader-Sim+Critic四通道+Revision-Writer ≤3轮) | — | — |
| 逐幕张力量化 | ★0-10 张力曲线+MCP自动验证 | — | — |
| 情绪引擎 | ★双模(情绪银行+情绪弹簧) | 情绪弹簧 | — |
| 命令数量 | 35 斜杠命令 | 4 任务模式 | 4 斜杠命令 |
| 审核体系 | 自审内置(写作+平台+格式+节奏+读者体验) | — | — |
| MCP 自动验证 | 17 工具 80+ 项 | — | — |
| 对标拆解 | 8 基因 + 7维风格指纹 | — | — |
| S+ 评分 | 11 维 100 分制(新增张力设计) | — | — |
| 文学润色 | ★五维润色(P/I/S/M/Se)+声纹校准 | — | ✓ (punch-up) |
| 剧本评估 | ✓ (Coverage+S+) | — | ✓ (Coverage) |
| 风格漂移检测 | ★自动(--baseline基线对比) | — | — |
| 故事圣经同步 | ★自动(剧本→圣经回写) | — | — |

## 文件结构

```
编剧工作台/
├── CLAUDE.md              ← 主 Agent 指令集（v7.0：35斜杠命令 + 四 Agent 调度 + 收敛式修订循环 + 17 MCP工具）
├── CORE_CREATIVE_DNA.md   ← 永久记忆（领域知识：S+评分/黄金四步/情绪银行/算法铁律）
├── SKILL.md               ← 本文件（Skill 元数据 + 分发入口）
├── .claude/
│   ├── settings.json      ← Hooks（SessionStart/Stop/PreToolUse）
│   ├── mcp.json           ← MCP 服务器配置（16个自动验证工具）
│   └── skills/            ← 可安装到其他项目的 skill 副本
├── .claudeignore          ← 上下文污染防护
├── agents/                ← ★v7.0 四 Agent 调度系统 + 收敛式修订循环
│   ├── README.md           ← Agent 系统总览 + 流水线编排指南
│   ├── agent_topic_research.md       ← Agent 1: 选题调研智能体
│   ├── agent_outline_construction.md ← Agent 2: 大纲搭建智能体
│   └── agent_content_expansion.md    ← Agent 3: 内容扩充智能体
├── scripts/
│   ├── validators.py      ← 65项自动化验证引擎
│   ├── mcp_server.py      ← MCP stdio JSON-RPC 服务器（零外部依赖）
│   ├── auto_fix.py        ← 自动修复引擎（AI腔/格式）
│   ├── save_docx.py       ← Markdown → Word 转换
│   ├── save_check.py      ← 自检报告累计保存
│   ├── save_checkpoint.py ← 会话检查点自动保存
│   └── md2docx.py         ← Markdown → Word 核心引擎
├── docs/                  ← PWA 网页应用（规则数据库 + 仪表盘）
└── 素材库/                ← 热梗名梗·爆款台词素材库
```

## 启动方式

**方式 A：作为项目打开**（推荐）
直接在 Claude Code 中打开 `编剧工作台/` 目录，CLAUDE.md 自动加载。

**方式 B：安装为 Skill**
将本目录复制到目标项目的 `.claude/skills/bianju-workstation/`，通过 `/bianju-workstation` 调用。

**方式 C：MCP 工具独立使用**
在其他项目中配置 `.claude/mcp.json` 引用 `scripts/mcp_server.py`，获得 7 个自动验证工具。

## MCP 工具（独立使用）

```json
{
  "mcpServers": {
    "bianju-validators": {
      "command": "python",
      "args": ["路径/scripts/mcp_server.py"]
    }
  }
}
```

16 个工具：`validate_episode` / `check_writing_redlines` / `check_format` / `check_platform_redlines` / `check_content_rules` / `check_rhythm` / `check_emotion_spring` / `check_emotion_spring_full` / `check_emotion_anchors` / `check_emotion_beat_template` / `check_character_emotion_range` / `check_emotion_bank` / `check_paywall_ramp` / `check_info_frontloading` / `check_dialogue_quality` / `validate_multi_episodes`

## 核心命令速查

输入 `/` 查看全部 35 个斜杠命令。关键流程：

**v7.0 四 Agent 调度流水线（一键全流程）**：
```
/流水线 → Agent 1 选题调研(等确认) → Agent 2 大纲搭建(等确认) → Agent 3 内容扩充(五阶段等确认) → /导出
```

**传统手动流程**：
```
/新项目 → /对标 → /备忘 → /简介 → /人物 → /大纲(等确认) → /梗概
→ /一审(1-3集) → /审核1 → /二审(4-10集) → /审核2
→ /三审(11-30集) → /审核3 → /50集(31-50集) → /审核50
→ /完本(51-100集) → /终审 → /导出
```

每个审核命令自动启动 5 个并行 Agent（剧情大纲/人物设定/已有逻辑/平台红线/格式规范）。

**三智能体独立调用**：`/选题调研` `/大纲搭建` `/内容扩充`——适合只需要某个阶段的场景。

## 技术架构

- **语言**：Python 3.12+（仅 stdlib，零外部依赖）
- **协议**：MCP JSON-RPC 2.0 over stdio
- **配置**：.claude/mcp.json + .claude/settings.json (hooks)
- **部署**：本地 Claude Code + MCP server 子进程
