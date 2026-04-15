# video-skills

Skills for working with videos - download, transcribe, and narrate.

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

Generate professional voiceover narration with Azure TTS. Analyzes video scenes, writes a timed script, and produces a narrated video with audio-video sync.

**Setup:**

```bash
pip install azure-cognitiveservices-speech python-dotenv
```

Create `~/.narrate_video.env`:

```sh
AZURE_SPEECH_KEY=your-key-here
AZURE_SPEECH_REGION=your-region-here
```

**Usage:**

```md
"Add voiceover narration to ~/Desktop/demo.mov"
"给这个录屏加上中文旁白: ~/Downloads/screen-recording.mp4"
"Narrate this tutorial video in English: ~/Desktop/tutorial.mov"
```

## License

[MIT](LICENSE)
