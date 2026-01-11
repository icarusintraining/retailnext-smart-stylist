# Video Walkthrough Guide: RetailNext Smart Stylist
## 5-6 Minute Technical Demo Script

**Focus:** Demonstrating technical competency - how you built on the OpenAI cookbook and can explain the code.

---

## TIMING OVERVIEW

| Section | Duration | Content |
|---------|----------|---------|
| 1. Introduction | 30 sec | What you built, cookbook foundation |
| 2. Architecture Overview | 45 sec | High-level architecture, OpenAI APIs used |
| 3. RAG Implementation | 90 sec | Embeddings, semantic search, real data |
| 4. Multimodal Features | 90 sec | Vision, Voice, Structured Outputs |
| 5. Frontend Integration | 45 sec | UI connecting to APIs |
| 6. Live Demo | 60 sec | Quick end-to-end demonstration |

**Total: ~5.5 minutes**

---

## SECTION 1: INTRODUCTION (30 seconds)

### What to Say:
> "I'm going to walk you through the RetailNext Smart Stylist, an AI fashion assistant I built by extending the OpenAI cookbook's clothing dataset example.
>
> The cookbook provided a foundation with sample clothing data and basic embedding search. I've extended this into a full-stack application that orchestrates **six different OpenAI APIs** - GPT-4o for chat and vision, text-embedding-3-large for RAG, plus transcription and text-to-speech for voice interactions."

### What to Show:
- Open the running application in browser (`localhost:8081`)
- Quick pan of the UI showing chat interface and product recommendations

---

## SECTION 2: ARCHITECTURE OVERVIEW (45 seconds)

### What to Say:
> "Let me show you the architecture. The backend is a FastAPI server with two main modules."

### What to Show:
Open `backend/server.py` and scroll to show endpoints:

```
Show lines ~150-180 (endpoints list)
```

> "The server exposes endpoints for chat, search, image analysis, transcription, and text-to-speech.
>
> Here are the four OpenAI models I'm using..."

Open `backend/backend.py` and show the model configuration:

```python
# Lines 30-38
GPT_MODEL = "gpt-4o"
TRANSCRIPTION_MODEL = "gpt-4o-transcribe"
TTS_MODEL = "gpt-4o-mini-tts"
EMBEDDING_MODEL = "text-embedding-3-large"
```

> "GPT-4o handles chat, vision analysis, and structured outputs. The newer transcription model provides better accuracy than Whisper. And text-embedding-3-large powers the semantic search."

---

## SECTION 3: RAG IMPLEMENTATION (90 seconds)

### What to Say:
> "The core of the recommendation engine is a custom RAG implementation. Let me show you how it works."

### What to Show:

**3a. Data Loading** - Open `backend/clothing_rag.py`:

```python
# Lines 36-55 - Show data loading
DATA_URL = "https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/data/sample_clothes/sample_styles.csv"
```

> "I'm using the OpenAI cookbook's clothing dataset - about 1,000 items with attributes like article type, color, season, and gender."

**3b. Embedding Generation** - Show the embedding code:

```python
# Lines 83-98
response = client.embeddings.create(
    model=EMBEDDING_MODEL,
    input=texts,
    dimensions=EMBEDDING_DIMENSIONS  # 256 dimensions
)
```

> "Each item gets embedded using text-embedding-3-large. I'm using 256 dimensions for efficiency. The embeddings are generated in parallel batches and cached to avoid redundant API calls."

**3c. Semantic Search** - Show the search function:

```python
# Lines 177-194 - find_similar_items function
def find_similar_items(query, gender=None, top_k=5):
    query_embedding = get_embedding(query)

    # Cosine similarity calculation
    similarities = []
    for idx, item_embedding in enumerate(embeddings):
        sim = cosine_similarity(query_embedding, item_embedding)
        similarities.append((idx, sim))
```

> "When a user asks for something, I embed their query and compute cosine similarity against all items. The results are filtered by gender and article type, then enriched with retail metadata like pricing and store locations."

**3d. Data Enrichment** - Show enrichment code:

```python
# Lines 268-314
price_ranges = {
    'shirts': (45, 120),
    'dresses': (75, 250),
    'blazers': (120, 400),
}
```

> "I added realistic retail data - deterministic pricing based on category, simulated stock levels with 70% in stock, 20% low stock, 10% out of stock, and physical store locations."

---

## SECTION 4: MULTIMODAL FEATURES (90 seconds)

### What to Say:
> "Beyond basic text search, I've integrated three powerful multimodal capabilities."

### What to Show:

**4a. Vision Analysis** - Open `backend/clothing_rag.py`:

```python
# Lines 366-420
response = client.chat.completions.create(
    model=GPT_MODEL,
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Analyze this clothing item..."},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}",
                    "detail": "high"
                }
            }
        ]
    }],
    response_format={"type": "json_object"}
)
```

> "Users can upload a photo of clothing. GPT-4o Vision analyzes it to extract article type, color, pattern, style, and even suggests complementary items. I then use that analysis to drive semantic search."

