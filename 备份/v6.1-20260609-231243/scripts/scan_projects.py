#!/usr/bin/env python3
"""scan_projects.py — 扫描作品/目录，输出结构化项目数据（供 Agent 0 调度使用）

用法:
  python scan_projects.py [--workspace 作品目录路径] [--json] [--project 项目名]

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


def find_scripts(project_path):
    """Find script files in various locations within a project."""
    scripts = []
    patterns = ["剧本-第*.md", "剧本/*.md", "剧本-*.md"]
    for pattern in patterns:
        for f in project_path.glob(pattern):
            if f.is_file():
                scripts.append(f.name)
    return sorted(set(scripts))


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

        project_data = {
            "name": project_dir.name,
            "path": str(project_dir),
            "has_anchor": anchor.exists(),
            "has_research_report": research.exists(),
            "has_story_bible": bible.exists(),
            "scripts_count": len(scripts),
            "outline_files": outlines,
            "last_modified": last_mod,
            "characters": extract_characters_from_anchor(anchor) if anchor.exists() else [],
            "keywords": extract_keywords_from_anchor(anchor) if anchor.exists() else []
        }
        projects.append(project_data)
        if len(scripts) > 0:
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
    print(f"▸ {proj['name']}")
    print(f"  锚点: {'✓' if proj['has_anchor'] else '✗'}")
    print(f"  调研报告: {'✓' if proj['has_research_report'] else '✗'}")
    print(f"  故事圣经: {'✓' if proj['has_story_bible'] else '✗'}")
    print(f"  剧本: {proj['scripts_count']} 集")
    print(f"  大纲: {len(proj['outline_files'])} 文件")
    if proj['characters']:
        print(f"  角色: {', '.join(proj['characters'])}")
    if proj['keywords']:
        print(f"  赛道关键词: {', '.join(proj['keywords'])}")
    print(f"  最后修改: {proj['last_modified'] or '未知'}")


if __name__ == "__main__":
    main()
