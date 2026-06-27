---
name: bianju-workstation
description: 短剧编剧工作台 v8.0——主编+写手分工模式。念念主编负责审查+提示词工程，DeepSeek Agent 负责调研/大纲/剧本执行。100集 v5.0 格式标准化产出，规则三层分级(⛔硬红线/⚡核心约束/💡优化建议)，正向指令优先。
version: "9.2"
author: "编剧工作台"
tags: [screenwriting, short-drama, content-creation, chinese, script-writing, editor-writer-workflow, minimalist]
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

# 编剧工作台 v8.0 — 短剧创作 Skill

## 能力概述

为下沉市场创作标准化 100 集短剧剧本。v8.0 核心变化：**主编+写手分工**——念念独立审查，DeepSeek Agent 专注创作。规则从 150+ 条砍到 ~25 条核心约束，负向禁令全部转为正向指令。

### v8.0 核心升级 vs v7.x

| 维度 | v7.x | v8.0 |
|------|------|------|
| 分工模式 | Agent 自写自审 | 念念独立审查 + DeepSeek 纯写 |
| 规则数量 | ~150条 | ~25条核心 |
| 规则类型 | 大量"禁止" | 正向指令 |
| 规则冗余 | 三层（spawn+agent+references） | 一层（spawn prompt） |
| 确认步骤 | 每次路由确认 | 高置信度直接干 |
| 简单任务 | 必须 spawn | 念念直接做 |
| PostToolUse | 每次写文件自动同步 | 手动触发 |
| 启动速度 | 30-60秒 | 5-15秒 |

## 文件结构

```
编剧工作台/
├── CLAUDE.md              ← 主编指令（v8.0：念念职责+审查清单+路由规则）
├── CORE_CREATIVE_DNA.md   ← 创作宪法（三层分级：⛔⚡💡）
├── SKILL.md               ← 本文件
├── .claude/
│   └── settings.json      ← Hooks（SessionStart+Stop）
├── agents/
│   ├── README.md           ← v8.0 架构总览
│   ├── agent_dispatcher.md ← 调度框架+spawn模板+念念审查清单
│   ├── agent_topic_research.md       ← Agent 1: 选题调研
│   ├── agent_outline_construction.md ← Agent 2: 大纲搭建
│   ├── agent_content_expansion.md    ← Agent 3: 剧本写作
│   └── references/
│       ├── evaluation_rubric.md      ← 竞品评估标准
│       └── gene_8_criteria.md        ← 对标拆解标准
├── scripts/
│   ├── scan_projects.py     ← 项目扫描
│   ├── save_checkpoint.py   ← 会话检查点
│   ├── sync_to_obsidian.py  ← Obsidian同步（手动触发）
│   └── create_shortcut.py   ← 桌面快捷方式
└── 素材库/                ← 热梗素材库
```

## 启动方式

在 Claude Code 中打开 `编剧工作台/` 目录，CLAUDE.md 自动加载。

## 工作流

```
哥哥说话 → 念念判断
            ├── 简单 → 念念直接做（改对白/查进度/读剧本）
            └── 重活 → spawn DeepSeek → 念念审查 → 过/改/重写
```
