---
name: v8-refactoring
description: v8.0 主编+写手分工重构——2026.6.22 完成
metadata:
  type: project
---

# 编剧工作台 v8.0 重构

**日期**: 2026-06-22
**触发**: 哥哥反馈「编剧工作台一点不好用」——太慢、质量差、流程复杂、不听话

## 核心理念变更

- v7.x: Agent 自写自审自评分 → 既当考生又当考官 → 评分虚高
- v8.0: 念念=主编(审查+提示词工程) / DeepSeek Agent=写手(调研/大纲/剧本) → 独立质检

## 关键改动

1. 规则从~150条砍到~25条核心
2. 三层规则冗余合并为一层(spawn prompt)
3. 全部负向禁令转为正向指令
4. 用户指令放在prompt最前面
5. 取消路由确认环节
6. 念念可直接处理简单任务
7. 砍掉PostToolUse自动sync钩子
8. 归档6个过时references文件

## 文件状态

- CLAUDE.md: v8.0 主编职责+审查清单
- CORE_CREATIVE_DNA.md: 三层分级(⛔⚡💡)
- agent_dispatcher.md: 新spawn模板+念念审查流程
- agent_content_expansion.md: 从391行砍到~130行
- agent_outline_construction.md: 精简
- agent_topic_research.md: 精简
- .claude/settings.json: 删PostToolUse Hook
- agents/references/: 从8个文件减到2个

## 正循环

DeepSeek写 → 念念审(6维清单) → ✅过/⚠改/❌重写 → 念念写精准修改提示词 → DeepSeek改 → 念念再过
