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

### Mobile (Android)

Download the latest APK from [Releases](https://github.com/essaie-creator/yamato-phonetic-transcriber/releases) or build from source in `mobile-android/` directory. See `mobile-android/README.md` for details.

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
