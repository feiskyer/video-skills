# video-skills

Skills for working with videos - download, transcribe, and narrate.

[![Try video-skills on Socialistic](https://socialistic.ai/api/embed/video-skills-b768c1)](https://socialistic.ai/en/skill/video-skills-b768c1?utm_source=github&utm_medium=issue&utm_campaign=20260522-zhihu-indie-cc-devs&utm_content=badge)

## Install

### Option 1: Claude Code plugin commands

```bash
/plugin marketplace add feiskyer/video-skills
/plugin install video-skills@video-skills
```

### Option 2: npx skills

```bash
npx skills add feiskyer/video-skills
```

## Skills

### download-video

Download videos from YouTube, Bilibili, Twitter/X, TikTok, and 1000+ other sites.

**Setup:**

```bash
brew install yt-dlp ffmpeg
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
pip install openai python-dotenv
```

Create `~/.transcribe_video.env`:

```sh
OPENAI_API_KEY=your-key-here
# OPENAI_API_BASE=https://<base-url>/v1/      # Optional Base URL
# TRANSCRIBE_MODEL=gpt-4o-transcribe-diarize. # Optional Model Name
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
pip install python-dotenv

# Azure provider only
pip install azure-cognitiveservices-speech
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
