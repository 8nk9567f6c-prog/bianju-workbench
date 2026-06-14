#!/usr/bin/env python3
"""validate_handoff.py — 验证 Agent 间交接协议字段完整性（吸收 claude-code-toolkit verifier gate 模式）

用法:
  python validate_handoff.py --from agent1 --to agent2 --file "调研报告-选题分析.md"
  python validate_handoff.py --from agent2 --to agent3 --anchor "ANCHOR.md" --outline "大纲-第1-10集.md"
  python validate_handoff.py --list-contracts  # 列出所有交接协议

交接协议定义:
  Agent 1 → Agent 2: 8 必须字段（调研报告）
  Agent 2 → Agent 3: 10 必须字段（ANCHOR.md + 大纲文件）
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ── 交接协议定义 ─────────────────────────────────────────

HANDOFF_CONTRACTS = {
    "agent1_to_agent2": {
        "name": "Agent 1 → Agent 2 交接协议",
        "source_agent": 1,
        "target_agent": 2,
        "source_file": "调研报告-选题分析.md",
        "required_fields": [
            {"id": "track", "name": "选定赛道+子赛道", "chapter": "第 1 章", "check": lambda content: _check_section_exists(content, "市场格局")},
            {"id": "competitors", "name": "≥3 部竞品 8 基因对标（含来源 URL）", "chapter": "第 2 章", "check": lambda content: _check_competitor_count(content) >= 3},
            {"id": "gene_map", "name": "赛道基因图谱（共性摘要 ≥ 5 条）", "chapter": "第 3 章", "check": lambda content: _check_list_items(content, "共性", 5)},
            {"id": "blue_ocean", "name": "蓝海缺口（≥ 2 个具体缺口，附竞品证据）", "chapter": "第 3 章", "check": lambda content: _check_list_items(content, "缺口", 2)},
            {"id": "premise", "name": "选定选题一句话核心前提", "chapter": "第 5 章", "check": lambda content: _check_section_exists(content, "选题提案")},
            {"id": "s_plus_score", "name": "选定选题 S+ 10 维评分（≥ 85）", "chapter": "第 5 章", "check": lambda content: _check_s_plus_score(content, 85)},
            {"id": "creative_brief", "name": "创作简报（类型/基调/目标情绪/必须要素/规避要素）", "chapter": "第 6 章", "check": lambda content: _check_section_exists(content, "创作简报")},
            {"id": "reference_works", "name": "对标参考作品（≥ 1 部，含风格指纹摘要）", "chapter": "第 6 章", "check": lambda content: _check_section_exists(content, "对标参考") or _check_list_items(content, "对标", 1)},
        ]
    },
    "agent2_to_agent3": {
        "name": "Agent 2 → Agent 3 交接协议",
        "source_agent": 2,
        "target_agent": 3,
        "source_files": ["ANCHOR.md", "大纲/大纲-第*-*.md"],
        "required_fields": [
            {"id": "north_star", "name": "北极星（200 字）", "file": "ANCHOR.md", "check": lambda anchor, _outline: _check_anchor_section(anchor, "一")},
            {"id": "characters", "name": "人物速查表（≤ 6 人，含完整信息）", "file": "ANCHOR.md", "check": lambda anchor, _outline: _check_anchor_section(anchor, "二")},
            {"id": "unit_roadmap", "name": "10 单元路线图（每单元：目标+闭环钩子）", "file": "ANCHOR.md", "check": lambda anchor, _outline: _check_anchor_section(anchor, "三")},
            {"id": "paywall", "name": "付费卡点表", "file": "ANCHOR.md", "check": lambda anchor, _outline: _check_anchor_section(anchor, "四")},
            {"id": "foreshadowing", "name": "伏笔总账（≥ 6 条，含状态追踪）", "file": "ANCHOR.md", "check": lambda anchor, _outline: _check_foreshadowing_count(anchor) >= 6},
            {"id": "relationships", "name": "人物关系图谱+信息不对称表", "file": "ANCHOR.md", "check": lambda anchor, _outline: _check_anchor_section(anchor, "六")},
            {"id": "writing_anchor", "name": "当前写作锚点", "file": "ANCHOR.md", "check": lambda anchor, _outline: _check_anchor_section(anchor, "七")},
            {"id": "emotion_tracking", "name": "情绪追踪表", "file": "ANCHOR.md", "check": lambda anchor, _outline: _check_anchor_section(anchor, "八")},
            {"id": "outline_segment", "name": "当前段大纲文件（每集 2-3 句梗概+标注）", "file": "大纲文件", "check": lambda anchor, outline: _check_outline_has_episodes(outline)},
            {"id": "self_review_pass", "name": "ANCHOR 八节自审全部 ✓ 标记", "file": "自审报告", "check": lambda anchor, _outline: _check_self_review_pass(anchor)},
        ]
    }
}


# ── 检查辅助函数 ─────────────────────────────────────────

def _read_file(filepath):
    """Read a file, return content or None."""
    path = Path(filepath)
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def _check_section_exists(content, keyword):
    """Check if a section/chapter exists in the content."""
    if content is None:
        return False
    return keyword in content


def _check_anchor_section(anchor_path, section_num):
    """Check if an ANCHOR.md section exists and has content."""
    content = _read_file(anchor_path)
    if content is None:
        return False
    markers = {
        "一": ["## 一", "# 一", "第一节", "北极星"],
        "二": ["## 二", "# 二", "第二节", "人物"],
        "三": ["## 三", "# 三", "第三节", "单元"],
        "四": ["## 四", "# 四", "第四节", "付费", "卡点"],
        "五": ["## 五", "# 五", "第五节", "伏笔"],
        "六": ["## 六", "# 六", "第六节", "人物关系"],
        "七": ["## 七", "# 七", "第七节", "写作锚点", "当前锚点"],
        "八": ["## 八", "# 八", "第八节", "情绪追踪"],
    }
    if section_num not in markers:
        return False
    for marker in markers[section_num]:
        if marker in content:
            # Check there's actual content after the section header
            idx = content.find(marker)
            section_content = content[idx + len(marker):]
            next_section = None
            for m in ["\n## ", "\n# "]:
                pos = section_content.find(m)
                if pos > 0 and (next_section is None or pos < next_section):
                    next_section = pos
            if next_section:
                section_content = section_content[:next_section]
            # At least 50 chars of real content (not just header)
            return len(section_content.strip()) >= 50
    return False


def _check_competitor_count(content):
    """Count competitor analyses in research report."""
    if content is None:
        return 0
    count = 0
    markers = ["竞品", "对标作品", "## 2.", "第2章", "基因 1:"]
    for marker in markers:
        count += content.count(marker)
    # Each competitor has 8 genes, so divide gene counts by 8
    gene_count = content.count("基因 ") + content.count("基因1") + content.count("基因2") + content.count("基因3") + content.count("基因4") + content.count("基因5") + content.count("基因6") + content.count("基因7") + content.count("基因8")
    estimated = max(count // 2, gene_count // 8)
    return min(estimated, 10)


def _check_list_items(content, keyword, min_count):
    """Check if a list with given keyword has at least min_count items."""
    if content is None:
        return False
    count = 0
    for line in content.split("\n"):
        if keyword in line and (line.strip().startswith("- ") or line.strip().startswith("* ") or line.strip()[0].isdigit()):
            count += 1
    return count >= min_count


def _check_s_plus_score(content, min_score):
    """Check if S+ score meets threshold."""
    if content is None:
        return False
    import re
    scores = re.findall(r'S\+\s*[:：]?\s*(\d+)\s*/\s*100', content)
    for s in scores:
        if int(s) >= min_score:
            return True
    scores_2 = re.findall(r'(\d+)\s*/\s*100', content)
    for s in scores_2:
        if int(s) >= min_score:
            return True
    return False


def _check_foreshadowing_count(anchor_path):
    """Count foreshadowing entries in ANCHOR.md."""
    content = _read_file(anchor_path)
    if content is None:
        return 0
    count = 0
    in_section_5 = False
    for line in content.split("\n"):
        if any(m in line for m in ["## 五", "# 五", "第五节", "伏笔"]):
            in_section_5 = True
            continue
        if in_section_5 and line.startswith("## "):
            break
        if in_section_5 and line.strip().startswith("- ") and len(line.strip()) > 5:
            count += 1
    return count


def _check_self_review_pass(anchor_path):
    """验证 ANCHOR.md 八节全部存在且有内容——Agent 2 自审完成的前置条件。"""
    sections = ["一", "二", "三", "四", "五", "六", "七", "八"]
    passed = 0
    for num in sections:
        if _check_anchor_section(anchor_path, num):
            passed += 1
    return passed == 8


def _check_outline_has_episodes(outline_path):
    """Check that the outline file contains per-episode entries."""
    if outline_path is None:
        return False
    content = _read_file(outline_path)
    if content is None:
        return False
    import re
    episodes = re.findall(r'第\s*(\d+)\s*集', content)
    return len(set(episodes)) >= 3  # at least 3 unique episodes mentioned


# ── 主验证逻辑 ─────────────────────────────────────────

def validate_handoff(from_agent, to_agent, report_file=None, anchor_file=None, outline_file=None):
    """Validate handoff between two agents."""
    contract_key = f"agent{from_agent}_to_agent{to_agent}"
    if contract_key not in HANDOFF_CONTRACTS:
        return {"status": "error", "reason": f"未定义交接协议: Agent {from_agent} → Agent {to_agent}"}

    contract = HANDOFF_CONTRACTS[contract_key]
    results = []
    passed = 0
    failed = 0

    if from_agent == 1 and to_agent == 2:
        content = _read_file(report_file) if report_file else None
        if content is None:
            return {"status": "error", "reason": f"调研报告不可读: {report_file}"}

        for field in contract["required_fields"]:
            ok = field["check"](content)
            if ok:
                passed += 1
                results.append({"field": field["name"], "status": "pass"})
            else:
                failed += 1
                results.append({"field": field["name"], "status": "fail", "chapter": field["chapter"]})

    elif from_agent == 2 and to_agent == 3:
        anchor_content = _read_file(anchor_file) if anchor_file else None
        outline_content = _read_file(outline_file) if outline_file else None

        if anchor_content is None:
            return {"status": "error", "reason": f"ANCHOR.md 不可读: {anchor_file}"}

        for field in contract["required_fields"]:
            ok = field["check"](anchor_file, outline_file)
            if ok:
                passed += 1
                results.append({"field": field["name"], "status": "pass"})
            else:
                failed += 1
                results.append({"field": field["name"], "status": "fail", "file": field.get("file", "?")})

    total = passed + failed
    return {
        "status": "pass" if failed == 0 else "fail",
        "contract": contract["name"],
        "passed": passed,
        "failed": failed,
        "total": total,
        "results": results
    }


def main():
    parser = argparse.ArgumentParser(description="验证 Agent 间交接协议字段完整性")
    parser.add_argument("--from", dest="from_agent", type=int, choices=[1, 2],
                        help="上游 Agent 编号")
    parser.add_argument("--to", dest="to_agent", type=int, choices=[2, 3],
                        help="下游 Agent 编号")
    parser.add_argument("--file", "-f", help="调研报告文件路径（Agent 1→2 时使用）")
    parser.add_argument("--anchor", "-a", help="ANCHOR.md 文件路径（Agent 2→3 时使用）")
    parser.add_argument("--outline", "-o", help="大纲文件路径（Agent 2→3 时使用）")
    parser.add_argument("--list-contracts", action="store_true", help="列出所有交接协议")

    args = parser.parse_args()

    if not args.list_contracts and (args.from_agent is None or args.to_agent is None):
        parser.error("--from and --to are required (unless --list-contracts)")

    if args.list_contracts:
        for key, contract in HANDOFF_CONTRACTS.items():
            print(f"▸ {contract['name']}")
            print(f"  必须字段: {len(contract['required_fields'])} 项")
            for f in contract['required_fields']:
                print(f"    - {f['name']}")
        return

    result = validate_handoff(
        from_agent=getattr(args, 'from_agent'),
        to_agent=getattr(args, 'to_agent'),
        report_file=args.file,
        anchor_file=args.anchor,
        outline_file=args.outline
    )

    if result["status"] == "error":
        print(f"✗ {result['reason']}")
        sys.exit(1)

    print(f"▸ {result['contract']}")
    print(f"  通过: {result['passed']}/{result['total']}  失败: {result['failed']}/{result['total']}")
    print()

    for r in result["results"]:
        mark = "✓" if r["status"] == "pass" else "✗"
        extra = r.get("chapter", "") or r.get("file", "")
        print(f"  {mark} {r['field']}  [{extra}]")

    if result["failed"] > 0:
        print(f"\n⚠ 缺失 {result['failed']} 项——下游 Agent 应拒绝启动，直到上游补全。")
        sys.exit(1)
    else:
        print(f"\n✓ 交接协议完整——下游 Agent 可以启动。")


if __name__ == "__main__":
    main()
