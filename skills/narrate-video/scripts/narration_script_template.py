#!/usr/bin/env python3
"""Video Narration - TTS Generation and Video Assembly

This script generates TTS audio segments using Azure Speech SDK or Gemini TTS,
positions them at specified timestamps, and merges them onto a video.

Usage:
    1. Fill in TTS_PROVIDER, VOICE_NAME, INPUT_VIDEO, OUTPUT_VIDEO, and SEGMENTS
    2. Ensure the matching provider credentials exist in ~/.narrate_video.env
    3. Run: python3 narration_script.py
"""

import base64
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
import wave

from dotenv import load_dotenv

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    speechsdk = None

load_dotenv(os.path.expanduser("~/.narrate_video.env"))

# ── Configuration ──────────────────────────────────────────────────────────
TTS_PROVIDER = "azure"                    # "azure" or "gemini"
SPEECH_KEY = os.environ.get("AZURE_SPEECH_KEY", "")
SERVICE_REGION = os.environ.get("AZURE_SPEECH_REGION", "eastus2")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_TTS_MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.1-flash-tts-preview")
GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_TTS_MODEL}:generateContent"
)
GEMINI_PCM_RATE = 24000
GEMINI_PCM_CHANNELS = 1
GEMINI_SAMPLE_WIDTH = 2
GEMINI_MAX_RETRIES = 3
VOICE_NAME = "REPLACE_WITH_VOICE"         # Azure: en-US-AndrewMultilingualNeural; Gemini: Kore
INPUT_VIDEO = "REPLACE_WITH_INPUT"        # Relative path only
OUTPUT_VIDEO = "REPLACE_WITH_OUTPUT"      # Relative path only
SEGMENTS_DIR = "narration_segments"       # Relative path only

# ── Narration Segments ─────────────────────────────────────────────────────
# Each entry: (start_seconds, "narration text")
# Fill from Phase 2 script writing
SEGMENTS = []


# ── TTS Generation ─────────────────────────────────────────────────────────
def segment_output_path(idx):
    """Pick a stable cache file extension for the active provider."""
    extension = "mp3" if TTS_PROVIDER == "azure" else "wav"
    return os.path.join(SEGMENTS_DIR, f"seg_{idx:03d}.{extension}")


def generate_segment_azure(idx, text, output_path):
    """Generate a single audio segment using Azure TTS."""
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SERVICE_REGION)
    speech_config.speech_synthesis_voice_name = VOICE_NAME
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )
    result = synthesizer.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"  [OK] Segment {idx}: {output_path}")
        return True
    details = result.cancellation_details
    print(f"  [FAIL] Segment {idx}: {details.reason} - {details.error_details}")
    return False


def write_wave_file(filename, pcm_data):
    """Persist Gemini PCM audio as a WAV file."""
    with wave.open(filename, "wb") as wav_file:
        wav_file.setnchannels(GEMINI_PCM_CHANNELS)
        wav_file.setsampwidth(GEMINI_SAMPLE_WIDTH)
        wav_file.setframerate(GEMINI_PCM_RATE)
        wav_file.writeframes(pcm_data)


def build_gemini_prompt(text):
    """Wrap transcript text so Gemini reliably emits audio instead of reading metadata."""
    return (
        "Generate speech audio only. Speak the transcript below naturally. "
        "Do not read headings, labels, or instructions aloud. "
        "Treat bracketed audio tags such as [whispers] or [excitedly] as delivery "
        "instructions rather than spoken words.\n\n"
        "TRANSCRIPT:\n"
        f"{text}"
    )


def extract_gemini_audio(response_body):
    """Extract inline base64 audio from Gemini's generateContent response."""
    candidates = response_body.get("candidates", [])
    if not candidates:
        return None
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        return None
    inline_data = parts[0].get("inlineData", {})
    return inline_data.get("data")


