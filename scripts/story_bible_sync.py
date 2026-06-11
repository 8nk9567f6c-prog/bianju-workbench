#!/usr/bin/env python3
"""story_bible_sync.py — 故事圣经自动同步引擎 (v7.0)
扫描项目剧本文件，自动提取角色/道具/伏笔/金手指/世界观更新至故事圣经.md

用法: python scripts/story_bible_sync.py "作品/{项目名}"
输出: 覆盖式更新 作品/{项目名}/故事圣经.md 的追踪数据（一/二/三节保留手动填写内容，四/五节自动更新）
"""

import sys
import re
import os
from pathlib import Path
from datetime import date
from collections import Counter, defaultdict

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def scan_scripts(project_dir):
    """扫描项目剧本目录，返回所有集数的结构化数据"""
    script_dir = Path(project_dir) / "剧本"
    if not script_dir.exists():
        print(f"✗ 剧本目录不存在: {script_dir}")
        return None

    script_files = sorted(script_dir.glob("*.md"))
    if not script_files:
        print(f"✗ 剧本目录为空: {script_dir}")
        return None

    data = {
        "episodes": [],
        "characters": defaultdict(lambda: {"appearances": 0, "episodes": [], "traits": set()}),
        "props": defaultdict(lambda: {"first_ep": None, "last_ep": None, "appearances": 0}),
        "locations": defaultdict(lambda: {"first_ep": None, "last_ep": None}),
        "golden_finger_uses": [],
        "foreshadowing": [],
        "last_episode_num": 0,
    }

    for f in script_files:
        text = f.read_text(encoding="utf-8")
        fname = f.stem

        # Extract episode number from filename (e.g., "剧本-第1-10集")
        ep_match = re.search(r'第(\d+)[\-~～](\d*)集', fname)
        if not ep_match:
            ep_match = re.search(r'第(\d+)集', fname)
        if ep_match:
            ep_start = int(ep_match.group(1))
            ep_end = int(ep_match.group(2)) if ep_match.group(2) else ep_start
        else:
            ep_start = data["last_episode_num"] + 1
            ep_end = ep_start

        data["episodes"].append({"file": fname, "start": ep_start, "end": ep_end})
        data["last_episode_num"] = max(data["last_episode_num"], ep_end)

        # ── Extract characters ──
        for match in re.finditer(r'人物[：:]\s*(.+)', text):
            chars = re.split(r'[ 　、，,]+', match.group(1).strip())
            for c in chars:
                c = c.strip()
                if c and len(c) >= 2:
                    data["characters"][c]["appearances"] += 1
                    if ep_start not in data["characters"][c]["episodes"]:
                        data["characters"][c]["episodes"].append(ep_start)

        # ── Extract props ──
        in_prop_section = False
        for line in text.split('\n'):
            if re.match(r'^道具[：:]', line):
                in_prop_section = True
                props = re.sub(r'^道具[：:]', '', line).strip()
                for p in re.split(r'[、，,]', props):
                    p = p.strip().lstrip('- ').rstrip()
                    if p and len(p) >= 2:
                        if data["props"][p]["first_ep"] is None:
                            data["props"][p]["first_ep"] = ep_start
                        data["props"][p]["last_ep"] = ep_start
                        data["props"][p]["appearances"] += 1
                continue
            if in_prop_section and re.match(r'^[^\s\-]', line) and '：' not in line[:6]:
                in_prop_section = False

        # ── Extract locations from scene headers ──
        for match in re.finditer(r'\d{3}\s+[日夜晚凌清][/\s]*[内 Outdoor 外]\s+(.+)', text):
            loc = match.group(1).strip()
            if loc:
                if data["locations"][loc]["first_ep"] is None:
                    data["locations"][loc]["first_ep"] = ep_start
                data["locations"][loc]["last_ep"] = ep_start

        # ── Extract golden finger usage ──
        gf_markers = ['金手指', '系统', '能力', '技能', '透视', '读心', '预知', '空间', '储物']
        for line in text.split('\n'):
            for marker in gf_markers:
                if marker in line and ('△' in line or '使用' in line or '激活' in line or '触发' in line):
                    data["golden_finger_uses"].append({
                        "episode": ep_start,
                        "line": line.strip()[:80]
                    })
                    break

        # ── Detect potential foreshadowing ──
        foreshadow_keywords = ['突然', '奇怪', '不对劲', '意外', '想不到', '竟然', '原来',
                               '发现', '秘密', '真相', '线索', '伏笔', '暗示']
        for line in text.split('\n'):
            for kw in foreshadow_keywords:
                if kw in line and len(line.strip()) > 10:
                    data["foreshadowing"].append({
                        "episode": ep_start,
                        "keyword": kw,
                        "line": line.strip()[:100]
                    })
                    break

    return data


