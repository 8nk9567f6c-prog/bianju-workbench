@echo off
chcp 65001 >nul
title 编剧工作台 - 本地服务器

echo.
echo  ╔══════════════════════════════════╗
echo  ║     编剧工作台 v5.5 服务器      ║
echo  ╚══════════════════════════════════╝
echo.

REM Get local IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "IP=%%a"
    setlocal enabledelayedexpansion
    set "IP=!IP: =!"
    echo   电脑访问: http://localhost:8080
    echo   手机访问: http://!IP!:8080
    endlocal
    goto :found
)
:found

echo.
echo   按 Ctrl+C 停止服务器
echo   ────────────────────────────────
echo.

cd /d "%~dp0docs"
python -m http.server 8080

pause
