# Douyin Downloader

批量下载抖音公开视频的小工具，基于 `yt-dlp` + Edge 浏览器 Cookie 自动导出。

## 环境要求

| 组件 | 版本 | 说明 |
| --- | --- | --- |
| Python | 3.12.x | 虚拟环境位于 `D:\DouyinDownloader\.venv` |
| yt-dlp | >= 2026.8.19 | 已通过 `requirements.txt` 安装 |
| Node.js | >= 18 | 用于执行 Cookie 导出脚本 `export_edge_cookies.js` |
| Microsoft Edge | 任意 | 用于启动调试端口导出登录 Cookie（路径已硬编码在 `download_douyin.py`） |

## 环境配置（如换机器/重装）

```powershell
# 1. 创建虚拟环境并安装依赖
python -m venv D:\DouyinDownloader\.venv
D:\DouyinDownloader\.venv\Scripts\python -m pip install -r requirements.txt

# 2. 验证
D:\DouyinDownloader\.venv\Scripts\python -m yt_dlp --version
```

## 使用方法

### 单个下载

```powershell
cd D:\DouyinDownloader\DouyinDownloader
..\.venv\Scripts\python download_douyin.py
```

按提示粘贴抖音分享链接（`https://v.douyin.com/xxxx/` 或整段分享文案均可）。
程序会自动打开 Edge 获取新鲜 Cookie，再调用 yt-dlp 下载到 `D:\DouyinVideos`。

### 批量下载

1. 在 `urls.txt` 中每行写一个链接（支持整段分享文案，`#` 开头为注释）。
2. 运行：

```powershell
..\.venv\Scripts\python batch_download_douyin.py
```

失败的链接会记录到 `failed_urls.txt`（格式：`URL<TAB>返回码`）。

### 运行测试

```powershell
..\.venv\Scripts\python -m unittest tests.test_batch_download_douyin -v
```

## 文件说明

| 文件 | 作用 |
| --- | --- |
| `download_douyin.py` | 单链接下载入口，含 Edge Cookie 自动导出 |
| `batch_download_douyin.py` | 批量下载入口，失败自动记录 |
| `export_edge_cookies.js` | 通过 Edge 远程调试端口导出抖音 Cookie（Netscape 格式） |
| `edge-temp-cookies.txt` | 最近一次导出的 Cookie（自动生成，请勿提交） |
| `urls.txt` | 批量下载的链接清单 |
| `EdgeTempProfile/` | Edge 临时用户目录（自动生成，可随时删除） |
| `requirements.txt` | Python 依赖清单 |

## 常见问题

- **No module named yt_dlp**：确认用的是虚拟环境的 Python（`D:\DouyinDownloader\.venv\Scripts\python.exe`），并已执行 `pip install -r requirements.txt`。
- **Cookie 失效 / 下载 403**：脚本每次运行都会重新从 Edge 导出 Cookie；若仍失败，确认 Edge 中已登录抖音且可正常浏览视频页。
- **Edge 路径找不到**：检查 `download_douyin.py` 中 `EDGE_PATH` 是否指向本机 Edge 安装位置。
