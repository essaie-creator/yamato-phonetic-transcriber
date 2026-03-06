# Yamato Phonetic Transcriber

A lightweight multilingual phonetic transcription application designed for low-resource environments.

## Features

- **Multilingual Support**: English (en), Spanish (es), French (fr), Japanese (ja), Haitian Creole (ht)
- **IPA Output**: International Phonetic Alphabet transcription
- **Low-Resource Optimized**: Uses ONNX runtime for efficient inference
- **SpeechBrain Integration**: Advanced speech processing capabilities
- **Phonemizer Backend**: Accurate text-to-phoneme conversion
- **Graphical User Interface**: User-friendly Tkinter GUI for non-technical users
- **Mobile App**: Native Android app for Huawei and other Android devices

## Installation

### Desktop (Python)

```bash
pip install -r requirements.txt
```

### Mobile (Android/Huawei)

**Option 1: Download Pre-built APK**
Download the latest APK from [Releases](https://github.com/essaie-creator/yamato-phonetic-transcriber/releases). Look for assets named `app-debug.apk` or `app-release-unsigned.apk`.

**Option 2: Build from Source**
See `mobile-android/README.md` and `mobile-android/BUILD.md` for detailed build instructions.

### Automatic Builds via GitHub Actions

This project uses GitHub Actions to automatically build and attach binaries to releases:

- **Python packages**: Triggered by tags like `v1.0.0`, `v1.2.3-beta`
- **Android APKs**: Triggered by tags like `v1.0.0-android`, `v1.2.3-mobile`

To trigger a build, simply create and push a tag:

```bash
# For Python release
git tag v1.0.0
git push origin v1.0.0

# For Android release
git tag v1.0.0-android
git push origin v1.0.0-android
```

GitHub will automatically build the project and attach the binaries to the release page.

## Usage

### Command Line

```bash
# Transcribe text to IPA
python transcribe.py --text "Hello world" --lang en

# Transcribe from audio file
python transcribe.py --audio input.wav --lang en

# Batch processing
python transcribe.py --input-file texts.txt --output-file transcriptions.txt --lang es

# Launch GUI
python transcribe.py --gui
```

### Python API

```python
from yamato_transcriber import PhoneticTranscriber, launch_gui

# Initialize transcriber
transcriber = PhoneticTranscriber(language='en')

# Text to phonemes
phonemes = transcriber.text_to_phonemes("Hello world")
print(phonemes)  # /həˈloʊ wɜrld/

# Audio to phonemes (via ASR)
phonemes = transcriber.audio_to_phonemes("audio.wav")

# Launch GUI
launch_gui()
```

### Mobile App

See `mobile-android/README.md` for installation and usage instructions.

## Supported Languages

| Language | Code | Script |
|----------|------|--------|
| English | en | Latin |
| Spanish | es | Latin |
| French | fr | Latin |
| Japanese | ja | Kana/Kanji |
| Haitian Creole | ht | Latin |

## Architecture

- **SpeechBrain**: Speech recognition and processing
- **Phonemizer**: Text-to-phoneme conversion with eSpeak backend
- **ONNX Runtime**: Optimized model inference
- **PyTorch**: Deep learning backend

## Low-Resource Optimization

- Quantized ONNX models for reduced memory footprint
- Lazy loading of language models
- Minimal dependencies for offline deployment
- CPU-optimized inference

## License

MIT License
