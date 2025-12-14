# 🛍️ RetailNext Smart Stylist

> AI-powered fashion assistant demonstrating OpenAI's latest APIs (December 2025)

## Overview

This demo showcases a complete AI fashion assistant for RetailNext, a premium retail store. It demonstrates **6 OpenAI APIs** working together to provide an intelligent, multimodal shopping experience.

## 🚀 OpenAI APIs Demonstrated

| API | Model | Purpose |
|-----|-------|---------|
| **Chat + Reasoning** | `gpt-5` | Intelligent fashion recommendations and conversation |
| **Vision** | `gpt-5` | Analyze uploaded/captured clothing images |
| **Speech-to-Text** | `gpt-4o-transcribe` | Voice input with superior accuracy |
| **Text-to-Speech** | `gpt-4o-mini-tts` | Australian-accented voice responses |
| **Embeddings** | `text-embedding-3-large` | Semantic product search (RAG) |
| **Structured Outputs** | JSON Schema | Reliable event context parsing |
| **Function Calling** | Tool Use | Dynamic inventory operations |

## 🎯 Business Problem Solved

**Customer Pain Point:** "I have an event coming up but don't know what to wear. I don't want to spend hours browsing - I want personalized recommendations that actually fit my needs."

**Our Solution:** An AI stylist that:
1. **Understands context** - Parses event type, formality, season, venue from natural conversation
2. **Sees what you show** - Analyzes clothing photos to suggest matching items
3. **Speaks naturally** - Voice input/output with Australian accent for local customers
4. **Finds perfect matches** - Semantic search goes beyond keywords
5. **Completes the look** - Creates head-to-toe outfit bundles with store locations

## 📁 Project Structure

```
retailnext-stylist-v2/
├── backend.py          # Core AI logic (all 6 APIs)
├── server.py           # FastAPI REST endpoints
├── demo_script.py      # Interactive demo for presentations
├── requirements.txt    # Python dependencies
├── .env.example        # Environment configuration template
└── README.md           # This file
```

## 🏃‍♂️ Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Your API Key

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

Or copy `.env.example` to `.env` and add your key there.

### 3. Run the Server

```bash
python server.py
```

Server starts at `http://localhost:8000`

### 4. Test the API

Open `http://localhost:8000/docs` for interactive Swagger documentation.

## 🎬 Demo Script (For Video Call Presentation)

The `demo_script.py` provides an interactive demonstration of all features:

```bash
# Run all demos with pauses (interactive)
python demo_script.py

# Run specific demo
python demo_script.py --demo 1  # Text chat
python demo_script.py --demo 2  # Semantic search
python demo_script.py --demo 3  # Outfit bundles
python demo_script.py --demo 4  # Vision analysis
python demo_script.py --demo 5  # Voice flow
python demo_script.py --demo 6  # Full pipeline

# Quick run without pauses
python demo_script.py --quick

# Health check only
python demo_script.py --health
```

## 🔌 API Endpoints

### Main Chat Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Text chat with optional image (base64) |
| `/voice-chat` | POST | Audio upload with optional image |
| `/chat-with-photo` | POST | Form-based chat with photo upload |

### Speech Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/transcribe` | POST | Audio to text (gpt-4o-transcribe) |
| `/tts` | POST | Text to speech (returns MP3) |
| `/tts/base64` | POST | Text to speech (returns base64) |

### Vision Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze-image` | POST | Analyze clothing image (file upload) |
| `/analyze-image/base64` | POST | Analyze clothing image (base64) |

### Structured Output Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/parse-event` | POST | Parse event context from text |

### Inventory Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/inventory` | GET | List all items |
| `/inventory/search` | POST | Search with filters |
| `/inventory/semantic-search` | POST | AI-powered similarity search |
| `/outfit-bundle` | POST | Generate complete outfit |

