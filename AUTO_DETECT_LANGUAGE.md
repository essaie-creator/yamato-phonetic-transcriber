# Automatic Language Detection

The Yamato Phonetic Transcriber now supports **automatic language detection** from audio files. You no longer need to manually select the language before transcribing audio.

## How It Works

When you enable auto-detection mode, the transcriber:

1. **Analyzes the audio** using SpeechBrain's language identification model
2. **Detects the spoken language** (English, Spanish, French, Japanese, or Haitian Creole)
3. **Automatically selects** the appropriate ASR model for that language
4. **Transcribes and phonemizes** the audio with optimal settings

## Usage

### Command Line

```bash
# Auto-detect language (default behavior)
python transcribe.py --audio speech.wav

# Auto-detect with explicit flag
python transcribe.py --audio speech.wav --lang auto

# Manually specify language (disables auto-detection)
python transcribe.py --audio speech.wav --lang en
```

When auto-detection is enabled, the output includes the detected language:
```
[Detected Language: es] ˈola ˈkom.o esˈtas
```

### Python API

```python
from yamato_transcriber import PhoneticTranscriber

# Enable auto-detection at initialization
transcriber = PhoneticTranscriber(
    language='en',  # Default fallback
    auto_detect_language=True
)

# Transcribe with auto-detection
phonemes, detected_lang = transcriber.audio_to_phonemes('speech.wav')
print(f"Language: {detected_lang}")
print(f"Phonemes: {phonemes}")

# Or override per-call
phonemes, detected_lang = transcriber.audio_to_phonemes(
    'speech.wav',
    detect_language=True  # Override instance setting
)
```

### GUI

In the graphical interface:
1. Open an audio file
2. Select **"Auto"** from the language dropdown (or leave default)
3. Click **Transcribe**
4. The detected language will be shown in the output

## Supported Languages

The auto-detection system supports:

| Code | Language       | Native Name     |
|------|---------------|-----------------|
| en   | English       | English         |
| es   | Spanish       | Español         |
| fr   | French        | Français        |
| ja   | Japanese      | 日本語           |
| ht   | Haitian Creole| Kreyòl Ayisyen  |

## Technical Details

### Language Identification Model

The system uses SpeechBrain's `lang-id-commonlanguage_ecapa` model:
- Lightweight and fast
- Trained on multiple languages
- Runs locally (no internet required after first download)

### Fallback Behavior

If language detection fails:
- Falls back to the default language (English)
- Logs a warning message
- Continues transcription without interruption

### Performance

- Detection adds ~1-2 seconds to transcription time
- Model is cached after first use
- Can be disabled for known-language audio for faster processing

## Examples

### Batch Processing with Auto-Detection

```python
from pathlib import Path
from yamato_transcriber import PhoneticTranscriber

transcriber = PhoneticTranscriber(auto_detect_language=True)

audio_files = list(Path('recordings').glob('*.wav'))

for audio_file in audio_files:
    phonemes, lang = transcriber.audio_to_phonemes(audio_file)
    print(f"{audio_file.name}: [{lang}] {phonemes}")
```

### Compare Manual vs Auto

```python
# Manual (faster if you know the language)
transcriber_manual = PhoneticTranscriber(language='es')
phonemes, _ = transcriber_manual.audio_to_phonemes('spanish.wav')

# Auto-detection (convenient for unknown sources)
transcriber_auto = PhoneticTranscriber(auto_detect_language=True)
phonemes, detected = transcriber_auto.audio_to_phonemes('unknown.wav')
```

## Troubleshooting

### Detection Seems Wrong

- Ensure audio has clear speech (at least 3-5 seconds)
- Background noise can affect accuracy
- Try with `--no-low-resource` for better models

### Unsupported Language Detected

If the detected language isn't supported:
- System falls back to English ASR
- Warning message is logged
- Consider manually specifying the closest supported language

### Slow Detection

First run downloads the language ID model (~100MB):
- Subsequent runs are faster (cached)
- Use manual language selection for batch processing same-language audio

## API Reference

### PhoneticTranscriber

```python
PhoneticTranscriber(
    language: str = 'en',
    use_onnx: bool = True,
    low_resource: bool = True,
    auto_detect_language: bool = False
)
```

### audio_to_phonemes

```python
def audio_to_phonemes(
    self,
    audio_path: Union[str, Path],
    sample_rate: Optional[int] = None,
    detect_language: bool = None  # Override instance setting
) -> Tuple[str, str]:  # Returns (phonemes, detected_language)
```

---

**Note**: Auto-detection requires SpeechBrain to be installed. Install with:
```bash
pip install speechbrain
```