def generate_segment_gemini(idx, text, output_path):
    """Generate a single audio segment using Gemini 3.1 Flash TTS."""
    payload = {
        "contents": [{
            "parts": [{
                "text": build_gemini_prompt(text),
            }]
        }],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": VOICE_NAME,
                    }
                }
            }
        },
        "model": GEMINI_TTS_MODEL,
    }
    request = urllib.request.Request(
        GEMINI_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY,
        },
        method="POST",
    )

    for attempt in range(1, GEMINI_MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                response_body = json.loads(response.read().decode("utf-8"))
            audio_data = extract_gemini_audio(response_body)
            if not audio_data:
                raise RuntimeError("Gemini response did not include inline audio data")
            pcm_data = base64.b64decode(audio_data)
            write_wave_file(output_path, pcm_data)
            print(f"  [OK] Segment {idx}: {output_path}")
            return True
        except urllib.error.HTTPError as exc:
            status = exc.code
            body = exc.read().decode("utf-8", errors="replace")
            should_retry = status in {429, 500, 502, 503, 504}
            if attempt < GEMINI_MAX_RETRIES and should_retry:
                print(
                    f"  [RETRY] Segment {idx}: Gemini HTTP {status} on attempt "
                    f"{attempt}/{GEMINI_MAX_RETRIES}"
                )
                time.sleep(attempt)
                continue
            print(f"  [FAIL] Segment {idx}: Gemini HTTP {status} - {body[:500]}")
            return False
        except Exception as exc:
            if attempt < GEMINI_MAX_RETRIES:
                print(
                    f"  [RETRY] Segment {idx}: {exc} "
                    f"({attempt}/{GEMINI_MAX_RETRIES})"
                )
                time.sleep(attempt)
                continue
            print(f"  [FAIL] Segment {idx}: {exc}")
            return False

    return False


def generate_segment(idx, text, output_path):
    """Dispatch segment generation to the configured provider."""
    if TTS_PROVIDER == "azure":
        return generate_segment_azure(idx, text, output_path)
    if TTS_PROVIDER == "gemini":
        return generate_segment_gemini(idx, text, output_path)
    raise ValueError(f"Unsupported TTS_PROVIDER: {TTS_PROVIDER}")


def get_audio_duration(path):
    """Get duration of an audio file in seconds via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path],
        capture_output=True, text=True
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def build_narrated_video():
    """Generate TTS segments, check timing, and assemble the narrated video."""
    os.makedirs(SEGMENTS_DIR, exist_ok=True)

    # Step 1: Generate audio segments (skips existing files)
    print("=== Step 1: Generating audio segments ===")
    segment_files = []
    for i, (start, text) in enumerate(SEGMENTS):
        out_path = segment_output_path(i)
        if not os.path.exists(out_path):
            if not generate_segment(i, text, out_path):
                return False
        else:
            print(f"  [SKIP] Segment {i}: already exists")
        segment_files.append((start, out_path))

    # Step 2: Get video duration
    video_duration = float(json.loads(subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", INPUT_VIDEO],
        capture_output=True, text=True
    ).stdout)["format"]["duration"])
    print(f"\nVideo duration: {video_duration:.1f}s")

    # Step 3: Check timing overlaps — abort on any overlap
    print("\n=== Step 2: Checking segment timings ===")
    has_overlap = False
    for i, (start, path) in enumerate(segment_files):
        dur = get_audio_duration(path)
        end = start + dur
        next_start = segment_files[i + 1][0] if i + 1 < len(segment_files) else video_duration
        gap = next_start - end
        status = "OK" if gap >= 0 else "OVERLAP"
        print(f"  Seg {i:2d}: {start:6.1f}s - {end:6.1f}s (dur: {dur:5.1f}s) gap: {gap:+.1f}s [{status}]")
        if gap < 0:
            has_overlap = True
            print(f"    WARNING: Overlap of {-gap:.1f}s with next segment!")
    if has_overlap:
        print("\nERROR: Fix overlaps before proceeding.")
        return False

    # Step 4: Build ffmpeg command
    print("\n=== Step 3: Building narrated video ===")
    inputs = ["-i", INPUT_VIDEO]
    for _, path in segment_files:
        inputs.extend(["-i", path])

    filter_parts = []
    n = len(segment_files)
    for i, (start, _) in enumerate(segment_files):
        delay_ms = int(start * 1000)
        filter_parts.append(f"[{i+1}:a]adelay={delay_ms}|{delay_ms}[a{i}]")

    # normalize=0 is essential: without it, amix divides volume by input count,
    # so 20 segments would reduce audio to 1/20th volume — nearly silent.
    mix_inputs = "".join(f"[a{i}]" for i in range(n))
    filter_parts.append(
        f"{mix_inputs}amix=inputs={n}:duration=longest"
        f":dropout_transition=0:normalize=0[final]"
    )

    # Original video audio is completely discarded — only the narration track
    # is mapped. Mixing original audio even at low volume causes audible
    # double-voice artifacts because the narration bleeds through both tracks.
    filter_complex = ";".join(filter_parts)
    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[final]",
        "-c:v", "copy",       # Copy video without re-encoding
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        OUTPUT_VIDEO
    ]

    print("  Running ffmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ffmpeg error:\n{result.stderr[-2000:]}")
        return False

    print(f"\n=== Done! Output: {OUTPUT_VIDEO} ===")
    return True


def check_inputs():
    """Validate all required configuration before running."""
    errors = []
    if TTS_PROVIDER not in {"azure", "gemini"}:
        errors.append('TTS_PROVIDER must be "azure" or "gemini"')
    if TTS_PROVIDER == "azure":
        if not SPEECH_KEY:
            errors.append("AZURE_SPEECH_KEY not found. Add it to ~/.narrate_video.env")
        if not os.environ.get("AZURE_SPEECH_REGION"):
            errors.append("AZURE_SPEECH_REGION not found. Add it to ~/.narrate_video.env")
        if speechsdk is None:
            errors.append(
                "azure.cognitiveservices.speech is not installed. "
                "Install it or switch TTS_PROVIDER to gemini"
            )
    if TTS_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY not found. Add it to ~/.narrate_video.env")
        if not GEMINI_TTS_MODEL:
            errors.append("GEMINI_TTS_MODEL is empty. Set it or remove the override")
    if VOICE_NAME == "REPLACE_WITH_VOICE":
        if TTS_PROVIDER == "gemini":
            errors.append("VOICE_NAME not set. Replace the placeholder with a Gemini voice (e.g. Kore)")
        else:
            errors.append(
                "VOICE_NAME not set. Replace the placeholder with an Azure voice "
                "(e.g. en-US-AndrewMultilingualNeural)"
            )
    if INPUT_VIDEO == "REPLACE_WITH_INPUT":
        errors.append("INPUT_VIDEO not set. Replace the placeholder with the input video path")
    elif not os.path.isfile(INPUT_VIDEO):
        errors.append(f"INPUT_VIDEO not found: {INPUT_VIDEO}")
    if OUTPUT_VIDEO == "REPLACE_WITH_OUTPUT":
        errors.append("OUTPUT_VIDEO not set. Replace the placeholder with the output video path")
    if not SEGMENTS:
        errors.append("SEGMENTS is empty. Add at least one (start_seconds, text) tuple")
    for i, seg in enumerate(SEGMENTS):
        if not isinstance(seg, (list, tuple)) or len(seg) != 2:
            errors.append(f"SEGMENTS[{i}]: must be a (start_seconds, text) tuple")
        elif not isinstance(seg[0], (int, float)) or seg[0] < 0:
            errors.append(f"SEGMENTS[{i}]: start_seconds must be a non-negative number")
        elif not isinstance(seg[1], str) or not seg[1].strip():
            errors.append(f"SEGMENTS[{i}]: text must be a non-empty string")
    for i in range(1, len(SEGMENTS)):
        if SEGMENTS[i][0] < SEGMENTS[i - 1][0]:
            errors.append("SEGMENTS must be sorted by ascending start_seconds")
            break
    if errors:
        print("ERROR: Fix the following before running:\n")
        for e in errors:
            print(f"  - {e}")
        return False
    return True


if __name__ == "__main__":
    if not check_inputs():
        exit(1)
    build_narrated_video()
