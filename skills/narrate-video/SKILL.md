---
name: narrate-video
description: Generate professional voiceover narration for a video with audio-video sync using Azure TTS by default, or Gemini 3.1 Flash TTS when configured. Use this skill whenever the user wants to add narration, voiceover, commentary, or voice dubbing to any video file — even if they just say "add audio to this video" or "make a narrated version." Also trigger when the user has a screen recording, demo, tutorial, or presentation video that needs a voice track. Trigger on Chinese requests like "视频配音", "给视频加旁白", "录屏解说", "视频加语音", "视频添加声音", "生成视频旁白", "自动配音", "视频解说词".
---

# Video Narration

Add professional voiceover to a video. Analyze the video, write or refine a timed script, generate speech via Azure TTS or Gemini 3.1 Flash TTS, and merge — producing a narrated video where audio and visuals stay in sync.

**Input**: $ARGUMENTS

## Additional resources

- Voice table and timing estimates: [references/voices.md](references/voices.md)
- Gemini TTS API and AI Studio request shape: [references/gemini-tts.md](references/gemini-tts.md)
- Python script template: [scripts/narration_script_template.py](scripts/narration_script_template.py) — copy into the video's directory as `narration_script.py` and fill in the placeholders

---

## Phase 0: Setup

### Provider

Default to `azure` unless the user explicitly asks for Gemini or already has `GEMINI_API_KEY` configured. When using Gemini, use the official Gemini TTS request pattern documented in [references/gemini-tts.md](references/gemini-tts.md).

### Language

Ask the user which language they want. Default to **English**. Look up the voice and speech rate in [references/voices.md](references/voices.md).

### Environment

```bash
# 1. Check provider credentials exist (NEVER read or display their values)
scripts/check_env.py azure
# or
scripts/check_env.py gemini

# 2. Check tool dependencies
command -v ffmpeg && command -v ffprobe && command -v python3

# 3. Check Python dependencies
python3 -c "import dotenv" 2>&1

# 4. Azure only
python3 -c "import azure.cognitiveservices.speech" 2>&1
```

If Azure is selected and `AZURE_SPEECH_KEY` or `AZURE_SPEECH_REGION` is missing, ask the user to add them to `~/.narrate_video.env`:

```
AZURE_SPEECH_KEY=your-key-here
AZURE_SPEECH_REGION=your-region-here
```

If Gemini is selected and `GEMINI_API_KEY` is missing, ask the user to add it to `~/.narrate_video.env`:

```
GEMINI_API_KEY=your-key-here
# Optional override
GEMINI_TTS_MODEL=gemini-3.1-flash-tts-preview
```

Then stop — the key is sensitive, only check whether it exists, never read or display its value.

---

## Phase 1: Video Analysis

### 1.1 Metadata

```bash
ffprobe -v quiet -print_format json -show_format -show_streams <video>
```

Record total duration, resolution, frame rate, and whether an audio track exists.

### 1.2 Scene extraction

Extract frames at 3–4 second intervals to identify scene transitions:

```bash
mkdir -p /tmp/narration-frames
for t in $(seq 0 3 <duration>); do
    ffmpeg -y -ss $t -i <video> -frames:v 1 -q:v 2 /tmp/narration-frames/frame_${t}s.jpg 2>/dev/null
done
```

Review the frames (use Read tool to view images). For each scene transition, note the precise timestamp. Where timing is ambiguous, extract additional frames at 1–2 second intervals to pinpoint the exact moment.

### 1.3 Transition map

Build a scene transition table mapping timestamps to visual content:

```
0s   - Opening screen
3s   - User starts typing
8s   - System begins processing
34s  - Response appears
```

Narration describing something on screen should start *after* that content is already visible. Viewers notice when audio arrives before the visuals — it feels disorienting. Narrating slightly after the visual appears feels natural, like a presenter walking you through what you're seeing.

---

## Phase 2: Script Writing

### Format

Each narration segment is a `(start_seconds, text)` tuple:

```python
SEGMENTS = [
    (0, "Opening narration here."),
    (8, "Next segment narration..."),
]
```

### Writing guidance

**Timing**: Leave at least 1 second of silence between segments — this breathing room makes narration feel conversational rather than rushed. Use the timing estimates from [references/voices.md](references/voices.md) to estimate whether text fits: for English, multiply the window (in seconds) by 2.5 words/sec, then take 80% as the safe word count.

