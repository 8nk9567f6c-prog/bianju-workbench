@echo off
chcp 65001 >nul 2>nul
cd /d "C:\Users\17928\Desktop\编剧工作台"
cls
echo.
echo  ╔══════════════════════════════════╗
echo  ║      编 剧 工 作 台 v2.0      ║
echo  ║    短剧创作专用 Claude Code   ║
echo  ╚══════════════════════════════════╝
echo.
echo  工作流已加载：
echo  - 对标分析 / 逻辑备忘录 / 大纲 / 人物小传
echo  - 分集梗概 / 剧本正文 / 质量复盘
echo.
echo  创作命令示例：
echo    创建新项目《XX》
echo    对标分析
echo    生成逻辑备忘录
echo    生成大纲
echo    生成人物小传
echo    生成分集梗概
echo    写剧本正文
echo    继续 / 修改第X集 / 复盘钩子 / 复盘逻辑
echo    复盘节奏 / 更新备忘录 / 记忆点 / 导出
echo.
echo  ─────────────────────────────────
echo  正在启动 Claude Code...
echo  ─────────────────────────────────
echo.
where claude >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 claude 命令，请确认 Claude Code 已安装并加入 PATH。
    echo 安装方法：npm install -g @anthropic-ai/claude-code
    pause
    exit /b 1
)
claude
exit /b 0
