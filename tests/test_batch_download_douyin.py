import tempfile
import unittest
from pathlib import Path

import batch_download_douyin as batch


class BatchDownloadTests(unittest.TestCase):
    def test_read_urls_extracts_links_from_pasted_share_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            urls_file = Path(temp_dir) / "urls.txt"
            urls_file.write_text(
                "# comment line\n"
                "\n"
                "文案 https://v.douyin.com/abc123/ 复制此链接\n"
                "https://v.douyin.com/def456/\n",
                encoding="utf-8",
            )

            self.assertEqual(
                batch.read_urls(urls_file),
                ["https://v.douyin.com/abc123/", "https://v.douyin.com/def456/"],
            )

    def test_run_batch_records_failures_and_continues(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            urls_file = Path(temp_dir) / "urls.txt"
            failed_file = Path(temp_dir) / "failed_urls.txt"
            urls_file.write_text(
                "https://v.douyin.com/ok111/\n"
                "https://v.douyin.com/fail222/\n",
                encoding="utf-8",
            )
            calls = []

            def fake_downloader(url):
                calls.append(url)
                return 7 if "fail" in url else 0

            summary = batch.run_batch(
                urls_file=urls_file,
                failed_file=failed_file,
                downloader=fake_downloader,
                sleep_seconds=0,
            )

            self.assertEqual(calls, ["https://v.douyin.com/ok111/", "https://v.douyin.com/fail222/"])
            self.assertEqual(summary, batch.BatchSummary(total=2, succeeded=1, failed=1))
            self.assertEqual(failed_file.read_text(encoding="utf-8"), "https://v.douyin.com/fail222/\t7\n")


if __name__ == "__main__":
    unittest.main()
