from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from download_douyin import download

TOOL_DIR = Path(__file__).resolve().parent
URLS_FILE = TOOL_DIR / "urls.txt"
FAILED_FILE = TOOL_DIR / "failed_urls.txt"
URL_PATTERN = re.compile(r"https?://[^\s]+")


@dataclass(frozen=True)
class BatchSummary:
    total: int
    succeeded: int
    failed: int


def read_urls(urls_file: Path) -> list[str]:
    if not urls_file.exists():
        return []

    urls: list[str] = []
    seen: set[str] = set()
    for line in urls_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for match in URL_PATTERN.findall(stripped):
            url = match.rstrip("，。,.!！)")
            if url not in seen:
                urls.append(url)
                seen.add(url)
    return urls


def append_failure(failed_file: Path, url: str, return_code: int) -> None:
    with failed_file.open("a", encoding="utf-8") as file:
        file.write(f"{url}\t{return_code}\n")


def run_batch(
    urls_file: Path = URLS_FILE,
    failed_file: Path = FAILED_FILE,
    downloader: Callable[[str], int] = download,
    sleep_seconds: int = 5,
) -> BatchSummary:
    urls = read_urls(urls_file)
    if failed_file.exists():
        failed_file.unlink()

    succeeded = 0
    failed = 0
    for index, url in enumerate(urls, start=1):
        print(f"[{index}/{len(urls)}] {url}")
        return_code = downloader(url)
        if return_code == 0:
            succeeded += 1
        else:
            failed += 1
            append_failure(failed_file, url, return_code)

        if index < len(urls) and sleep_seconds > 0:
            time.sleep(sleep_seconds)

    return BatchSummary(total=len(urls), succeeded=succeeded, failed=failed)


def main() -> int:
    print("Douyin batch downloader")
    print(f"URL file: {URLS_FILE}")
    print("One public Douyin share link per line. Pasted share text is also OK.")

    urls = read_urls(URLS_FILE)
    if not urls:
        print(f"No URLs found. Add links to: {URLS_FILE}")
        return 2

    summary = run_batch(URLS_FILE, FAILED_FILE)
    print(f"Finished. Total: {summary.total}, succeeded: {summary.succeeded}, failed: {summary.failed}")
    if summary.failed:
        print(f"Failed URLs: {FAILED_FILE}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
