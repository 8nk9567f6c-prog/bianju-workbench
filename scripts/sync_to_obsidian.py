#!/usr/bin/env python3
"""sync_to_obsidian.py — 将剧本工作台产出自动同步到 Obsidian 仓库（按项目分文件夹）

用法:
  python sync_to_obsidian.py <源文件路径> [--project 项目名] [--vault 仓库路径]
  python sync_to_obsidian.py --scan <项目目录> [--vault 仓库路径]
  python sync_to_obsidian.py --scan-all [--vault 仓库路径]

仓库结构:
  {vault}/
  ├── 项目A/
  │   ├── 剧本/
  │   │   ├── 剧本-第1集.md
  │   │   └── ...
  │   ├── 大纲/
  │   │   └── ...
  │   └── ANCHOR.md
  └── 项目B/
      └── ...

配置:
  默认 Obsidian 仓库: D:/Obsidian/剧本库/
  可通过环境变量 OBSIDIAN_VAULT 覆盖
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def get_vault_path(vault_arg=None):
    if vault_arg:
        return Path(vault_arg)
    env_vault = os.environ.get("OBSIDIAN_VAULT", "")
    if env_vault:
        return Path(env_vault)
    return Path("D:/Obsidian/剧本库")


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    return path


def _append_sync_note(filepath, source_path):
    try:
        content = filepath.read_text(encoding="utf-8")
        sync_line = f"\n\n%% 同步自: {source_path} | {datetime.now().strftime('%Y-%m-%d %H:%M')} %%\n"
        if "%% 同步自:" not in content:
            filepath.write_text(content + sync_line, encoding="utf-8")
    except Exception:
        pass


def copy_and_tag(source, dest):
    """复制文件并追加同步标记"""
    shutil.copy2(source, dest)
    _append_sync_note(dest, source)


def scan_and_sync(project_dir, vault_root):
    """扫描单个项目目录，按子目录结构同步到 vault/{项目名}/"""
    project_dir = Path(project_dir)
    if not project_dir.is_dir():
        return {"status": "error", "reason": f"项目目录不存在: {project_dir}"}

    project_name = project_dir.name
    if project_name.startswith("_"):  # 跳过模板等内部目录
        return {"status": "skip", "reason": f"跳过内部目录: {project_name}"}

    project_vault = ensure_dir(vault_root / project_name)
    results = []

    # 1. 同步剧本文件 — 扫描 剧本/ 子目录 + 项目根目录
    script_files = []
    script_dir = project_dir / "剧本"
    if script_dir.is_dir():
        script_files.extend((f, "剧本") for f in script_dir.glob("剧本-第*.md"))
    script_files.extend((f, "剧本") for f in project_dir.glob("剧本-第*.md"))

    seen_scripts = set()
    dest_script_dir = ensure_dir(project_vault / "剧本")
    for f, _ in sorted(script_files):
        if f.name in seen_scripts:
            continue
        seen_scripts.add(f.name)
        dest = dest_script_dir / f.name
        copy_and_tag(f, dest)
        results.append({"file": f"剧本/{f.name}", "status": "ok"})

    # 2. 同步大纲文件
    outline_dir = project_dir / "大纲"
    if outline_dir.is_dir():
        outline_files = sorted(outline_dir.glob("*.md"))
        if outline_files:
            dest_outline_dir = ensure_dir(project_vault / "大纲")
            for f in outline_files:
                dest = dest_outline_dir / f.name
                copy_and_tag(f, dest)
                results.append({"file": f"大纲/{f.name}", "status": "ok"})

    # 3. 同步 ANCHOR.md
    anchor = project_dir / "ANCHOR.md"
    if anchor.exists():
        dest = project_vault / "ANCHOR.md"
        copy_and_tag(anchor, dest)
        results.append({"file": "ANCHOR.md", "status": "ok"})

    return {"status": "ok", "project": project_name, "synced": results}


def scan_all_projects(workspace_dir, vault_root):
    """扫描作品目录下所有项目并同步"""
    workspace = Path(workspace_dir)
    if not workspace.is_dir():
        return {"status": "error", "reason": f"作品目录不存在: {workspace_dir}"}

    all_results = []
    for project_dir in sorted(workspace.iterdir()):
        if not project_dir.is_dir():
            continue
        result = scan_and_sync(project_dir, vault_root)
        if result["status"] == "ok" and result["synced"]:
            all_results.append(result)
        elif result["status"] == "error":
            all_results.append(result)

    return {"status": "ok", "total_projects": len(all_results), "results": all_results}


def list_vault(vault_root):
    """列出仓库中所有项目及文件"""
    vault_root = Path(vault_root)
    if not vault_root.is_dir():
        print("▸ 仓库为空，还没有同步过文件。")
        return

    projects = sorted(d for d in vault_root.iterdir() if d.is_dir())
    if not projects:
        print("▸ 仓库为空，还没有同步过文件。")
        return

    total_files = 0
    for proj in projects:
        files = sorted(proj.rglob("*.md"))
        total_files += len(files)
        print(f"▸ {proj.name}/ ({len(files)} 文件)")
        for f in files:
            rel = f.relative_to(proj)
            size_kb = f.stat().st_size / 1024
            print(f"    {rel} ({size_kb:.1f} KB)")
    print(f"▸ 总计: {len(projects)} 项目, {total_files} 文件")


def main():
    parser = argparse.ArgumentParser(description="同步剧本到 Obsidian 仓库（按项目分文件夹）")
    parser.add_argument("source", nargs="?", help="源文件路径")
    parser.add_argument("--project", "-p", help="项目名称")
    parser.add_argument("--vault", "-v", help="Obsidian 仓库路径（默认 D:/Obsidian/剧本库/）")
    parser.add_argument("--scan", "-s", help="扫描并同步单个项目目录")
    parser.add_argument("--scan-all", action="store_true", help="扫描作品目录下所有项目并同步")
    parser.add_argument("--list", "-l", action="store_true", help="列出仓库中所有已同步的文件")
    parser.add_argument("--clean", action="store_true", help="清除仓库根目录的旧扁平文件（迁移到新结构后使用）")

    args = parser.parse_args()
    vault_root = get_vault_path(args.vault)

    if args.list:
        print(f"▸ Obsidian 仓库: {vault_root}")
        list_vault(vault_root)
        return

    if args.clean:
        # 删除仓库根目录的 .md 文件（旧扁平结构残留）
        removed = 0
        for f in vault_root.glob("*.md"):
            f.unlink()
            removed += 1
        print(f"▸ 已清除 {removed} 个旧扁平文件")
        return

    if args.scan_all:
        workspace = Path("D:/WorkSpace/编剧工作台/作品")
        print(f"▸ Obsidian 仓库: {vault_root}")
        result = scan_all_projects(workspace, vault_root)
        if result["status"] == "ok":
            for r in result["results"]:
                if r["status"] == "ok":
                    print(f"▸ {r['project']}: 同步 {len(r['synced'])} 个文件")
                    for item in r["synced"]:
                        print(f"    ✓ {item['file']}")
                else:
                    print(f"▸ {r.get('project', '?')}: ✗ {r.get('reason', '')}")
            print(f"▸ 总计: {result['total_projects']} 个项目已同步")
        else:
            print(f"✗ {result['reason']}")
            sys.exit(1)
        return

    if args.scan:
        print(f"▸ Obsidian 仓库: {vault_root}")
        result = scan_and_sync(args.scan, vault_root)
        if result["status"] == "ok":
            print(f"▸ {result['project']}: 同步 {len(result['synced'])} 个文件")
            for item in result["synced"]:
                print(f"    ✓ {item['file']}")
        elif result["status"] == "skip":
            print(f"▸ 跳过: {result['reason']}")
        else:
            print(f"✗ {result['reason']}")
            sys.exit(1)
        return

    if not args.source:
        parser.print_help()
        sys.exit(1)

    # 单文件同步 — 按项目分目录
    source = Path(args.source)
    if not source.exists():
        print(f"✗ 源文件不存在: {args.source}")
        sys.exit(1)

    project_name = args.project or "未分类"
    project_vault = ensure_dir(vault_root / project_name)

    # 根据文件路径判断子目录
    source_str = str(source)
    if "剧本" in source_str or "剧本-" in source.name:
        dest_dir = ensure_dir(project_vault / "剧本")
    elif "大纲" in source_str:
        dest_dir = ensure_dir(project_vault / "大纲")
    else:
        dest_dir = project_vault

    dest = dest_dir / source.name
    copy_and_tag(source, dest)
    print(f"▸ Obsidian 仓库: {vault_root}")
    print(f"▸ 同步完成: {project_name}/{dest.relative_to(project_vault)} ({source.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
