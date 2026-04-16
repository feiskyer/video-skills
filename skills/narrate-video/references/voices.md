# TTS Voice Reference

## Provider overview

- `azure` is the default provider. It uses language-specific Azure Neural voices.
- `gemini` uses `gemini-3.1-flash-tts-preview` and AI Studio's prebuilt voice library. Gemini voices are style-based rather than language-specific.

## Azure: recommended voices by language

| Language | Voice Name |
|----------|------------|
| English | `en-US-AndrewMultilingualNeural` |
| Chinese (Mandarin) | `zh-CN-YunxiMultilingualNeural` |
| Japanese | `ja-JP-MasaruMultilingualNeural` |
| Korean | `ko-KR-HyunsuMultilingualNeural` |
| French | `fr-FR-VivienneMultilingualNeural` |
| German | `de-DE-FlorianMultilingualNeural` |
| Spanish | `es-ES-XimenaMultilingualNeural` |

For unlisted languages, prefer Azure `MultilingualNeural` voices first, then the best available `Neural` voice.

## Gemini: recommended voices by style

These are the same `voiceName` values exposed in Google AI Studio's Gemini TTS voice library.

| Use case | Voice Name | Style |
|----------|------------|-------|
| Neutral product demo | `Kore` | Firm |
| Friendly walkthrough | `Achird` | Friendly |
| Upbeat promo | `Puck` | Upbeat |
| Calm explainer | `Umbriel` | Easy-going |
| Warm narration | `Sulafat` | Warm |
| Breezy social clip | `Aoede` | Breezy |
| Mature documentary tone | `Gacrux` | Mature |
| Clear instructional read | `Iapetus` | Clear |

Other commonly useful Gemini voices: `Charon`, `Fenrir`, `Leda`, `Orus`, `Autonoe`, `Enceladus`, `Despina`, `Erinome`, `Achernar`, `Pulcherrima`, `Vindemiatrix`, `Sadachbia`, `Sadaltager`.

## Timing estimates for segment planning

Use these rates to estimate whether a segment will fit inside its window. These are planning estimates, not guarantees.

| Language | Approx Rate | Unit |
|----------|-------------|------|
| English | ~150 | words/min |
| Chinese (Mandarin) | ~250 | chars/min |
| Japanese | ~350 | chars/min |
| Korean | ~300 | chars/min |
| French | ~150 | words/min |
| German | ~140 | words/min |
| Spanish | ~160 | words/min |

```
speech_rate_per_second = speech_rate_per_minute / 60
max_units = time_window_seconds * speech_rate_per_second * 0.8
```

Examples:
- English: a 10-second window fits about `10 * 2.5 * 0.8 = 20` words.
- Chinese: a 10-second window fits about `10 * 4.2 * 0.8 = 33` characters.
