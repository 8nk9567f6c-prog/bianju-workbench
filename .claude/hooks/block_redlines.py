#!/usr/bin/env python3
"""block_redlines.py — PreToolUse Hook：剧本写入前红线硬拦截

用法（在 .claude/settings.json 的 PreToolUse hook 中配置）：
  匹配 Write|Edit 工具 → 运行此脚本
  如果检测到红线违规 → exit(2) 阻止写入
  通过 → exit(0) 允许继续

检查维度：
  1. AI标记词超限（每600字>1个）
  2. 平台红线关键词
  3. 写作红线关键词（心理描写/抽象情绪等）
  4. 剧本格式基本校验
"""

import json
import sys
import os
import re
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────

# 统一 AI 标记词（与 validators.py / auto_fix.py / check_text_variety.py 保持一致）
# 两类：情绪填充词 + 正式连接词（AI腔）
AI_MARKERS = [
    # 情绪/转折填充词（AI 偷懒高频词）
    "仿佛", "忽然", "竟然", "不禁", "宛如", "猛地", "难以置信", "无形中",
    "然而", "因此", "于是", "随后", "与此同时", "就这样", "不仅如此",
    # 正式/书面连接词（AI腔——validators.py check_ai_tone 同步）
    "岂料", "殊不知", "正所谓", "不料", "显而易见", "毋庸置疑",
    "由此可见", "换言之", "总而言之", "综上所述", "顷刻间",
    "蓦然", "倏地", "须臾", "便见得",
]

PLATFORM_REDLINE_KEYWORDS = [
    "中国政府", "共产党", "国家主席", "台湾独立", "西藏独立",
    "色情", "裸体", "性交", "性器官",
    "血腥虐杀", "肢解", "酷刑", "分尸",
    "毒品制作", "制毒方法", "吸毒教学",
    "未成年人恋爱", "未成年性行为",
]

WRITING_REDLINE_PATTERNS = [
    (r"他心想", "心理描写：'他心想'"),
    (r"他感到", "心理描写：'他感到'（排除可拍动作）"),
    (r"他意识到", "心理描写：'他意识到'"),
    (r"愤怒涌上心头", "抽象情绪：'愤怒涌上心头'"),
    (r"悲伤弥漫", "抽象情绪：'悲伤弥漫'"),
    (r"你忘了吗.*家族", "台词解说设定"),
    (r"人生啊", "说教催泪"),
    (r"你一定要坚强", "说教催泪"),
    (r"金碧辉煌的大厅", "形容词堆砌"),
    (r"豪华气派", "形容词堆砌"),
]


def is_script_file(file_path):
    """判断是否为剧本文件"""
    if not file_path:
        return False
    name = Path(file_path).name
    return name.startswith("剧本-第") and name.endswith(".md")


def count_chars(text):
    """计算中文字符数（排除标点和空白）"""
    return len(re.sub(r'[\s\d\W]', '', text))


def check_ai_markers(content, file_path):
    """检查AI标记词是否超限"""
    char_count = max(count_chars(content), 1)
    total_markers = 0
    violations = []
    for marker in AI_MARKERS:
        count = content.count(marker)
        if count > 0:
            total_markers += count
            violations.append(f"  - '{marker}' ×{count}")

    threshold = max(1, char_count // 600)
    if total_markers > threshold:
        msg = f"⛔ AI标记词超限：{total_markers}个（阈值{threshold}）在 {char_count}字中"
        detail = "\n".join(violations[:20])
        return False, f"{msg}\n{detail}"
    return True, ""


def check_platform_redlines(content, file_path):
    """检查平台红线关键词"""
    for kw in PLATFORM_REDLINE_KEYWORDS:
        if kw in content:
            return False, f"⛔ 平台红线：检测到禁止关键词 '{kw}'"
    return True, ""


def check_writing_redlines(content, file_path):
    """检查写作红线"""
    for pattern, desc in WRITING_REDLINE_PATTERNS:
        if re.search(pattern, content):
            return False, f"⛔ 写作红线：{desc}"
    return True, ""


def check_format_basics(content, file_path):
    """检查剧本格式基本要求"""
    # 只对剧本文件做格式检查
    if not is_script_file(file_path):
        return True, ""

    issues = []

    # 必须有第x集标识
    if not re.search(r'第\d+集', content):
        issues.append("缺少'第x集'标识")

    # 必须有分场分隔符
    if '---' not in content:
        issues.append("缺少分场分隔符'---'")

    # 检查是否超过650字限制
    char_count = count_chars(content)
    if char_count > 650:
        issues.append(f"单集字数{char_count}>650上限")

    if issues:
        return False, "⛔ 格式问题：" + " | ".join(issues)
    return True, ""


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        # 非 JSON 输入（如手动触发），静默通过
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "") or tool_input.get("new_string", "")

    # 如果不是写入文件的操作，跳过
    if not file_path:
        sys.exit(0)

    # 只对剧本文件做严格检查，其他文件只做平台红线
    is_script = is_script_file(file_path)

    checks = [
        ("平台红线", check_platform_redlines),
    ]

    if is_script or content:
        # 对于有内容的写入，做更完整检查
        checks.append(("AI标记词", check_ai_markers))
        if is_script:
            checks.append(("写作红线", check_writing_redlines))
            checks.append(("格式基础", check_format_basics))

    for check_name, check_fn in checks:
        passed, msg = check_fn(content, file_path)
        if not passed:
            print(f"\n{'='*60}")
            print(f"🛑 编剧工作台 · 红线拦截")
            print(f"   文件: {file_path}")
            print(f"   检查: {check_name}")
            print(f"{'='*60}")
            print(msg)
            print(f"{'='*60}")
            print("💡 修复以上问题后重新写入。")
            sys.exit(2)  # exit code 2 = 阻止工具执行

    # 通过：静默退出
    sys.exit(0)


if __name__ == "__main__":
    main()