**Flow**: Each segment should connect logically to the next. Transition words ("And", "Now", "So") help, but vary them — three consecutive "And now" transitions sound robotic.

**Adapting to input**: If the user provided a draft, calibrate its timestamps against the scene analysis, trim text that overflows its time window, and polish the language — but preserve their intent and key points. Without a draft, write narration for each scene based on what's visible.

**Gemini prompt hygiene**: If using Gemini, keep style instructions separate from the spoken transcript. The script template already wraps text in a safe `TRANSCRIPT:` preamble because Gemini 3.1 Flash TTS can occasionally read metadata aloud or reject vague prompts.

### Pre-flight check

Before generating audio, verify each segment fits:

```
window = next_segment_start - this_segment_start
max_words = window * words_per_second * 0.8
```

If a segment is too long, shorten the text now — trimming words is much cheaper than regenerating audio.

---

## Phase 3: Generate the Script

Copy [scripts/narration_script_template.py](scripts/narration_script_template.py) into the video's directory as `narration_script.py`. Fill in:
- `TTS_PROVIDER` as `azure` or `gemini`
- `VOICE_NAME` from the provider-specific table
- `INPUT_VIDEO` and `OUTPUT_VIDEO` (relative paths only)
- `SEGMENTS` from Phase 2

### Design notes

These choices come from debugging real production issues:

- **`normalize=0` on amix**: ffmpeg's `amix` divides volume by input count by default. With 20 segments, output would be 1/20th volume — essentially silent.
- **Discarding original audio**: Even mixing original audio at 5% volume produces audible double-voice artifacts.
- **Aborting on overlap**: If any segment's audio extends past the next segment's start time, the script stops and reports the problem. Overlapping audio sounds broken.
- **Skipping existing audio files**: The script only generates audio for segments without an existing cached file. Azure uses `.mp3`; Gemini uses `.wav`. If you change a segment's text, delete the matching `seg_XXX.*` file before re-running.
- **Gemini retry logic**: Gemini 3.1 Flash TTS can occasionally return transient `500` errors. The template retries a few times automatically before failing.

---

## Phase 4: Run & Iterate

```bash
python3 narration_script.py
```

If the timing report shows overlaps (gap < 0), decide whether to shorten the text or push the next segment's start time later. If you change text, delete the corresponding cached audio file in `narration_segments/` first. If you only change start times, re-run directly.

Keep iterating until all gaps are non-negative.

---

## Phase 5: Verification

Run all three checks after every successful build:

### Volume

```bash
ffmpeg -i <output> -ss 0 -t 30 -af "volumedetect" -vn -f null - 2>&1 | grep -E "mean_volume|max_volume"
```

Expect mean_volume between -25 and -15 dB, max between -10 and 0 dB. If mean is below -40 dB, the `normalize=0` fix isn't applied — check the filter string.

### Silence gaps

```bash
ffmpeg -i <output> -af "silencedetect=noise=-30dB:d=0.3" -vn -f null - 2>&1 | grep -E "silence_(start|end)" | head -20
```

Confirm clean silence between segment transitions. Silence boundaries should match expected segment end/start times.

### Audio-video sync

Extract frames at 5–8 key segment start times and view them:

```bash
for t in <timestamps>; do
    ffmpeg -y -ss $t -i <output> -frames:v 1 -q:v 2 /tmp/verify_${t}s.jpg 2>/dev/null
done
```

The on-screen content should already be visible when the narration for that scene begins.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Two voices playing | Original audio was mixed in | Only map `[final]` audio track, never `0:a` |
| Audio nearly silent | amix divided volume by input count | Add `:normalize=0` to amix parameters |
| Narration out of sync | Imprecise scene timestamps | Re-extract frames at 1–2s intervals around the problem area |
| Overlap at segment boundary | Previous segment runs too long | Shorten that segment's text or delay the next segment |
| Text changed but audio didn't | Old cached audio file still exists | Delete `narration_segments/seg_XXX.*` and re-run |
| Audio cut off at video end | Last segment overflows video duration | Shorten to finish 3–4s before video ends |
| Gemini returns `500` | Preview model emitted text tokens instead of audio | Re-run; the template already retries transient failures |
| Gemini reads prompt labels aloud | Prompt classifier failed or prompt was too vague | Keep the transcript explicit and use the template's `TRANSCRIPT:` wrapper |
