# Deployment Guide

## Streamlit Cloud Deployment (Recommended)

### Quick Setup (2 minutes)

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. Click "New app"
3. Connect your GitHub repository: `essaie-creator/yamato-phonetic-transcriber`
4. Configure:
   - **Main file path:** `app.py`
   - **Python version:** `3.10` or `3.11`
   - **Requirements file:** `requirements-web.txt`
5. Click "Deploy!"

### What Happens Next

Streamlit Cloud will:
- Install all dependencies automatically
- Run your app in the cloud for free
- Provide a public URL like: `https://yamato-phonetic-transcriber.streamlit.app`

### Requirements Files Updated

✅ `requirements-web.txt` - Optimized for Streamlit Cloud with pinned versions:
- speechbrain==0.3.3 (fixed version for compatibility)
- torch & torchaudio < 2.5.0 (prevents breaking changes)
- numpy < 2.0.0 (avoids compatibility issues)

✅ `.streamlit/config.toml` - Pre-configured settings
✅ `.streamlit/secrets.toml` - For API keys if needed

## Manual Deployment

### Local Testing

```bash
pip install -r requirements-web.txt
streamlit run app.py
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

Then run:
```bash
docker build -t yamato-transcriber .
docker run -p 8501:8501 yamato-transcriber
```

## Troubleshooting

### Error: `torchaudio.list_audio_backends()`

This error occurs with incompatible torch/torchaudio versions. Our updated `requirements-web.txt` fixes this by:
- Pinning speechbrain to 0.3.3
- Limiting torch/torchaudio to < 2.5.0
- Adding explicit torchaudio dependency

### Error: Module not found

Ensure you're using `requirements-web.txt` not `requirements.txt` for Streamlit deployment.

## Automatic Deployment

The workflow `.github/workflows/streamlit-deploy.yml` automatically validates your app structure on every push to main branch.
