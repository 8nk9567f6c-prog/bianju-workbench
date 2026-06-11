"""
编剧工作台 v5.5 — 自动修复引擎
Usage: python auto_fix.py <episode_file.md> [--dry-run]
"""
import sys
import re
from pathlib import Path

# ── AI腔替换表 ──
AI_TONE_REPLACEMENTS = {
    "岂料": "没想到",
    "殊不知": "却不知道",
    "与此同时": "同时",
    "正所谓": "正应了那句",
    "不料": "没想到",
    "显而易见": "很明显",
    "毋庸置疑": "毫无疑问",
    "由此可见": "看来",
    "换言之": "换句话说",
    "总而言之": "总之",
    "综上所述": "以上种种",
    "顷刻间": "一瞬间",
    "蓦然": "突然",
    "倏地": "猛地",
    "须臾": "片刻",
    "便见得": "只见",
}

def auto_fix_ai_tone(text):
    """Replace AI-tone words with natural alternatives."""
    changes = []
    fixed = text
    for ai_word, replacement in AI_TONE_REPLACEMENTS.items():
        if ai_word in fixed:
            count = fixed.count(ai_word)
            fixed = fixed.replace(ai_word, replacement)
            changes.append(f"AI腔 '{ai_word}' → '{replacement}' ({count}处)")
    return fixed, changes


def auto_fix_format(text):
    """Add missing format elements where possible."""
    changes = []

    # Ensure 第x集 at top
    if not re.search(r'^第\d+集\s*$', text, re.MULTILINE):
        text = "第1集\n\n" + text
        changes.append("格式补全：添加'第x集'标记（默认第1集，请手动修正集数）")

    # Ensure --- scene separators exist
    scene_count = len(re.findall(r'^---\s*$', text, re.MULTILINE))
    if scene_count == 0 and '【' in text:
        # Add at least one separator before scene description
        text = re.sub(r'(\n)(【)', r'\1---\n\2', text, count=1)
        changes.append("格式补全：添加场景分隔符 '---'")

    # Ensure (第x集完) at end
    if not re.search(r'（第\d+集完）', text):
        text = text.rstrip() + "\n\n（第1集完）\n"
        changes.append("格式补全：添加'（第x集完）'结尾标记（默认第1集，请手动修正）")

    # Ensure 道具： section exists (add placeholder if missing)
    if '人物：' in text and '道具：' not in text:
        text = text.replace('服装：', '道具：\n- （请补充本集道具）\n\n服装：')
        changes.append("格式补全：添加空'道具：'节（请手动补充道具列表）")

    return text, changes


def auto_fix_dialogue_markers(text):
    """Ensure dialogue lines use ： (full-width colon)."""
    changes = []
    # Find lines that look like dialogue but use half-width :
    dialogue_pattern = re.compile(r'^([^\s△#\-【\d\n][^:：\n]{0,10}):([^:：\n]+)$', re.MULTILINE)
    matches = dialogue_pattern.findall(text)
    if matches:
        text = dialogue_pattern.sub(r'\1：\2', text)
        changes.append(f"对白格式修正：{len(matches)}处半角冒号→全角冒号")
    return text, changes


def auto_fix(text, dry_run=False):
    """Run all auto-fixes. Returns (fixed_text, change_log)."""
    all_changes = []

    fixed, changes = auto_fix_ai_tone(text)
    all_changes.extend(changes)

    fixed, changes = auto_fix_format(fixed)
    all_changes.extend(changes)

    fixed2, changes = auto_fix_dialogue_markers(fixed)
    all_changes.extend(changes)
    fixed = fixed2

    if dry_run:
        return text, all_changes  # Return original unchanged
    return fixed, all_changes


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python auto_fix.py <episode_file.md> [--dry-run]")
        print("  --dry-run  Preview changes without applying")
        sys.exit(1)

    filepath = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    text = Path(filepath).read_text(encoding="utf-8")
    fixed, changes = auto_fix(text, dry_run=dry_run)

    if not changes:
        print("没有发现可自动修复的问题。")
    else:
        print(f"发现 {len(changes)} 处可自动修复的问题：")
        for c in changes:
            print(f"  ✓ {c}")

        if not dry_run:
            Path(filepath).write_text(fixed, encoding="utf-8")
            print(f"\n已保存修复后的文件: {filepath}")
        else:
            print("\n[dry-run] 未实际修改文件。使用不带 --dry-run 参数运行以应用修改。")
