from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import re

try:
    from phonemizer import phonemize
    PHONEMIZER_AVAILABLE = True
except ImportError:
    PHONEMIZER_AVAILABLE = False

app = FastAPI(title="Yamato Phonetic Lyrics API")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LyricLine(BaseModel):
    time: float
    text: str
    phonemes: str = ""

class SongResponse(BaseModel):
    title: str
    artist: str
    album: str
    language: str
    lyrics: list[LyricLine]
    is_synced: bool

def fetch_lyrics_from_lrclib(artist: str, title: str) -> dict | None:
    """Fetch synchronized lyrics from LRCLIB"""
    try:
        url = "https://lrclib.net/api/get"
        params = {"artist_name": artist, "track_name": title}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def parse_synced_lyrics(synced_text: str) -> list[dict]:
    """Parse [mm:ss.xx] formatted lyrics"""
    lines = []
    pattern = r'\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)'
    
    for line in synced_text.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            milliseconds = int(match.group(3).ljust(3, '0')[:3])
            time = minutes * 60 + seconds + milliseconds / 1000.0
            text = match.group(4).strip()
            if text:  # Skip empty lines
                lines.append({"time": time, "text": text})
    
    return lines

def text_to_phonemes(text: str, language: str = 'en') -> str:
    """Convert text to IPA phonemes using subprocess to avoid espeak threading issues"""
    if not PHONEMIZER_AVAILABLE:
        return text  # Fallback to original text
    
    try:
        # Map language codes
        lang_map = {
            'en': 'en-us',
            'es': 'es',
            'fr': 'fr-fr',
            'ja': 'ja',
            'ht': 'fr-fr'  # Haitian Creole uses French rules
        }
        lang_code = lang_map.get(language, 'en-us')
        
        # Use subprocess to avoid espeak-ng threading/fifo issues
        import subprocess
        result = subprocess.run(
            ['espeak-ng', f'-v{lang_code}', '--ipa', '-q', text],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return text
    except Exception as e:
        # Log error but return original text as fallback
        print(f"Phonemization error: {e}")
        return text

@app.get("/")
def root():
    return {"message": "Yamato API - Phonetic Lyrics Transcription Service"}

@app.get("/api/search", response_model=list[dict])
def search_songs(q: str = Query(..., min_length=1)):
    """Search for songs by query"""
    try:
        url = "https://lrclib.net/api/search"
        params = {"q": q}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            # Return simplified results
            return [
                {
                    "id": item.get("id"),
                    "title": item.get("trackName"),
                    "artist": item.get("artistName"),
                    "album": item.get("albumName"),
                    "duration": item.get("duration"),
                    "hasSynced": bool(item.get("syncedLyrics"))
                }
                for item in results[:20]  # Limit to 20 results
            ]
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/lyrics/{song_id}", response_model=SongResponse)
def get_lyrics(song_id: int, lang: str = Query(default="en")):
    """Get lyrics with phonetic transcription by song ID"""
    try:
        url = f"https://lrclib.net/api/get/{song_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Song not found")
        
        data = response.json()
        synced_text = data.get("syncedLyrics")
        plain_text = data.get("plainLyrics")
        
        is_synced = bool(synced_text)
        lyric_lines = []
        
        if is_synced and synced_text:
            parsed_lines = parse_synced_lyrics(synced_text)
            for line in parsed_lines:
                phonemes = text_to_phonemes(line["text"], lang)
                lyric_lines.append(LyricLine(
                    time=line["time"],
                    text=line["text"],
                    phonemes=phonemes
                ))
        elif plain_text:
            # Fallback to plain lyrics without timing
            for line in plain_text.split('\n'):
                if line.strip():
                    phonemes = text_to_phonemes(line.strip(), lang)
                    lyric_lines.append(LyricLine(
                        time=0.0,
                        text=line.strip(),
                        phonemes=phonemes
                    ))
        else:
            raise HTTPException(status_code=404, detail="No lyrics available")
        
        return SongResponse(
            title=data.get("trackName", "Unknown"),
            artist=data.get("artistName", "Unknown"),
            album=data.get("albumName", "Unknown"),
            language=lang,
            lyrics=lyric_lines,
            is_synced=is_synced
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