def update_story_bible(project_dir, data):
    """基于扫描数据更新故事圣经.md 的第四、五节"""
    bible_path = Path(project_dir) / "故事圣经.md"
    if not bible_path.exists():
        print(f"✗ 故事圣经不存在: {bible_path}")
        return False

    original = bible_path.read_text(encoding="utf-8")

    # ── Build replacement sections ──

    # 连续性追踪: 重要道具
    prop_table = "| 道具 | 首次出现集数 | 当前状态 | 最后提及集数 |\n"
    prop_table += "|------|------------|---------|------------|\n"
    for prop, info in sorted(data["props"].items(), key=lambda x: -x[1]["appearances"]):
        last_ep = info["last_ep"]
        status = "使用中" if last_ep >= data["last_episode_num"] * 0.7 else "已停用"
        prop_table += f"| {prop} | {info['first_ep']} | {status} | {last_ep} |\n"

    # 连续性追踪: 关键地点
    loc_table = "| 地点 | 首次出现 | 当前状态 |\n"
    loc_table += "|------|--------|---------|\n"
    for loc, info in sorted(data["locations"].items()):
        loc_table += f"| {loc} | 第{info['first_ep']}集 | 活跃 |\n"

    # 连续性追踪: 伏笔状态（保留原有前置伏笔 + 追加新检测到的）
    new_fs_lines = []
    seen_episodes = set()
    for fs in data["foreshadowing"][:20]:  # Top 20 potential foreshadowing
        if fs["episode"] not in seen_episodes:
            new_fs_lines.append(f"| {len(new_fs_lines)+1} | {fs['line'][:40]}... | 已埋 | 第{fs['episode']}集 | 待回收 |")
            seen_episodes.add(fs["episode"])

    # 金手指已兑现代价记录
    gf_lines = []
    for gf in data["golden_finger_uses"][:15]:
        gf_lines.append(f"- 第{gf['episode']}集：{gf['line']}")

    # ── Apply replacements ──
    today = date.today().isoformat()

    # Update header
    original = re.sub(r'> 最后更新: .+', f'> 最后更新: {today} | 更新者: story_bible_sync.py (v7.0 auto) | 版本: v2.0', original)

    # Update prop table
    original = re.sub(
        r'\|\s*道具\s*\|[^|]*\|[^|]*\|[^|]*\|\s*\n\|[-| ]+\|\s*\n((?:\|.*\|\s*\n)*)',
        prop_table,
        original
    )

    # Update location table
    original = re.sub(
        r'\|\s*地点\s*\|[^|]*\|[^|]*\|\s*\n\|[-| ]+\|\s*\n((?:\|.*\|\s*\n)*)',
        loc_table,
        original
    )

    # Update foreshadowing table — preserve existing ones and append new
    fs_section_pattern = r'(### 伏笔状态（动态）\s*\n)((?:\|.*\|\s*\n)+)'
    existing_fs_match = re.search(fs_section_pattern, original)
    if existing_fs_match:
        existing_fs = existing_fs_match.group(2).strip()
        original = re.sub(fs_section_pattern, f'\\1{existing_fs}\n{chr(10).join(new_fs_lines)}\n', original)

    # Update golden finger cost record
    if gf_lines:
        cost_section = '\n'.join(gf_lines)
        cost_pattern = r'(- 已兑现代价记录：\s*\n)((?:\s*- .*\n)*)'
        if re.search(cost_pattern, original):
            original = re.sub(cost_pattern, f'\\1{cost_section}\n', original)

    bible_path.write_text(original, encoding="utf-8")
    return True


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/story_bible_sync.py \"作品/{项目名}\"", file=sys.stderr)
        sys.exit(1)

    project_dir = sys.argv[1]
    if not os.path.isdir(project_dir):
        print(f"✗ 项目目录不存在: {project_dir}", file=sys.stderr)
        sys.exit(2)

    print(f"▸ 故事圣经自动同步 — {project_dir}")
    data = scan_scripts(project_dir)
    if data is None:
        sys.exit(2)

    print(f"  ✓ 扫描完成: {len(data['episodes'])} 个剧本文件, 第1-{data['last_episode_num']}集")
    print(f"  ✓ 角色: {len(data['characters'])} 个")
    print(f"  ✓ 道具: {len(data['props'])} 个")
    print(f"  ✓ 地点: {len(data['locations'])} 个")
    print(f"  ✓ 金手指使用: {len(data['golden_finger_uses'])} 次")
    print(f"  ✓ 潜在伏笔: {len(data['foreshadowing'])} 处")

    success = update_story_bible(project_dir, data)
    if success:
        bible_path = Path(project_dir) / "故事圣经.md"
        print(f"  ✓ 故事圣经已更新: {bible_path}")
    else:
        print(f"  ✗ 故事圣经更新失败")
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
