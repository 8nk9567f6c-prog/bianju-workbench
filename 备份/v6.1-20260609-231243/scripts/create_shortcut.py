#!/usr/bin/env python3
"""Create desktop shortcut for 脚本工作台 v6.0"""
import os

desktop = os.path.expanduser(r"~\Desktop")
bat_path = os.path.join(desktop, "编剧工作台.bat")

lines = [
    "@echo off",
    "chcp 65001 >nul",
    'cd /d "D:\\WorkSpace\\编剧工作台"',
    "",
    "echo.",
    "echo   ╔══════════════════════════════════════════╗",
    "echo   ║       编 剧 工 作 台  v6.0              ║",
    "echo   ║   四 Agent 调度框架 + 自审内置           ║",
    "echo   ╚══════════════════════════════════════════╝",
    "echo.",
    "echo   项目路径: D:\\WorkSpace\\编剧工作台\\",
    "echo   4 Agent / 16 MCP / 自审内置 / 渐进披露",
    "echo   输入 /调度 开始",
    "echo   ──────────────────────────────────────────",
    "echo.",
    "",
    "claude",
]

with open(bat_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"Created: {bat_path}")

# Verify
with open(bat_path, "r", encoding="utf-8") as f:
    content = f.read()
print(f"Lines: {len(content.splitlines())}")