### Demo Helpers

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/demo/quick-test` | GET | Test all APIs |
| `/demo/sample-queries` | GET | Get sample demo queries |

## 🎤 Voice Features

### Australian Accent TTS

The TTS uses `gpt-4o-mini-tts` with instruction-steered voice:

```python
instructions = """
Speak with a warm, friendly Australian accent. 
Use natural Australian intonation and pacing.
Sound like a helpful retail assistant in Melbourne or Sydney.
"""
```

### Superior Transcription

Using `gpt-4o-transcribe` instead of Whisper for:
- Better accent handling
- Reduced hallucinations
- Higher accuracy in noisy environments

## 📸 Vision Capabilities

### Supported Inputs
- **File Upload**: JPG, PNG, WEBP
- **Base64**: Camera capture from mobile/webcam
- **Both**: Can combine with text query

### Analysis Output
```json
{
  "clothing_type": "blouse",
  "colors": ["blue", "white"],
  "patterns": ["floral"],
  "style": "casual",
  "occasion_suitability": ["brunch", "shopping", "casual outing"],
  "matching_suggestions": ["white pants", "denim jeans", "nude heels"]
}
```

## 🧠 Structured Outputs

Event parsing uses JSON Schema for reliable extraction:

**Input:** "I need an outfit for my daughter's graduation next Saturday. It's outdoors."

**Output:**
```json
{
  "event_type": "graduation ceremony",
  "formality_level": "smart-casual",
  "season": "spring",
  "venue_type": "outdoor",
  "gender": "women",
  "specific_requirements": ["comfortable shoes", "sun-appropriate"]
}
```

## 🔧 Function Calling

The AI dynamically calls inventory functions:

1. **check_inventory** - Verify item availability
2. **find_similar_items** - Semantic search (uses embeddings)
3. **get_outfit_bundle** - Create coordinated outfits
4. **get_item_location** - Get exact store location (aisle/bin)

## 🎭 Demo Mode

For reliable offline demonstrations:

```bash
export DEMO_MODE=true
python server.py
```

In demo mode:
- All API calls return mock data
- No OpenAI credits consumed
- Perfect for testing UI/UX
- Fallback for network issues during live demo

## 📊 Sample Demo Flow

### For CTO (Technical Depth)

1. Show architecture diagram
2. Demo `/parse-event` → Explain Structured Outputs with JSON Schema
3. Demo `/inventory/semantic-search` → Explain RAG with embeddings
4. Demo `/chat` with function calling → Show tool orchestration
5. Demo `/voice-chat` → Show full multimodal pipeline

### For Head of Innovation (Business Value)

1. Customer scenario: "Graduation outfit help"
2. Show natural voice interaction
3. Demonstrate image analysis capability
4. Present complete outfit bundle with prices
5. Highlight store location directions
6. Discuss ROI: reduced walk-outs, increased basket size

## 🎯 Key Differentiators

1. **Latest Models**: GPT-5, gpt-4o-transcribe, gpt-4o-mini-tts
2. **True Multimodal**: Voice + Vision + Text in single flow
3. **Australian Accent**: Instruction-steered TTS for local market
4. **Robust Demo**: Fallback mode for reliable presentations
5. **Production-Ready**: Proper error handling, logging, CORS

## 🔒 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | Your OpenAI API key |
| `OPENAI_GPT_MODEL` | `gpt-5` | Main reasoning model |
| `OPENAI_TRANSCRIBE_MODEL` | `gpt-4o-transcribe` | STT model |
| `OPENAI_TTS_MODEL` | `gpt-4o-mini-tts` | TTS model |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-large` | Embedding model |
| `TTS_VOICE` | `nova` | Base TTS voice |
| `DEMO_MODE` | `false` | Enable offline demo |
| `PORT` | `8000` | Server port |

## 📈 Metrics & ROI

Projected impact for RetailNext:
- **30% reduction** in "I couldn't find anything" walk-outs
- **25% increase** in average basket size (complete outfits vs. single items)
- **40% faster** customer service (AI handles routine questions)
- **95% customer satisfaction** with personalized recommendations

## 🚨 Troubleshooting

### API Key Issues
```bash
# Verify key is set
echo $OPENAI_API_KEY

# Test connectivity
python -c "from backend import health_check; print(health_check())"
```

### Demo Mode Not Working
```bash
# Ensure environment variable is set correctly
export DEMO_MODE=true  # Not "True" or "1"
```

### Audio Not Playing
- Check browser supports MP3
- Verify TTS endpoint returns 200
- Try `/tts/base64` endpoint instead

## 📞 Support

For questions about this demo:
- Check `/docs` for interactive API documentation
- Run `python demo_script.py --health` to verify setup
- Review logs for detailed error messages

---

**Built for OpenAI Solutions Engineer Interview**  
*Demonstrating deep integration of OpenAI's latest API capabilities*
