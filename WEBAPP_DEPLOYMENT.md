# 🌐 Deploy Web App to Streamlit Cloud (FREE)

## Option 1: One-Click Deployment (Recommended)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select repository: `essaie-creator/yamato-phonetic-transcriber`
4. Set main file path: `app.py`
5. Set requirements file: `requirements-web.txt`
6. Click **Deploy!**

Your app will be live at: `https://yamato-phonetic-transcriber.streamlit.app`

---

## Option 2: Manual Deployment with GitHub Actions

The workflow in `.github/workflows/webapp-deploy.yml` automatically:
- ✅ Builds the web app package
- ✅ Uploads as artifact for download
- ✅ Creates GitHub Release when you tag a version

### To trigger manually:
```bash
git push origin main
```

### To create a release:
```bash
git tag v1.0.0-web
git push origin v1.0.0-web
```

---

## Run Locally

```bash
# Install dependencies
pip install -r requirements-web.txt

# Run the web app
streamlit run app.py
```

The app will open at: http://localhost:8501

---

## Features

✅ **Automatic Language Detection** - Just upload audio, no need to select language  
✅ **Multi-language Support** - English, Spanish, French, Japanese, Haitian Creole  
✅ **Phonetic Transcription** - IPA output format  
✅ **Download Results** - Save transcriptions as text files  
✅ **User-Friendly Interface** - Simple drag-and-drop upload  

---

## How It Works

1. User uploads audio file (WAV, MP3, FLAC)
2. System automatically detects spoken language
3. SpeechBrain ASR transcribes audio to text
4. Phonemizer converts text to IPA phonemes
5. Results displayed with download option

---

## Requirements

- Python 3.8+
- speechbrain >= 0.3.0
- phonemizer >= 3.2.0
- onnxruntime >= 1.16.0
- streamlit >= 1.28.0

---

## Troubleshooting

**Error: "Language detection failed"**
- Ensure audio quality is good (clear speech, minimal background noise)
- Try with longer audio samples (at least 3 seconds)

**Error: "phonemizer not installed"**
```bash
pip install phonemizer
sudo apt-get install espeak-ng  # Linux
brew install espeak             # macOS
```

**App runs slowly**
- Enable low-resource mode in code
- Use smaller audio files (< 10MB)
- Consider using ONNX runtime optimization
