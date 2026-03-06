# Yamato Phonetic Transcriber

A lightweight multilingual phonetic transcription application designed for low-resource environments.

## Features

- **Multilingual Support**: English (en), Spanish (es), French (fr), Japanese (ja), Haitian Creole (ht)
- **IPA Output**: International Phonetic Alphabet transcription
- **Low-Resource Optimized**: Uses ONNX runtime for efficient inference
- **SpeechBrain Integration**: Advanced speech processing capabilities
- **Phonemizer Backend**: Accurate text-to-phoneme conversion

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Transcribe text to IPA
python transcribe.py --text "Hello world" --lang en

# Transcribe from audio file
python transcribe.py --audio input.wav --lang en

# Batch processing
python transcribe.py --input-file texts.txt --output-file transcriptions.txt --lang es
```

### Python API

```python
from yamato_transcriber import PhoneticTranscriber

# Initialize transcriber
transcriber = PhoneticTranscriber(language='en')

# Text to phonemes
phonemes = transcriber.text_to_phonemes("Hello world")
print(phonemes)  # /həˈloʊ wɜrld/

# Audio to phonemes (via ASR)
phonemes = transcriber.audio_to_phonemes("audio.wav")
```

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
