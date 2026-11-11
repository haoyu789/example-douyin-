@echo off
rem 双击运行：批量下载抖音视频（读取 urls.txt）
chcp 65001 >nul
cd /d "%~dp0"
d:/DouyinDownloader/.venv/Scripts/python.exe batch_download_douyin.py
echo.
pause
