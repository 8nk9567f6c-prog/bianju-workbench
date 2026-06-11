@echo off
chcp 65001 >nul
cd /d "D:\WorkSpace\编剧工作台\docs"

echo.
echo ╔══════════════════════════════════════════╗
echo ║     编剧工作台 — 局域网服务器           ║
echo ╚══════════════════════════════════════════╝
echo.

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "IP=%%a"
    setlocal enabledelayedexpansion
    set "IP=!IP: =!"
    echo   本机局域网 IP: !IP!
    endlocal
    goto :found
)
:found
echo   服务端口:      8080
echo.
echo ═══════════════════════════════════════════
echo   iPhone 打开 Safari，输入下方地址：
echo.
echo   http://%ip%:8080
echo.
echo ═══════════════════════════════════════════
echo   按 Ctrl+C 可停止服务器
echo.

python -m http.server 8080 --bind 0.0.0.0

pause
