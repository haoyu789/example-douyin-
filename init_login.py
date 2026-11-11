"""首次使用 / cookie 失效时：在临时 Edge 配置中登录抖音并导出登录态 cookie。

登录状态会保存在 EdgeTempProfile 目录中，之后正常下载时会自动带上登录态，
从而绕过抖音对未登录会话的风控（403 / "Fresh cookies are needed"）。
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import download_douyin as dd

LOGIN_URL = "https://www.douyin.com/"
# 登录后才会出现的字段，用于判断登录是否成功
LOGGED_IN_MARKERS = ("sessionid", "sid_tt", "uid_tt")


def export_cookies() -> bool:
    """导出 cookie 并返回是否检测到登录态。"""
    subprocess.run(
        ["node", str(dd.COOKIE_EXPORTER), str(dd.COOKIE_FILE)],
        check=True,
    )
    content = dd.COOKIE_FILE.read_text(encoding="utf-8", errors="ignore")
    return any(marker in content for marker in LOGGED_IN_MARKERS)


def main() -> int:
    print("=" * 56)
    print("抖音登录初始化（只需做一次）")
    print("=" * 56)
    print("流程：")
    print("  1. 自动打开 Edge 浏览器（独立的临时配置，不影响你日常浏览器）")
    print("  2. 在浏览器里登录抖音（扫码 / 手机号验证码均可）")
    print("  3. 确认能看到自己的头像后，回到本窗口按回车")
    print()

    if not dd.EDGE_PATH.exists():
        print(f"未找到 Edge: {dd.EDGE_PATH}")
        return 5
    if not dd.COOKIE_EXPORTER.exists():
        print(f"未找到导出脚本: {dd.COOKIE_EXPORTER}")
        return 5

    input("按回车打开浏览器...")

    process = subprocess.Popen([
        str(dd.EDGE_PATH),
        f"--remote-debugging-port={dd.DEBUGGING_PORT}",
        f"--user-data-dir={dd.EDGE_PROFILE_DIR}",
        "--no-first-run",
        "--disable-default-apps",
        LOGIN_URL,
    ])

    try:
        input("\n登录完成后，按回车导出 cookie...")
        print("正在导出 cookie...")
        logged_in = export_cookies()
        size = dd.COOKIE_FILE.stat().st_size if dd.COOKIE_FILE.exists() else 0
        print(f"Cookie 已保存: {dd.COOKIE_FILE} ({size} 字节)")

        if logged_in:
            print("\n[成功] 已检测到登录态 cookie，现在可以正常下载了。")
            return 0
        print("\n[注意] 未检测到登录字段，可能没有登录成功。")
        print("请重新运行本脚本，确认在浏览器中完成登录。")
        return 1
    except subprocess.CalledProcessError as exc:
        print(f"导出 cookie 失败: {exc}")
        print("请确认浏览器已完全打开、且 node 已安装。")
        return 6
    finally:
        process.terminate()
        time.sleep(2)


if __name__ == "__main__":
    raise SystemExit(main())
