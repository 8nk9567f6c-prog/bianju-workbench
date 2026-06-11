"""Save self-check reports to an accumulating Word doc in a subfolder.
Usage: python save_check.py <project_dir> <check_content.md>

Reads check_content.md and appends it to the accumulating self-check
markdown file in <project_dir>/自检/. Then regenerates the full docx.
"""
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from md2docx import convert_md_to_docx


def append_check(project_dir, content_md_path):
    checks_dir = Path(project_dir) / "自检"
    checks_dir.mkdir(parents=True, exist_ok=True)

    accum_md = checks_dir / "自检记录.md"

    # Read new content
    with open(content_md_path, "r", encoding="utf-8") as f:
        new_content = f.read().strip()

    if not new_content:
        print("[自检] 内容为空，跳过")
        return

    # Append to accumulating markdown
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    separator = "\n\n---\n\n"

    with open(accum_md, "a", encoding="utf-8") as f:
        if accum_md.stat().st_size > 0:
            f.write(separator)
        f.write(f"## {timestamp}\n\n")
        f.write(new_content)

    # Regenerate docx from accumulated markdown
    docx_path = checks_dir / "自检记录.docx"
    convert_md_to_docx(str(accum_md), str(docx_path))

    # Count total checks
    check_count = 0
    with open(accum_md, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("## 20"):
                check_count += 1

    print(f"[自检] 已追加 → 自检/自检记录.docx（累计 {check_count} 次）")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python save_check.py <project_dir> <check_content.md>")
        sys.exit(1)

    project_dir = sys.argv[1]
    content_md = sys.argv[2]

    if not Path(content_md).exists():
        print(f"Error: input file not found: {content_md}")
        sys.exit(1)

    append_check(project_dir, content_md)
