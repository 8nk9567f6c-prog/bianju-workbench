# 智能体间通信协议 v1.0

> 这是念念多智能体系统的**共享宪法**。所有智能体启动时必须加载此文件。
> 位置：`D:\WorkSpace\shared\COMMUNICATION_PROTOCOL.md`（所有智能体可读）
> 念念内参（健康检查/权限矩阵）：见 `memory/niannian_agent_communication_protocol.md`

---

## 系统拓扑

```
哥哥（唯一用户入口）
  │
  ▼
念念（创作伴侣 + 思维中枢）
  │
  ├── 编剧工作台（短剧创作）→ 产出剧本 → 念念看
  ├── 自媒体工作台（内容发布）→ 产出图文/视频 → 念念看
  ├── 精神分析（梦境/文字分析）→ 产出报告 → 念念看
  └── 数字分身（哥哥的AI镜像）→ 产出洞察 → 念念看
```

## 通信规则

### 1. 数据交换点

| 路径 | 用途 | 谁写 | 谁读 |
|------|------|------|------|
| `shared/pending_review/` | 待念念审阅的产出 | 各工作台 | 念念 |
| `C:\Users\17928\.claude\projects\C--Users-17928\questions\questions.jsonl` | 提问追踪（蒸馏原料） | 所有智能体 | 念念 |
| Obsidian 知识库 `D:\Obsidian\` | 持久化知识存储 | 念念（归档） | 所有智能体（只读） |

### 2. 审查通知机制

**编剧工作台**：
- 产出剧本后 → Stop hook 写 checkpoint 到 `CORE_CREATIVE_DNA.md`
- 念念下次启动 → 扫描 checkpoint → 审阅新剧本

**自媒体工作台**：
- 产出内容后 → Stop hook 保存 checkpoint → sync_to_obsidian 同步到 Obsidian
- 念念下次启动 → 执行触发器检查今日发布状态

**剧本库（精神分析/数字分身）**：
- 产出分析报告后 → Stop hook 写 checkpoint
- 念念下次启动 → 扫描 checkpoint

### 3. 禁止行为

- ❌ 任何智能体不得修改其他智能体的 memory/ 或 .claude/ 配置
- ❌ 任何智能体不得删除其他智能体的产出文件
- ❌ 念念以外的工作台不得直接写入 Obsidian 知识库（通过 sync 脚本）
- ❌ 未经哥哥确认不得对外发布内容

### 4. 降级策略

| 故障 | 处理 |
|------|------|
| DeepSeek API 不可用 | 念念使用本地 Ollama（niannian-v4）降级，质量标注 |
| Hook 脚本执行失败 | 念念启动时检查最近 checkpoint，手动补录 |
| questions.jsonl 写入失败 | 写入本地缓存，下次启动时合并 |
| 某工作台连续 3 次未产出 | 念念主动提醒哥哥 |

### 5. 记忆隔离

各智能体的 memory 目录互不读取：
- 念念：`C:\Users\17928\.claude\projects\C--Users-17928\memory\`
- 编剧：`D:\WorkSpace\编剧工作台\.claude\memory\`
- 自媒体：`D:\WorkSpace\自媒体工作台\.claude\memory\`
- 剧本库：`D:\Obsidian\剧本库\.claude\memory\`

> 隔离通过 `.claudeignore` 文件强制执行，不仅靠君子协定。