**4b. Structured Outputs** - Open `backend/backend.py`:

```python
# Lines 165-235 - EVENT_CONTEXT_SCHEMA
response_format={
    "type": "json_schema",
    "json_schema": {
        "name": "event_context",
        "strict": True,
        "schema": EVENT_CONTEXT_SCHEMA
    }
}
```

> "For parsing user requests like 'I need an outfit for a graduation', I use structured outputs with a strict JSON schema. This guarantees I get properly formatted event details - formality level, season, venue type, budget preference - which drive the filtering."

**4c. Voice with Australian Accent** - Show TTS code:

```python
# Lines 41-46, 756-766
TTS_AUSTRALIAN_INSTRUCTIONS = """
Speak with a warm, friendly Australian accent.
Sound like a helpful retail assistant in Melbourne or Sydney.
"""

response = client.audio.speech.create(
    model=TTS_MODEL,
    voice="nova",
    input=text,
    instructions=TTS_AUSTRALIAN_INSTRUCTIONS  # Instruction steering
)
```

> "For the Australian retail context, I'm using instruction-steered text-to-speech. Instead of training a custom voice, I pass natural language instructions to the TTS model to adopt an Australian accent. This is a newer capability that's really powerful."

---

## SECTION 5: FRONTEND INTEGRATION (45 seconds)

### What to Say:
> "The frontend is a vanilla JavaScript application that ties everything together."

### What to Show:

Open `frontend/app.js`:

```javascript
// Lines 172-204 - sendMessage function
const requestPayload = {
    message: message,
    conversation_history: state.conversationHistory,
    image_base64: state.currentImage,
    return_audio: ENABLE_AUDIO_RESPONSES
};

const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestPayload)
});
```

> "The main chat endpoint accepts text, optional images, and conversation history. It returns recommendations with real product images, and optionally an audio response."

Show the product card rendering:

```javascript
// Lines 638-694 - createProductCard
card.innerHTML = `
    <div class="product-image-container">
        <img src="${imageUrl}" class="product-image">
        <div class="product-actions">
            <button class="add-to-bag-btn">Add to Bag</button>
        </div>
    </div>
`;
```

> "Results are displayed in a Pinterest-style masonry grid with hover effects and quick actions."

---

## SECTION 6: LIVE DEMO (60 seconds)

### What to Say:
> "Let me show you this working end-to-end."

### What to Demo:

1. **Type a query:**
   > "I need an outfit for a summer wedding"

2. **Wait for response** - Show the AI thinking animation

3. **Point out the results:**
   > "You can see GPT-4o parsed the event context - it identified 'wedding' as semi-formal, summer season. The RAG system found semantically relevant items, and each card shows the product image from the dataset, a generated price, and store location."

4. **Click a product card:**
   > "The modal shows full details including 'Complete the Look' suggestions for cross-selling."

5. **(Optional if time)** Click the microphone:
   > "Voice input uses the transcription API, and responses can be played back with the Australian accent TTS."

---

## CLOSING (15 seconds)

### What to Say:
> "To summarize - I extended the cookbook's basic dataset into a production-grade application using six OpenAI APIs: embeddings for RAG, GPT-4o for chat and vision, structured outputs for parsing, plus voice transcription and TTS. The code is modular, well-documented, and ready for the executive demo.
>
> Thanks for watching."

---

## KEY TECHNICAL POINTS TO EMPHASIZE

If asked questions or need to elaborate, these are the strongest technical differentiators:

1. **Custom RAG Pipeline** - Not using LangChain or vector databases; pure OpenAI embeddings with manual cosine similarity for educational clarity

2. **Multimodal Orchestration** - Single `/api/chat` endpoint that intelligently combines text, vision, and audio

3. **Instruction-Steered TTS** - Novel use of the `instructions` parameter for accent control

4. **Structured Outputs with Strict Schema** - Guarantees valid JSON for event parsing

5. **Retail Domain Enrichment** - Realistic pricing, inventory, and store locations layered on top of cookbook data

6. **Graceful Degradation** - Demo mode allows testing without API keys

---

## FILES TO HAVE OPEN

Before recording, open these files in your editor:

1. `backend/server.py` - Show endpoints and orchestration
2. `backend/backend.py` - Show model config, TTS instructions, structured outputs
3. `backend/clothing_rag.py` - Show RAG implementation, vision analysis
4. `frontend/app.js` - Show API integration and UI rendering

---

## TROUBLESHOOTING

**If the backend isn't responding:**
- Check `python server.py` is running on port 8001
- Verify `OPENAI_API_KEY` is set

**If images don't load:**
- Images come from GitHub raw URLs; ensure internet connectivity

**If voice doesn't work:**
- Browser microphone permissions required
- Check console for errors

---

## RECORDING TIPS

1. **Use a clean browser** - No bookmarks bar, extensions hidden
2. **Zoom your editor** - 150-175% for readability
3. **Pre-load all tabs** - Backend terminal, editor with files, browser with app
4. **Practice the flow** - Run through once before recording
5. **Speak clearly** - Focus on explaining *why* you made technical choices
