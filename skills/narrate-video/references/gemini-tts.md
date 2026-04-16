# Gemini 3.1 Flash TTS Reference

Last checked against Google AI for Developers docs updated **2026-04-15 UTC**.

## AI Studio / Gemini API request shape

Google AI Studio's Gemini TTS uses the same public Gemini API pattern:

- **Model**: `gemini-3.1-flash-tts-preview`
- **Endpoint**: `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-tts-preview:generateContent`
- **Auth header**: `x-goog-api-key: $GEMINI_API_KEY`
- **Response modality**: `"AUDIO"`
- **Voice config path**: `generationConfig.speechConfig.voiceConfig.prebuiltVoiceConfig.voiceName`
- **Audio payload path**: `candidates[0].content.parts[0].inlineData.data`

Minimal REST payload:

```json
{
  "contents": [{
    "parts": [{
      "text": "Generate speech audio only. Read the transcript below aloud exactly as written.\n\nTRANSCRIPT:\nHello world."
    }]
  }],
  "generationConfig": {
    "responseModalities": ["AUDIO"],
    "speechConfig": {
      "voiceConfig": {
        "prebuiltVoiceConfig": {
          "voiceName": "Kore"
        }
      }
    }
  },
  "model": "gemini-3.1-flash-tts-preview"
}
```

## Audio format

The REST response returns base64-encoded raw PCM:

- 16-bit signed little-endian (`s16le`)
- 24 kHz sample rate
- mono

To convert raw PCM to WAV with `ffmpeg`:

```bash
ffmpeg -f s16le -ar 24000 -ac 1 -i out.pcm out.wav
```

The bundled template writes WAV directly from PCM bytes, so you do not need a separate conversion step.

## Known Gemini 3.1 Flash TTS caveats

- **Preview model**: treat it as less stable than Azure.
- **Transient `500` errors**: official docs note that the model can occasionally return text tokens instead of audio, so retry automatically.
- **Prompt classifier false rejections**: vague prompts can be rejected or read aloud. Use an explicit speech-only preamble and clearly label the actual transcript.
- **Voice mismatch**: choose a voice whose style matches the transcript tone; the docs explicitly warn that mismatched persona and transcript can sound wrong.

## Supported alternatives

The official TTS docs also list these TTS-capable models:

- `gemini-2.5-flash-preview-tts`
- `gemini-2.5-pro-preview-tts`

Keep the skill default on `gemini-3.1-flash-tts-preview` unless the user explicitly wants a different Gemini TTS model.
