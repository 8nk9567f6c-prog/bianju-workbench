#!/usr/bin/env python3
"""Create desktop shortcut for 编剧工作台 v7.1"""
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
    "echo   ║       编 剧 工 作 台  v7.1              ║",
    "echo   ║  4 Agent + 17 MCP + Forge Loop          ║",
    "echo   ╚══════════════════════════════════════════╝",
    "echo.",
    "echo   项目路径: D:\\WorkSpace\\编剧工作台\\",
    "echo   4 Agent / 17 MCP / Forge Loop / 收敛式修订",
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
