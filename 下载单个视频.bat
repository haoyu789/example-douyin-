@echo off
rem 双击运行：单个抖音视频下载
chcp 65001 >nul
cd /d "%~dp0"
d:/DouyinDownloader/.venv/Scripts/python.exe download_douyin.py
echo.
pause
