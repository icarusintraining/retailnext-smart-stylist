# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RetailNext Smart Stylist is an AI-powered fashion assistant demonstrating integration of OpenAI APIs. It helps customers find outfits for specific events using natural language, voice input, and image analysis.

## Build & Run Commands

### Backend (Python/FastAPI)
```bash
cd backend
pip install -r requirements.txt
python server.py                    # Runs on http://localhost:8001
```

### Frontend
```bash
cd frontend
python -m http.server 8080          # Open http://localhost:8080
```

### Demo Mode (no API calls, mock data)
```bash
export DEMO_MODE=true
python server.py
```

### Environment Variables
- `OPENAI_API_KEY` - Required for API calls
- `OPENAI_GPT_MODEL` - Default: `gpt-4o`
- `OPENAI_TRANSCRIBE_MODEL` - Default: `gpt-4o-transcribe`
- `OPENAI_TTS_MODEL` - Default: `gpt-4o-mini-tts`
- `OPENAI_EMBEDDING_MODEL` - Default: `text-embedding-3-large`
- `PORT` - Server port (default: 8001)

## Architecture

### Backend Structure
- **server.py**: FastAPI REST server with all endpoints (`/api/chat`, `/api/search`, `/api/transcribe`, `/api/tts`, `/api/outfit-bundle`, etc.)
- **backend.py**: Core AI logic with OpenAI API integrations, function calling tools, mock inventory database, and demo fallbacks
- **clothing_rag.py**: RAG implementation with embeddings for semantic product search. Loads `sample_styles.csv` clothing dataset and generates/caches embeddings for similarity search

### Frontend Structure
- **index.html/app.js**: Main application with chat interface, voice recording (MediaRecorder API), and product display
- **demo.html**: API testing helper page for verifying endpoints

### Key API Flow
1. User input (text/voice/image) → `/api/chat`
2. Server orchestrates: event parsing (Structured Outputs) → image analysis (Vision) → semantic search (Embeddings/RAG) → response generation
3. Returns: text response, recommended items with prices/locations, optional audio (TTS)

### OpenAI APIs Used
- **GPT-4o**: Chat, vision analysis, structured outputs for event parsing
- **gpt-4o-transcribe**: Speech-to-text
- **gpt-4o-mini-tts**: Text-to-speech with Australian accent (instruction-steered)
- **text-embedding-3-large**: Semantic search (256 dimensions)
- **Function Calling**: Dynamic inventory operations (`check_inventory`, `find_similar_items`, `get_outfit_bundle`)

## Key Implementation Details

### RAG System (clothing_rag.py)
- Loads CSV dataset from `sample_styles.csv`
- Generates embeddings for all items on startup (cached in `_embeddings_cache`)
- Uses cosine similarity with configurable threshold (default 0.3-0.5)
- Enriches items with mock prices, store locations, and stock levels

### Function Calling (backend.py)
- `STYLIST_TOOLS` defines available functions
- `FUNCTION_MAP` dispatches to implementations: `check_inventory`, `find_similar_items`, `get_outfit_bundle`, `get_item_location`

### Demo Mode
When `DEMO_MODE=true`, all API calls return realistic mock data from `MOCK_INVENTORY` in backend.py. Useful for testing without API costs.

## Frontend Notes

- API base URL configured in `app.js`: `const API_BASE_URL = 'http://localhost:8001'`
- Microphone uses MediaRecorder API with WebM format
- Product images served from GitHub (openai-cookbook sample_images)
