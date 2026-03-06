# Setup script for Yamato Phonetic Transcriber

This guide will help you set up the Yamato Phonetic Transcriber on your system.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- espeak-ng (required for phonemizer backend)

## Installation Steps

### 1. Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y espeak-ng espeak-ng-data libespeak-ng-dev
```

#### macOS
```bash
brew install espeak-ng
```

#### Windows
Download and install eSpeak NG from: https://github.com/espeak-ng/espeak-ng/releases

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install speechbrain phonemizer onnxruntime numpy torch librosa soundfile
```

### 3. Verify Installation

Test the installation:
```bash
python transcribe.py --list-languages
python transcribe.py --text "Hello world" --lang en
```

## Low-Resource Mode

The application is optimized for low-resource environments by default:

- Uses ONNX runtime for efficient inference
- Lazy loading of models to reduce memory footprint
- CPU-optimized execution providers
- Quantized model support

To disable optimizations:
```bash
python transcribe.py --text "Hello" --lang en --no-onnx --no-low-resource
```

## Usage Examples

### Text to Phonemes
```bash
# English
python transcribe.py --text "Hello world" --lang en

# Spanish
python transcribe.py --text "Hola mundo" --lang es

# French
python transcribe.py --text "Bonjour le monde" --lang fr

# Japanese
python transcribe.py --text "こんにちは" --lang ja

# Haitian Creole
python transcribe.py --text "Bonjou mond" --lang ht
```

### Audio to Phonemes
```bash
python transcribe.py --audio speech.wav --lang en
```

### Batch Processing
```bash
python transcribe.py --input-file texts.txt --output-file output.txt --lang es
```

### Python API
```python
from yamato_transcriber import PhoneticTranscriber

transcriber = PhoneticTranscriber(language='en')
phonemes = transcriber.text_to_phonemes("Hello world")
print(phonemes)
```

## Troubleshooting

### phonemizer not found
Make sure espeak-ng is installed and in your PATH:
```bash
which espeak-ng
```

### Memory issues
Enable low-resource mode (default):
```bash
python transcribe.py --text "..." --lang en --no-low-resource  # Disable if needed
```

### Slow performance
Ensure ONNX runtime is using CPU optimizations:
```bash
pip install onnxruntime-gpu  # If GPU available
```

## Supported Languages

| Code | Language | Script |
|------|----------|--------|
| en | English | Latin |
| es | Spanish | Latin |
| fr | French | Latin |
| ja | Japanese | Kana/Kanji |
| ht | Haitian Creole | Latin |

## License

MIT License
