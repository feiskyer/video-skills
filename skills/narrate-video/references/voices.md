# TTS Voice Reference

## Provider overview

- `azure` is the default provider. English narration defaults to `en-US-Jimmie:DragonHDFlashLatestNeural`; all other narration defaults to `zh-CN-Yunxiao:DragonHDFlashLatestNeural`.
- `gemini` uses `gemini-3.1-flash-tts-preview` and AI Studio's prebuilt voice library. Gemini voices are style-based rather than language-specific.

## Azure: default voices

Select by the actual narration language. Use Jimmie for English and Yunxiao otherwise, including mixed Chinese and English. An explicit user voice choice overrides this rule.

| Narration | Voice Name |
|-----------|------------|
| English | `en-US-Jimmie:DragonHDFlashLatestNeural` |
| Other | `zh-CN-Yunxiao:DragonHDFlashLatestNeural` |

HD Flash supports Chinese and English text. The non-English default is a selection policy, not a guarantee of support for other languages; for unsupported text, explain the limitation before synthesis rather than silently translating or substituting voices.

## Azure: optional voices for explicit language-specific requests

These alternatives do not replace the default selection rule above.

| Language | Voice Name |
|----------|------------|
| Japanese | `ja-JP-MasaruMultilingualNeural` |
| Korean | `ko-KR-HyunsuMultilingualNeural` |
| French | `fr-FR-VivienneMultilingualNeural` |
| German | `de-DE-FlorianMultilingualNeural` |
| Spanish | `es-ES-XimenaMultilingualNeural` |

For an explicit request for another unlisted language, prefer Azure `MultilingualNeural` voices first, then the best available `Neural` voice.

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
