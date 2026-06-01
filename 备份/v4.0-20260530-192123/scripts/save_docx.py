"""Save markdown content as a sequentially numbered Word doc in a project folder.
Usage: python save_docx.py <project_dir> <title_slug> <input.md>

Reads markdown from input.md, saves as <project_dir>/NN-title_slug.docx
where NN is auto-incremented from the project's .docx_seq counter.
"""

import sys
import os
from pathlib import Path

# Add scripts dir to path to import md2docx
sys.path.insert(0, str(Path(__file__).parent))
from md2docx import convert_md_to_docx

PYTHON = r"C:\Users\17928\AppData\Local\Programs\Python\Python312\python.exe"


def get_next_seq(project_dir):
    seq_file = Path(project_dir) / ".docx_seq"
    if seq_file.exists():
        current = int(seq_file.read_text().strip())
    else:
        current = 0
    next_num = current + 1
    seq_file.write_text(str(next_num))
    return next_num


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python save_docx.py <project_dir> <title_slug> <input.md>")
        print("  title_slug examples: 对标分析, 逻辑备忘录, 大纲, 人物小传")
        sys.exit(1)

    project_dir = sys.argv[1]
    title_slug = sys.argv[2]
    md_path = sys.argv[3]

    if not Path(md_path).exists():
        print(f"Error: input file not found: {md_path}")
        sys.exit(1)

    Path(project_dir).mkdir(parents=True, exist_ok=True)
    seq = get_next_seq(project_dir)
    filename = f"{seq:02d}-{title_slug}.docx"
    output_path = str(Path(project_dir) / filename)

    convert_md_to_docx(md_path, output_path)
    print(f"[Word] {filename}")
