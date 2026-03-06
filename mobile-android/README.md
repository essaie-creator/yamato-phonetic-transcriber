# Yamato Phonetic Transcriber - Android Mobile App

Native Android application for phonetic transcription, compatible with Huawei and other Android devices.

## Features

- **Offline Transcription**: Works without internet connection after initial model download
- **Text-to-Phoneme**: Convert text to IPA phonetic transcription
- **Audio-to-Phoneme**: Record or upload audio files for transcription
- **Multi-language Support**: English, Spanish, French, Japanese, Haitian Creole
- **Low Resource Mode**: Optimized for devices with limited RAM
- **Material Design**: Modern, intuitive user interface
- **Dark Mode**: Easy on the eyes for extended use

## Requirements

- Android 8.0 (API level 26) or higher
- Minimum 2GB RAM (4GB recommended)
- 500MB free storage space

## Installation

### Option 1: Download APK

Download the latest APK from the [Releases](https://github.com/essaie-creator/yamato-phonetic-transcriber/releases) page.

### Option 2: Build from Source

```bash
# Clone the repository
git clone https://github.com/essaie-creator/yamato-phonetic-transcriber.git
cd yamato-phonetic-transcriber/mobile-android

# Open in Android Studio
# File -> Open -> Select the mobile-android directory

# Build APK
# Build -> Build Bundle(s) / APK(s) -> Build APK(s)
```

### Option 3: Command Line Build

```bash
# Navigate to project directory
cd mobile-android

# Build debug APK
./gradlew assembleDebug

# Build release APK (requires signing)
./gradlew assembleRelease
```

## Project Structure

```
mobile-android/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/yamato/transcriber/
│   │       │   ├── MainActivity.kt
│   │       │   ├── TranscriberEngine.kt
│   │       │   ├── PhonemeAdapter.kt
│   │       │   └── util/
│   │       │       └── AudioUtils.kt
│   │       ├── res/
│   │       │   ├── layout/
│   │       │   ├── values/
│   │       │   └── drawable/
│   │       └── AndroidManifest.xml
│   └── build.gradle.kts
├── gradle/
├── build.gradle.kts
└── settings.gradle.kts
```

## Usage

### Text Transcription

1. Launch the app
2. Select language from dropdown
3. Type or paste text in input field
4. Tap "Transcribe" button
5. View IPA phonetic transcription in output field
6. Copy or save results

### Audio Transcription

1. Tap microphone icon
2. Grant microphone permission
3. Speak clearly into microphone
4. Tap stop button when finished
5. Wait for processing
6. View phonetic transcription

### Batch Processing

1. Tap menu → Batch Process
2. Import text file (one line per text)
3. Configure output format
4. Start batch processing
5. Export results

## Configuration

Access settings via menu → Settings:

- **Default Language**: Set preferred transcription language
- **Output Format**: Choose between IPA or ARPABET
- **Low Resource Mode**: Enable for devices with < 3GB RAM
- **Cache Models**: Store models locally for faster loading
- **Audio Quality**: Adjust recording quality (affects file size)

## Huawei Device Compatibility

This app is fully compatible with Huawei devices running EMUI:

- **Huawei P Series**: P30, P40, P50, etc.
- **Huawei Mate Series**: Mate 30, Mate 40, Mate 50, etc.
- **Huawei Nova Series**: Nova 7, Nova 8, Nova 9, etc.
- **Honor Devices**: Honor 50, Honor 60, etc. (pre-split models)

### Huawei AppGallery

The app will be available on Huawei AppGallery soon. For now, install via APK.

## Troubleshooting

### App Crashes on Startup

- Ensure Android version is 8.0 or higher
- Clear app data: Settings → Apps → Yamato → Storage → Clear Data
- Reinstall the app

### Transcription Fails

- Check if language model is downloaded (Settings → Models)
- Ensure sufficient storage space (> 500MB)
- Try enabling Low Resource Mode

### Audio Recording Issues

- Grant microphone permission: Settings → Apps → Yamato → Permissions
- Check if other apps can record audio
- Restart the app

## Performance Optimization

For best performance on low-end devices:

1. Enable Low Resource Mode in settings
2. Use shorter audio clips (< 30 seconds)
3. Close background apps before transcription
4. Use WAV format for audio (better compatibility)

## Privacy

- All processing happens on-device (no internet required)
- No data is collected or transmitted
- Audio recordings are stored locally only
- Models are cached locally for offline use

## License

MIT License - See LICENSE file for details

## Support

For issues and feature requests, please visit:
https://github.com/essaie-creator/yamato-phonetic-transcriber/issues

## Credits

- SpeechBrain team for ASR models
- eSpeak NG for phonemization
- ONNX Runtime for optimization
- Android open-source community
