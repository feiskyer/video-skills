---
name: download-video
metadata:
  version: "1.0.3"
description: Download videos from 1000+ websites (YouTube, Bilibili, Twitter/X, TikTok, Vimeo, Instagram, Twitch, etc.) using yt-dlp. Use this skill whenever a user shares a video URL, asks to save or download a video, wants to extract audio from an online video, needs a specific quality like 1080p or 4K, or mentions downloading a playlist. Also trigger on "下载视频", "保存视频", "提取音频", or any URL from a supported video platform.
---

# Download Video

Download videos from YouTube, Bilibili, Twitter/X, TikTok, and 1000+ other sites using yt-dlp.

## Step 1: Check prerequisites

```bash
which yt-dlp && yt-dlp --version
which ffmpeg && which ffprobe
which deno && deno --version
```

Use Python 3.11 or newer. Install or update the stable Python dependencies in the active virtual environment (`<skill_directory>` is this skill's directory):

```bash
python -m pip install --upgrade -r <skill_directory>/requirements.txt

# macOS: install external tools (use brew upgrade if already installed)
brew install ffmpeg deno
```

The dependency file includes yt-dlp's default extras, including the EJS challenge solver. Deno is needed for full YouTube support. Keep the virtual environment active so the bundled script invokes the updated `yt-dlp` executable. See the [official EJS guide](https://github.com/yt-dlp/yt-dlp/wiki/EJS) for other JavaScript runtimes.

## Step 2: Download

Use the bundled script — it wraps yt-dlp with sensible defaults and clear error messages.

```bash
python3 scripts/download.py "VIDEO_URL"
```

Default output: `~/Downloads/Videos/`

### Common options

```bash
python3 scripts/download.py "URL" -f 1080            # Max 1080p
python3 scripts/download.py "URL" -a                  # Audio only (MP3)
python3 scripts/download.py "URL" -F                  # List formats
python3 scripts/download.py "URL" --subs              # With subtitles
python3 scripts/download.py "URL" -o ~/Desktop        # Custom output dir
python3 scripts/download.py "URL" --cookies chrome    # Use browser cookies
```

### Direct yt-dlp commands

For cases the script doesn't cover, use yt-dlp directly:

```bash
# Download playlist
yt-dlp -P ~/Downloads/Videos "PLAYLIST_URL"

# Custom filename template
yt-dlp -o "%(uploader)s - %(title)s.%(ext)s" "VIDEO_URL"

# Download with subtitles in specific languages
yt-dlp --write-subs --sub-lang zh,en -P ~/Downloads/Videos "VIDEO_URL"
```

## Troubleshooting

Most download failures fall into these categories:

| Symptom | Fix |
|---------|-----|
| "Sign in required" or age-restricted | Add `--cookies chrome` to use browser session |
| Only low quality available | Update yt-dlp (`brew upgrade yt-dlp`), then try with `--cookies chrome` |
| Slow downloads | Try `--concurrent-fragments 3` or `--downloader aria2c` |
| Network errors (behind firewall) | Use `--proxy socks5://127.0.0.1:1080` or set `ALL_PROXY` env var |

For platform-specific details (YouTube PO tokens, Bilibili series, TikTok watermark removal, etc.), see [references/platform-tips.md](references/platform-tips.md).
