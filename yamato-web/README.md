# Yamato Web - Phonetic Lyrics App

A cloud-native web application for displaying synchronized lyrics with IPA phonetic transcriptions. Accessible from anywhere, no credentials required.

## Features

- 🔍 **Search Songs**: Find any song using LRCLIB database
- 📝 **Real Lyrics**: Faithful lyrics fetched automatically from the internet
- 🎯 **IPA Transcription**: Phonetic guides for perfect pronunciation
- ⏱️ **Synced Lyrics**: Time-synchronized display for karaoke-style singing
- 🌍 **Multilingual**: Support for English, Spanish, French, Japanese, Haitian Creole
- 📱 **Mobile Responsive**: Works on any device with a browser
- 🔓 **No Login**: Open access without credentials

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend API    │────▶│   LRCLIB API    │
│  (HTML/JS/CSS)  │     │  (FastAPI + UV)  │     │  (Lyrics Data)  │
│   Vercel/Netlify│     │  Render/Railway  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Phonemizer      │
                        │  (eSpeak-ng)     │
                        │  IPA Conversion  │
                        └──────────────────┘
```

## Quick Start

### Local Development

#### Backend

```bash
cd backend

# Install system dependencies (Linux/Mac)
# Ubuntu/Debian:
sudo apt-get install espeak-ng espeak-ng-data

# Mac:
brew install espeak-ng

# Install Python dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

Simply open `frontend/index.html` in a browser, or serve it:

```bash
cd frontend
python -m http.server 3000
# Visit http://localhost:3000
```

**Note**: Update the `API_BASE` URL in `frontend/index.html` to point to your backend (default: `http://localhost:8000`).

### Docker Deployment

```bash
cd backend

# Build the image
docker build -t yamato-api .

# Run the container
docker run -p 8000:8000 yamato-api
```

## Cloud Deployment

### Deploy Backend to Render.com

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect your GitHub repository
3. Configure:
   - **Root Directory**: `yamato-web/backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy!

### Deploy Frontend to Vercel

1. Push code to GitHub
2. Import project to [Vercel](https://vercel.com)
3. Set root directory to `yamato-web/frontend`
4. Update `API_BASE` in `index.html` to your Render backend URL
5. Deploy!

## API Endpoints

### Search Songs
```
GET /api/search?q={query}
```

**Response:**
```json
[
  {
    "id": 12345,
    "title": "Bohemian Rhapsody",
    "artist": "Queen",
    "album": "A Night at the Opera",
    "duration": 354,
    "hasSynced": true
  }
]
```

### Get Lyrics with Phonemes
```
GET /api/lyrics/{song_id}?lang={language_code}
```

**Parameters:**
- `song_id`: LRCLIB song ID
- `lang`: Language code (`en`, `es`, `fr`, `ja`, `ht`)

**Response:**
```json
{
  "title": "Bohemian Rhapsody",
  "artist": "Queen",
  "album": "A Night at the Opera",
  "language": "en",
  "is_synced": true,
  "lyrics": [
    {
      "time": 0.0,
      "text": "Is this the real life?",
      "phonemes": "ɪz ðɪs ðə ɹiəl laɪf?"
    },
    {
      "time": 4.5,
      "text": "Is this just fantasy?",
      "phonemes": "ɪz ðɪs ʤʌst fæntəsi?"
    }
  ]
}
```

## User Journey

1. **Open App**: Navigate to your deployed URL (no login needed)
2. **Search**: Type song name or artist (e.g., "Bohemian Rhapsody Queen")
3. **Select**: Click on the desired song from search results
4. **Sing Along**: View lyrics with IPA phonetic transcription
   - Original text displayed prominently
   - IPA pronunciation guide below each line
   - Synced lyrics highlight current position (if available)

## Technology Stack

**Backend:**
- FastAPI (Python web framework)
- Uvicorn (ASGI server)
- phonemizer (IPA conversion via eSpeak-ng)
- requests (HTTP client)

**Frontend:**
- Vanilla HTML/CSS/JavaScript
- Mobile-responsive design
- No framework dependencies

**External APIs:**
- LRCLIB (lyrics database - free, no API key required)

**Deployment:**
- Docker containerization
- Render/Railway/Fly.io (backend hosting)
- Vercel/Netlify (frontend hosting)

## Supported Languages

| Code | Language | Quality |
|------|----------|---------|
| en   | English  | ★★★★★ |
| es   | Spanish  | ★★★★★ |
| fr   | French   | ★★★★★ |
| ja   | Japanese | ★★★★☆ |
| ht   | Haitian Creole | ★★★☆☆ |

## License

MIT License - Free for personal and commercial use.

## Credits

- Lyrics data: [LRCLIB](https://lrclib.net)
- Phonetic transcription: [eSpeak-ng](https://github.com/espeak-ng/espeak-ng)
- Inspired by the Yamato phonetic transcription project
