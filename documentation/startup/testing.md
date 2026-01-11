# Local Testing Guide

Quick guide to run the RetailNext Smart Stylist locally with live OpenAI API calls.

---

## Prerequisites

- Python 3.9+
- OpenAI API key with credits
- Modern web browser

---

## Step 1: Set Your API Key

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

Or create `backend/.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

---

## Step 2: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## Step 3: Start Backend

```bash
cd backend
python server.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Loading clothing data...
INFO:     Generating embeddings... (takes 30-60 seconds first time)
INFO:     RAG system ready
```

**Backend runs on:** `http://localhost:8001`

---

## Step 4: Start Frontend

Open a new terminal:

```bash
cd frontend
python -m http.server 8080
```

**Frontend runs on:** `http://localhost:8080`

---

## Step 5: Test

1. Open `http://localhost:8080` in browser
2. Check header shows **green "Connected"** status
3. Type: `I need an outfit for a graduation`
4. Wait 3-5 seconds for AI response

---

## Quick Health Check

```bash
curl http://localhost:8001/health
```

Expected response:
```json
{"status": "healthy", "rag_loaded": true}
```

---

## Test Individual Features

| Feature | How to Test |
|---------|-------------|
| Chat | Type any fashion question |
| Vision | Click camera icon, upload clothing image |
| Voice Input | Click microphone, speak, click stop |
| Voice Output | Toggle "Audio Response" switch before sending |

---

## API Test Page

Open `http://localhost:8080/demo.html` to test each API endpoint individually.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection Failed" | Check backend is running on port 8001 |
| "API key not configured" | Verify `OPENAI_API_KEY` is set |
| Slow first response | Normal - embeddings generating (one-time) |
| CORS errors | Use `python -m http.server`, not `file://` |

---

## Estimated Costs

| Action | Approximate Cost |
|--------|------------------|
| Single chat query | $0.002 - $0.005 |
| Image analysis | $0.005 - $0.01 |
| Voice transcription (30s) | $0.0015 |
| Voice response (30s) | $0.01 |
| **Full conversation** | **~$0.02** |

---

## Stop Services

- Backend: `Ctrl+C` in terminal
- Frontend: `Ctrl+C` in terminal
