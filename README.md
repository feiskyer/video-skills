# video-skills

Skills for working with videos - download, transcribe, and narrate.

## Install and upgrade

Plugin installation is recommended for both Claude Code and Codex. Run the following commands in your terminal.

### Claude Code (recommended)

Install:

```bash
claude plugin marketplace add feiskyer/video-skills
claude plugin install video-skills@video-skills
```

Upgrade:

```bash
claude plugin marketplace update video-skills
claude plugin update video-skills@video-skills
```

Restart Claude Code after installing or upgrading. See the [Claude Code plugin documentation](https://code.claude.com/docs/en/discover-plugins).

### Codex (recommended)

Install:

```bash
codex plugin marketplace add feiskyer/video-skills
codex plugin add video-skills@video-skills
```

Upgrade:

```bash
codex plugin marketplace upgrade video-skills
codex plugin add video-skills@video-skills
```

The upgrade commands refresh the marketplace checkout and install its current plugin version. Start a new Codex session after installing or upgrading. These commands are verified with Codex CLI 0.167.0; use a current CLI with `codex plugin` support.

Codex uses the root `plugin.json` and `.agents/plugins/marketplace.json`; Claude Code uses `.claude-plugin/`. Both packages include the same `skills/` directory. See the [OpenAI plugin packaging documentation](https://developers.openai.com/plugins/build/plugins).

### Skill-only installation (alternative)

For other agents or when you only want the skill files:

```bash
npx skills add feiskyer/video-skills
```

## Dependencies

Plugin installation does not install Python packages or external executables. Each skill includes its dependency setup instructions. Use Python 3.11 or newer; from a local checkout of this repository, install the tested stable dependencies in an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade -r requirements.txt
```

The per-skill `requirements.txt` files also work when a skill is installed on its own. Direct Python dependencies are pinned to stable releases verified on 2026-11-09: yt-dlp 2026.10.26 (including its default EJS dependencies), OpenAI 3.46.0, python-dotenv 1.2.4, and Azure Speech SDK 1.53.0.

FFmpeg and ffprobe are external executables. YouTube downloads also require a supported JavaScript runtime; Deno is recommended. The tested stable versions are FFmpeg 9.0.2 and Deno 2.9.8. On macOS:

```bash
brew install ffmpeg deno
# If already installed:
brew upgrade ffmpeg deno
```

These are library/tool versions. Existing transcription deployments, API versions, and the optional Gemini preview model are configured separately and are not changed by installing dependencies.

## Skills

### download-video

Download videos from YouTube, Bilibili, Twitter/X, TikTok, and 1000+ other sites.

**Setup:**

```bash
python -m pip install --upgrade -r skills/download-video/requirements.txt
brew install ffmpeg deno
```

**Usage:**

```md
"Download this video: https://youtube.com/watch?v=..."
"Download audio only from https://youtu.be/..."
"Download this video in 1080p: https://bilibili.com/video/BV..."
```

### transcribe-video

Extract transcript from local video files. Checks for embedded subtitles first, falls back to API-based speech recognition.

**Setup:**

```bash
python -m pip install --upgrade -r skills/transcribe-video/requirements.txt
```

Create `~/.transcribe_video.env`:

```sh
OPENAI_API_KEY=your-key-here
# OPENAI_API_BASE=https://<base-url>/v1/      # Optional Base URL
# TRANSCRIBE_MODEL=gpt-4o-transcribe-diarize  # Optional Model Name
```

**Usage:**

```sh
"Transcribe ~/Downloads/meeting.mp4"
"Extract subtitles from ~/Desktop/lecture.mkv"
"把这个视频转成文字: ~/Downloads/demo.mov"
```

### narrate-video

Generate professional voiceover narration with Azure TTS by default, or Gemini 3.1 Flash TTS when configured. The skill analyzes video scenes, writes a timed script, and produces a narrated video with audio-video sync.

**Setup:**

```bash
python -m pip install --upgrade -r skills/narrate-video/requirements.txt
```

Create `~/.narrate_video.env`:

```sh
# Azure provider (default)
AZURE_SPEECH_KEY=your-key-here
AZURE_SPEECH_REGION=your-region-here

# Gemini provider (optional)
# GEMINI_API_KEY=your-key-here
# GEMINI_TTS_MODEL=gemini-3.1-flash-tts-preview
```

Notes:

- `azure` is still the default provider.
- To use Gemini, add `GEMINI_API_KEY` and set `TTS_PROVIDER = "gemini"` in the generated `narration_script.py`.
- Gemini uses the official Google AI Studio / Gemini API TTS flow with model `gemini-3.1-flash-tts-preview`.

**Usage:**

```md
"Add voiceover narration to ~/Desktop/demo.mov"
"给这个录屏加上中文旁白: ~/Downloads/screen-recording.mp4"
"Narrate this tutorial video in English: ~/Desktop/tutorial.mov"
"Use Gemini TTS to narrate ~/Desktop/tutorial.mov with a warm voice"
```

## License

[MIT](LICENSE)
