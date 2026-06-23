"""
Session checkpoint auto-saver for 编剧工作台 Stop hook.
Updates CORE_CREATIVE_DNA.md 会话检查点 with actual session info.
v2.0 — 不再写[待补充]占位符，改为自动捕获会话产出。
"""
import sys
import os
from datetime import datetime

DNA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "CORE_CREATIVE_DNA.md")
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHECKPOINT_TEMPLATE = """### {date}
- 会话ID：{session_id}
- 活跃项目：{project}
- 产出文件：{files}
- 待念念审：{pending_review}
"""


def detect_activity():
    """扫描工作区最近修改的文件，推断会话做了什么"""
    recent_files = []
    projects_touched = set()
    workspace_dir = WORKSPACE

    # 扫描 作品/ 目录下最近修改的 .md 文件
    works_dir = os.path.join(workspace_dir, "作品")
    if os.path.exists(works_dir):
        for root, dirs, files in os.walk(works_dir):
            for f in files:
                if f.endswith(".md"):
                    full = os.path.join(root, f)
                    try:
                        mtime = os.path.getmtime(full)
                        # 最近 2 小时内修改的
                        if datetime.now().timestamp() - mtime < 7200:
                            rel = os.path.relpath(full, workspace_dir)
                            recent_files.append(rel)
                            # 提取项目名（作品/项目名/...）
                            parts = rel.replace("\\", "/").split("/")
                            if len(parts) >= 2:
                                projects_touched.add(parts[1])
                    except OSError:
                        pass

    project_str = ", ".join(projects_touched) if projects_touched else "未识别"
    files_str = ", ".join(recent_files[:5]) if recent_files else "无新增文件"
    if len(recent_files) > 5:
        files_str += f" 等{len(recent_files)}个文件"

    pending = "是" if recent_files else "无"

    return project_str, files_str, pending


def main():
    session_id = ""
    for arg in sys.argv[1:]:
        if arg.startswith("--session="):
            session_id = arg.split("=", 1)[1]

    # 也尝试从环境变量获取
    if not session_id:
        session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    project, files, pending = detect_activity()

    if not os.path.exists(DNA_PATH):
        print(f"[checkpoint] DNA file not found at {DNA_PATH}, creating minimal record")
        checkpoint_dir = os.path.join(WORKSPACE, ".claude", "checkpoints")
        os.makedirs(checkpoint_dir, exist_ok=True)
        checkpoint_path = os.path.join(checkpoint_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            f.write(CHECKPOINT_TEMPLATE.format(
                date=date_str, session_id=session_id,
                project=project, files=files, pending_review=pending
            ))
        print(f"[checkpoint] Saved to {checkpoint_path}")
        return

    with open(DNA_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    checkpoint_block = CHECKPOINT_TEMPLATE.format(
        date=date_str,
        session_id=session_id,
        project=project,
        files=files,
        pending_review=pending,
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
        print(f"[checkpoint] Session saved ({date_str}) | 项目:{project} | 文件:{files}")
    else:
        print("[checkpoint] Marker not found, appending...")
        with open(DNA_PATH, "a", encoding="utf-8") as f:
            f.write("\n" + checkpoint_block)
        print(f"[checkpoint] Appended ({date_str})")
