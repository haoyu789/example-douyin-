@echo off
rem 双击运行：登录抖音以获取有效 cookie（下载报 403 / Fresh cookies 时先跑这个）
chcp 65001 >nul
cd /d "%~dp0"
d:/DouyinDownloader/.venv/Scripts/python.exe init_login.py
echo.
pause
