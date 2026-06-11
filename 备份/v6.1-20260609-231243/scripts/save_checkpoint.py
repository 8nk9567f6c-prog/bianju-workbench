"""
Session checkpoint auto-saver for 编剧工作台 Stop hook.
Updates CORE_CREATIVE_DNA.md 会话检查点 with timestamp.
"""
import sys
import os
from datetime import datetime

DNA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "CORE_CREATIVE_DNA.md")

CHECKPOINT_TEMPLATE = """
### 最近会话摘要
- 日期：{date}
- 会话ID：{session_id}
- 项目目录：{project_dir}
- 操作内容：[由用户在下一次会话中手动补充]
- 关键决策：[待补充]
- 下一步：[待补充]
- 待解决问题：无
"""

def main():
    project_dir = ""
    session_id = ""
    for arg in sys.argv[1:]:
        if arg.startswith("--project="):
            project_dir = arg.split("=", 1)[1]
        elif arg.startswith("--session="):
            session_id = arg.split("=", 1)[1]

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    if not os.path.exists(DNA_PATH):
        print(f"[checkpoint] DNA file not found at {DNA_PATH}, skipping auto-save")
        return

    with open(DNA_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    checkpoint_block = CHECKPOINT_TEMPLATE.format(
        date=date_str,
        session_id=session_id or "unknown",
        project_dir=project_dir or os.path.dirname(DNA_PATH),
    )

    marker = "## 四、会话检查点"
    if marker in content:
        idx = content.index(marker)
        next_marker = content.find("\n## ", idx + len(marker))
        if next_marker == -1:
            next_marker = content.find("\n---", idx + len(marker))
        if next_marker == -1:
            next_marker = len(content)

        before = content[:idx + len(marker)]
        after = content[next_marker:]

        new_content = before + "\n" + checkpoint_block + "\n" + after
        with open(DNA_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[checkpoint] Session checkpoint saved to CORE_CREATIVE_DNA.md ({date_str})")
    else:
        print("[checkpoint] Checkpoint marker not found, appending...")
        with open(DNA_PATH, "a", encoding="utf-8") as f:
            f.write("\n" + checkpoint_block)
        print(f"[checkpoint] Session checkpoint appended ({date_str})")


if __name__ == "__main__":
    main()
