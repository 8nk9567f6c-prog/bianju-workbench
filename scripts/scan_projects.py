#!/usr/bin/env python3
"""scan_projects.py — 扫描作品/目录，输出结构化项目数据 + 仪表盘

用法:
  python scan_projects.py [--workspace 作品目录路径] [--json] [--project 项目名] [--dashboard]

输出 JSON:
  {
    "projects": [
      {
        "name": "项目名",
        "path": "作品/项目名",
        "has_anchor": true/false,
        "has_research_report": true/false,
        "has_story_bible": true/false,
        "scripts_count": 3,
        "outline_files": ["大纲-第1-10集.md", ...],
        "last_modified": "ISO timestamp",
        "characters": ["角色A", "角色B"],  // from ANCHOR.md if exists
        "keywords": ["战神", "复仇", ...]   // from ANCHOR.md 北极星
      }
    ],
    "total_projects": N,
    "active_projects": N  // has >= 1 script file
  }
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


def is_abandoned(project_path):
    """Check if project has been explicitly abandoned by the user."""
    return (project_path / ".abandoned").exists()


def find_scripts(project_path):
    """Find script files in various locations within a project.

    Only counts files matching 剧本-第N集.md pattern (excludes 速查表, temp files, etc.)
    """
    scripts = []
    # Match: 剧本-第1集.md, 剧本/剧本-第10集.md, etc.
    patterns = ["剧本-第*集.md", "剧本/剧本-第*集.md"]
    for pattern in patterns:
        for f in project_path.glob(pattern):
            if f.is_file():
                scripts.append(f.name)
    return sorted(set(scripts))


def count_docx_episodes(project_path):
    """Count episodes from .docx source files in the project directory.

    Returns the max episode count found across all docx files.
    """
    import re
    max_eps = 0
    for docx_file in project_path.glob("*.docx"):
        try:
            import zipfile
            from xml.etree import ElementTree as ET
            with zipfile.ZipFile(docx_file) as z:
                xml_content = z.read('word/document.xml').decode('utf-8')
                tree = ET.fromstring(xml_content)
                paragraphs = []
                for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                    texts = []
                    for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                        if t.text:
                            texts.append(t.text)
                    line = ''.join(texts).strip()
                    if line:
                        paragraphs.append(line)
                full_text = '\n'.join(paragraphs)
                # Match Chinese numerals: 第一集, 第十集, 第十五集
                cn_nums = re.findall(r'第([一二三四五六七八九十百]+)集', full_text)
                # Match Arabic numerals: 第1集, 第15集
                ar_nums = re.findall(r'第(\d+)集', full_text)
                episode_nums = set()
                for n in cn_nums:
                    num = _cn_num_to_int(n)
                    if num and num <= 200:
                        episode_nums.add(num)
                for n in ar_nums:
                    n = int(n)
                    if n <= 200:
                        episode_nums.add(n)
                if episode_nums:
                    max_eps = max(max_eps, max(episode_nums))
        except Exception:
            pass
    return max_eps


def _cn_num_to_int(cn):
    """Convert Chinese numeral string to integer. E.g., '十五' -> 15, '一百' -> 100."""
    map_cn = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
              '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '百': 100}
    if not cn:
        return None
    total = 0
    section = 0
    for ch in cn:
        if ch == '百':
            total += (section or 1) * 100
            section = 0
        elif ch == '十':
            total += (section or 1) * 10
            section = 0
        else:
            section = map_cn.get(ch, 0)
    total += section
    return total if total > 0 else None


def find_outlines(project_path):
    """Find outline files."""
    outlines = []
    outline_dir = project_path / "大纲"
    if outline_dir.is_dir():
        for f in outline_dir.glob("*.md"):
            outlines.append(f"大纲/{f.name}")
    for f in project_path.glob("大纲-*.md"):
        outlines.append(f.name)
    return sorted(outlines)


def extract_characters_from_anchor(anchor_path):
    """Extract character names from ANCHOR.md section 2."""
    try:
        content = anchor_path.read_text(encoding="utf-8")
        characters = []
        in_section_2 = False
        for line in content.split("\n"):
            if "## 二" in line or "## 2" in line or "第二节" in line or "人物" in line:
                in_section_2 = True
                continue
            if in_section_2 and line.startswith("## "):
                break
            if in_section_2 and line.strip().startswith("- "):
                name = line.strip()[2:].split("：")[0].split(":")[0].strip()
                if name and len(name) <= 10:
                    characters.append(name)
        return characters[:6]  # max 6 characters
    except Exception:
        return []


def extract_keywords_from_anchor(anchor_path):
    """Extract keywords from ANCHOR.md 北极星."""
    try:
        content = anchor_path.read_text(encoding="utf-8")
        keywords = set()
        track_keywords = ["战神", "高手下山", "出狱", "巨富归来", "修仙归来", "算命天师",
                          "重生复仇", "契约婚姻", "真假千金", "穿书觉醒", "离婚", "赘婿",
                          "神医", "鉴宝", "盗墓", "末世", "系统", "穿越", "古代", "现代"]
        for kw in track_keywords:
            if kw in content:
                keywords.add(kw)
        return sorted(keywords)
    except Exception:
        return []


def get_last_modified(project_path):
    """Get the most recent modification time of any file in the project."""
    try:
        max_time = 0
        for f in project_path.rglob("*"):
            if f.is_file():
                mtime = f.stat().st_mtime
                if mtime > max_time:
                    max_time = mtime
        return datetime.fromtimestamp(max_time).isoformat() if max_time > 0 else None
    except Exception:
        return None


def get_checkpoint_info(project_path):
    """Extract checkpoint info from .checkpoint_script.json or .checkpoint_outline.json."""
    info = {}
    for cp_name in [".checkpoint_script.json", ".checkpoint_outline.json"]:
        cp = project_path / cp_name
        if cp.exists():
            try:
                data = json.loads(cp.read_text(encoding="utf-8"))
                info["checkpoint_type"] = data.get("agent", cp_name)
                info["phase"] = data.get("phase", data.get("current_phase", "?"))
                info["episodes"] = data.get("total_episodes_written", data.get("episode_range", "?"))
                info["last_updated"] = data.get("last_updated", "")
                # Foreshadowing
                if "foreshadowing_count" in data:
                    fc = data["foreshadowing_count"]
                    info["foreshadowing"] = f"埋{fc.get('埋设',fc.get('total',0))}/收{fc.get('已回收',0)}"
                elif "truth_files" in data:
                    tf = data["truth_files"]
                    info["foreshadowing"] = f"开{tf.get('hooks_open',0)}收{tf.get('hooks_resolved',0)}"
                break
            except Exception:
                pass
    return info


def get_speed_table_status(project_path):
    """Check if 剧本速查表 exists and return row count."""
    speed = project_path / "剧本" / "剧本速查表.md"
    if not speed.exists():
        speed = project_path / "剧本速查表.md"
    if speed.exists():
        try:
            content = speed.read_text(encoding="utf-8")
            rows = len([l for l in content.split("\n") if l.strip().startswith("|") and not l.strip().startswith("|---")])
            return {"exists": True, "rows": max(0, rows - 1)}  # minus header
        except Exception:
            return {"exists": True, "rows": 0}
    return {"exists": False, "rows": 0}


def get_days_since(timestamp_str):
    """Calculate days since a timestamp."""
    if not timestamp_str:
        return None
    try:
        ts = datetime.fromisoformat(timestamp_str)
        return (datetime.now() - ts).days
    except Exception:
        return None


def print_dashboard(projects):
    """Print a human-readable project dashboard."""
    now = datetime.now()
    print("▸ ═══════════════════════════════════════════════════════")
    print("▸ 编剧工作台 — 项目仪表盘")
    print(f"▸ 更新时间: {now.strftime('%Y-%m-%d %H:%M')}")
    print("▸ ═══════════════════════════════════════════════════════")
    print()

    abandoned_list = []
    active_list = []
    stale_list = []
    dead_list = []

    for proj in projects:
        if proj.get("abandoned"):
            abandoned_list.append(proj)
            continue
        scripts = proj["scripts_count"]
        has_anchor = proj["has_anchor"]
        days = get_days_since(proj["last_modified"])

        if scripts == 0 and not has_anchor:
            dead_list.append(proj)
        elif days is not None and days > 14:
            stale_list.append(proj)
        else:
            active_list.append(proj)

    # Active projects
    if active_list:
        print("🟢 活跃项目")
        print(f"{'项目':<16} {'进度':<10} {'速查表':<8} {'检查点':<14} {'S+/状态':<12} {'最后改动':<12}")
        print("-" * 75)
        for proj in active_list:
            _print_dashboard_row(proj)

    # Stale projects
    if stale_list:
        print()
        print("🟡 停滞项目（>14天未改动）")
        for proj in stale_list:
            days = get_days_since(proj["last_modified"])
            print(f"  {proj['name']:<14}  {proj['scripts_count']}集剧本  {days}天前")

    # Abandoned projects
    if abandoned_list:
        print()
        print("🚫 已放弃项目")
        for proj in abandoned_list:
            effective = proj.get("effective_episodes", proj["scripts_count"])
            print(f"  {proj['name']:<14}  {effective}集剧本  (主动放弃)")

    # Dead projects
    if dead_list:
        print()
        print("⚫ 死项目（无剧本无锚点）")
        for proj in dead_list:
            print(f"  {proj['name']}")

    print()
    total_scripts = sum(p.get("effective_episodes", p["scripts_count"]) for p in projects)
    active_count = len(active_list)
    abandon_count = len(abandoned_list)
    summary_parts = [f"{len(projects)}项目", f"{active_count}活跃", f"{total_scripts}集剧本"]
    if abandon_count > 0:
        summary_parts.append(f"{abandon_count}已放弃")
    summary_parts.append(f"{len(stale_list)}停滞")
    summary_parts.append(f"{len(dead_list)}死项目")
    print(f"▸ 总计: {' | '.join(summary_parts)}")
    print()


def _print_dashboard_row(proj):
    """Print a single project row for the dashboard."""
    name = proj["name"]
    effective = proj.get("effective_episodes", proj["scripts_count"])
    docx_eps = proj.get("docx_episodes", 0)
    scripts = proj["scripts_count"]
    progress = f"{effective}/100" if effective > 0 else "未开始"

    # Speed table
    st = get_speed_table_status(Path(proj["path"]))
    speed_str = f"{st['rows']}行" if st["exists"] else "—"

    # Checkpoint
    cp = get_checkpoint_info(Path(proj["path"]))
    if cp:
        cp_str = f"{cp.get('phase','?')}"
    else:
        cp_str = "—"

    # Status / S+
    if scripts >= 100:
        status = "完本"
    elif scripts > 0:
        status = "创作中"
    elif proj["has_anchor"]:
        status = "大纲阶段"
    elif proj["has_research_report"]:
        status = "调研完成"
    else:
        status = "待启动"

    # Last modified
    days = get_days_since(proj["last_modified"])
    modified_str = f"{days}天前" if days is not None and days >= 0 else "今天" if days == 0 else "—"

    print(f"{name:<16} {progress:<10} {speed_str:<8} {cp_str:<14} {status:<12} {modified_str:<12}")


def scan_projects(workspace_path):
    """Scan all projects in the workspace."""
    workspace = Path(workspace_path)
    if not workspace.is_dir():
        return {"error": f"作品目录不存在: {workspace_path}", "projects": [], "total_projects": 0, "active_projects": 0}

    projects = []
    active_count = 0

    for project_dir in sorted(workspace.iterdir()):
        if not project_dir.is_dir():
            continue
        if project_dir.name.startswith("_"):
            continue

        anchor = project_dir / "ANCHOR.md"
        research = project_dir / "调研报告-选题分析.md"
        bible = project_dir / "故事圣经.md"
        scripts = find_scripts(project_dir)
        outlines = find_outlines(project_dir)
        last_mod = get_last_modified(project_dir)
        docx_eps = count_docx_episodes(project_dir)
        # Progress = max of script files and docx source episodes
        effective_eps = max(len(scripts), docx_eps)

        project_data = {
            "name": project_dir.name,
            "path": str(project_dir),
            "has_anchor": anchor.exists(),
            "has_research_report": research.exists(),
            "has_story_bible": bible.exists(),
            "scripts_count": len(scripts),
            "docx_episodes": docx_eps,
            "effective_episodes": effective_eps,
            "outline_files": outlines,
            "last_modified": last_mod,
            "characters": extract_characters_from_anchor(anchor) if anchor.exists() else [],
            "keywords": extract_keywords_from_anchor(anchor) if anchor.exists() else [],
            "abandoned": is_abandoned(project_dir)
        }
        projects.append(project_data)
        if effective_eps > 0:
            active_count += 1

    return {
        "projects": projects,
        "total_projects": len(projects),
        "active_projects": active_count
    }


def main():
    parser = argparse.ArgumentParser(description="扫描编剧工作台项目目录，输出结构化数据")
    parser.add_argument("--workspace", "-w", default="D:/WorkSpace/编剧工作台/作品",
                        help="作品目录路径（默认 D:/WorkSpace/编剧工作台/作品）")
    parser.add_argument("--json", "-j", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--project", "-p", help="只查询指定项目")
    parser.add_argument("--dashboard", "-d", action="store_true", help="输出项目仪表盘")
    args = parser.parse_args()

    result = scan_projects(args.workspace)

    if "error" in result:
        print(f"✗ {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.project:
        for proj in result["projects"]:
            if proj["name"] == args.project:
                if args.json:
                    print(json.dumps(proj, ensure_ascii=False, indent=2))
                else:
                    _print_project(proj)
                return
        print(f"✗ 项目不存在: {args.project}", file=sys.stderr)
        sys.exit(1)

    if args.dashboard:
        print_dashboard(result["projects"])
        return

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"▸ 项目扫描完成: {result['total_projects']} 项目 ({result['active_projects']} 活跃)")
        for proj in result["projects"]:
            anchor_mark = "锚点[✓]" if proj["has_anchor"] else "锚点[✗]"
            script_mark = f"剧本[{proj['scripts_count']}集]" if proj['scripts_count'] > 0 else "剧本[无]"
            chars = f"角色[{','.join(proj['characters'][:3])}]" if proj['characters'] else ""
            kw = f"赛道[{','.join(proj['keywords'][:3])}]" if proj['keywords'] else ""
            meta = " ".join(filter(None, [anchor_mark, script_mark, chars, kw]))
            print(f"  {proj['name']}  {meta}")


def _print_project(proj):
    effective = proj.get("effective_episodes", proj["scripts_count"])
    print(f"▸ {proj['name']}")
    print(f"  锚点: {'✓' if proj['has_anchor'] else '✗'}")
    print(f"  调研报告: {'✓' if proj['has_research_report'] else '✗'}")
    print(f"  故事圣经: {'✓' if proj['has_story_bible'] else '✗'}")
    print(f"  剧本: {proj['scripts_count']} 集 (源文档 {proj.get('docx_episodes', 0)} 集, 有效 {effective} 集)")
    print(f"  大纲: {len(proj['outline_files'])} 文件")
    if proj['characters']:
        print(f"  角色: {', '.join(proj['characters'])}")
    if proj['keywords']:
        print(f"  赛道关键词: {', '.join(proj['keywords'])}")
    print(f"  最后修改: {proj['last_modified'] or '未知'}")


if __name__ == "__main__":
    main()
