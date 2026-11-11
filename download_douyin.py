from __future__ import annotations
from pathlib import Path
import subprocess
import sys
import time

OUTPUT_DIR = Path(r"D:\DouyinVideos")
TOOL_DIR = Path(__file__).resolve().parent
EDGE_PATH = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
EDGE_PROFILE_DIR = TOOL_DIR / "EdgeTempProfile"
COOKIE_FILE = TOOL_DIR / "edge-temp-cookies.txt"
COOKIE_EXPORTER = TOOL_DIR / "export_edge_cookies.js"
DEBUGGING_PORT = "9222"

# 抖音页面需要足够时间加载并由 JS 生成 __ac_signature，太短会拿到无效凭证
PAGE_WAIT_SECONDS = 30
# 风控较严时刷新一次 cookie 后重试，通常第二次即可通过
MAX_RETRIES = 2

# 与本地 Edge 版本保持一致，避免 UA 与 cookie 指纹不匹配触发风控
EDGE_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36 Edg/155.0.4283.62"
)


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_command(url: str) -> list[str]:
    output_template = str(OUTPUT_DIR / "%(title).120s-%(id)s.%(ext)s")
    return [
        sys.executable,
        "-m",
        "yt_dlp",
        "--no-playlist",
        "--cookies",
        str(COOKIE_FILE),
        "--user-agent",
        EDGE_UA,
        "--referer",
        "https://www.douyin.com/",
        "-o",
        output_template,
        url,
    ]


def create_fresh_cookie_file(url: str) -> None:
    if not EDGE_PATH.exists():
        raise RuntimeError(f"Microsoft Edge was not found at {EDGE_PATH}")
    if not COOKIE_EXPORTER.exists():
        raise RuntimeError(f"Cookie exporter was not found at {COOKIE_EXPORTER}")

    process = subprocess.Popen([
        str(EDGE_PATH),
        f"--remote-debugging-port={DEBUGGING_PORT}",
        f"--user-data-dir={EDGE_PROFILE_DIR}",
        "--no-first-run",
        "--disable-default-apps",
        url,
    ])
    try:
        time.sleep(PAGE_WAIT_SECONDS)
        _ = subprocess.run(
            ["node", str(COOKIE_EXPORTER), str(COOKIE_FILE)],
            check=True,
        )
    finally:
        process.terminate()
        # 给 Edge 留出释放调试端口的时间，否则下一次启动会复用失败
        time.sleep(2)


def download(url: str) -> int:
    """下载单个视频；失败时刷新 cookie 后自动重试。"""
    ensure_output_dir()
    return_code = 1
    for attempt in range(1, MAX_RETRIES + 1):
        create_fresh_cookie_file(url)
        completed = subprocess.run(build_command(url), check=False)
        return_code = completed.returncode
        if return_code == 0:
            return 0
        if attempt < MAX_RETRIES:
            notice = (
                f"Download failed (code {return_code}). "
                f"Refreshing cookies and retrying ({attempt}/{MAX_RETRIES})..."
            )
            print(notice)
    return return_code


def _download_from_file(url_file: Path) -> int:
    """逐行读取链接并批量下载（复用 batch 模块的解析/失败记录逻辑）。"""
    # 本文件以脚本方式直接运行，只能使用绝对导入（相对导入会失败）
    if str(TOOL_DIR) not in sys.path:
        sys.path.insert(0, str(TOOL_DIR))
    import batch_download_douyin as batch  # pyright: ignore[reportImplicitRelativeImport]
    urls = batch.read_urls(url_file)
    if not urls:
        print(f"No URLs found in: {url_file}")
        return 2
    summary = batch.run_batch(
        urls_file=url_file,
        failed_file=TOOL_DIR / "failed_urls.txt",
        downloader=download,
        sleep_seconds=5,
    )
    message = (
        f"Finished. Total: {summary.total}, succeeded: {summary.succeeded}, "
        f"failed: {summary.failed}"
    )
    print(message)
    return 0 if summary.failed == 0 else 1
 

def main() -> int:
    print("Douyin video downloader")
    print(f"Save directory: {OUTPUT_DIR}")
    try:
        ensure_output_dir()
    except OSError as exc:
        print(f"Could not prepare save directory: {exc}")
        return 7

    # 支持命令行直接传链接：python download_douyin.py <url>
    # 也支持传文件路径（每行一个链接）
    if len(sys.argv) > 1:
        args_url = sys.argv[1].strip()
        if args_url.startswith("http://") or args_url.startswith("https://"):
            return download(args_url)
        url_file = Path(args_url)
        if url_file.is_file():
            return _download_from_file(url_file)
        print(f"Unrecognized argument: {args_url}")
        return 2

    url = input("Paste one public Douyin share URL: ").strip()
    if not url:
        print("No URL provided.")
        return 2

    try:
        return_code = download(url)
    except RuntimeError as exc:
        print(str(exc))
        return 5
    except subprocess.CalledProcessError as exc:
        print(f"Could not export temporary Edge cookies: {exc}")
        return 6
    except OSError as exc:
        print(f"Could not run download: {exc}")
        return 40

    if return_code == 0:
        print(f"Done. Check: {OUTPUT_DIR}")
    else:
        print("Download failed. Confirm the URL is public and supported by yt-dlp.")
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())