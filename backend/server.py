"""
RetailNext Smart Stylist - API Server V2
Using real clothing data with RAG implementation
Based on OpenAI Cookbook approach
"""

import os
import base64
import json
import logging
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import our RAG implementation
from clothing_rag import (
    initialize_rag_system,
    search_by_description,
    get_matching_items,
    create_outfit_bundle,
    analyze_clothing_image
)

# Import original backend for TTS/STT
from backend import (
    transcribe_audio_bytes,
    text_to_speech_bytes,
    parse_event_context,
    get_client,
    GPT_MODEL,
    TRANSCRIPTION_MODEL,
    TTS_MODEL,
    EMBEDDING_MODEL,
    DEMO_MODE
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def detect_search_intent(message: str) -> str:
    """
    Detect whether user wants similar items or complementary items.

    Returns:
        "similar" - user wants items like the one they uploaded
        "complementary" - user wants items that go WITH what they uploaded
    """
    if not message:
        return "complementary"  # Default when no message provided

    message_lower = message.lower()

    # Keywords indicating user wants SIMILAR items (same type)
    similar_keywords = [
        "similar", "like this", "like that", "same", "matching",
        "alternatives", "other options", "more like", "this style",
        "do you have", "any other", "different color", "different colours",
        "show me more", "similar to"
    ]

    # Keywords indicating user wants COMPLEMENTARY items (go with it)
    complementary_keywords = [
        "goes with", "go with", "pair with", "match with", "wear with",
        "complement", "complete the look", "outfit", "what to wear",
        "accessories for", "style with"
    ]

    # Check for similar intent first (more specific ask)
    for keyword in similar_keywords:
        if keyword in message_lower:
            logger.info(f"Detected 'similar' intent from keyword: '{keyword}'")
            return "similar"

    # Check for complementary intent
    for keyword in complementary_keywords:
        if keyword in message_lower:
            logger.info(f"Detected 'complementary' intent from keyword: '{keyword}'")
            return "complementary"

    # Default: if they're asking about a specific item type they uploaded, they likely want similar
    # e.g., "Do you have any mens shirts" when uploading a shirt
    return "similar"

# ============================================================================
# INITIALIZE RAG SYSTEM
# ============================================================================

logger.info("Initializing clothing RAG system...")
STYLES_DF, EMBEDDINGS = initialize_rag_system()
logger.info(f"Loaded {len(STYLES_DF) if STYLES_DF is not None else 0} clothing items")

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="RetailNext Smart Stylist API V2",
    description="AI fashion assistant with real clothing data and RAG",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message")
    conversation_history: Optional[List[dict]] = Field(default=[], description="Chat history")
    image_base64: Optional[str] = Field(default=None, description="Base64 image")
    return_audio: bool = Field(default=False, description="Return audio response")

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    gender: Optional[str] = Field(default=None, description="Gender filter")
    top_k: int = Field(default=8, description="Number of results")

class OutfitRequest(BaseModel):
    occasion: str = Field(..., description="Occasion or event")
    gender: str = Field(..., description="Gender (Men/Women/Unisex)")
    formality: str = Field(default="casual", description="Formality level")
    color_preference: Optional[str] = Field(default=None, description="Preferred colors")
    max_items: int = Field(default=5, description="Max items in outfit")

class TTSRequest(BaseModel):
    text: str
    use_australian_accent: bool = Field(default=True)

# ============================================================================
# HEALTH & INFO
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": "RetailNext Smart Stylist V2",
        "status": "operational",
        "dataset_size": len(STYLES_DF) if STYLES_DF is not None else 0,
        "demo_mode": DEMO_MODE,
        "models": {
            "chat": GPT_MODEL,
            "transcription": TRANSCRIPTION_MODEL,
            "tts": TTS_MODEL,
            "embedding": EMBEDDING_MODEL
        }
    }

@app.get("/health")
async def health():
    client = get_client()
    return {
        "status": "healthy",
        "demo_mode": DEMO_MODE,
        "openai_connected": client is not None,
        "dataset_loaded": STYLES_DF is not None,
        "dataset_size": len(STYLES_DF) if STYLES_DF is not None else 0,
        "embeddings_ready": EMBEDDINGS is not None,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# SEARCH & DISCOVERY
# ============================================================================

@app.post("/api/search")
async def search_items(request: SearchRequest):
    """
    Search clothing items using semantic RAG search
    """
    try:
        results = search_by_description(
            description=request.query,
            gender=request.gender,
            top_k=request.top_k
        )

        return {
            "query": request.query,
            "results": results,
            "count": len(results)
        }

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/outfit-bundle")
async def generate_outfit(request: OutfitRequest):
    """
    Generate complete outfit recommendation
    """
    try:
        outfit = create_outfit_bundle(
            occasion=request.occasion,
            gender=request.gender,
            df=STYLES_DF,
            embeddings=EMBEDDINGS,
            formality=request.formality,
            color_preference=request.color_preference,
            max_items=request.max_items
        )

        return outfit

    except Exception as e:
        logger.error(f"Outfit generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# VISION & IMAGE ANALYSIS
# ============================================================================

@app.post("/api/analyze-image")
async def analyze_image(
    image: UploadFile = File(...),
    gender: str = Form("Women")
):
    """
    Analyze uploaded clothing image and find matching items
    """
    try:
        image_bytes = await image.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        result = get_matching_items(
            image_base64=image_base64,
            gender=gender,
            top_k=8
        )

        return {
            "analysis": result["analysis"],
            "matching_items": result["matching_items"],
            "count": len(result["matching_items"])
        }

    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-image-base64")
async def analyze_image_base64(
    image_base64: str = Form(...),
    gender: str = Form("Women")
):
    """
    Analyze base64 image and find matching items
    """
    try:
        result = get_matching_items(
            image_base64=image_base64,
            gender=gender,
            top_k=8
        )

        return {
            "analysis": result["analysis"],
            "matching_items": result["matching_items"],
            "count": len(result["matching_items"])
        }

    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CHAT (ORCHESTRATION)
# ============================================================================

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint - orchestrates all AI capabilities
    """
    try:
        result = {
            "text_response": "",
            "audio_response_base64": None,
            "event_context": None,
            "image_analysis": None,
            "recommended_items": [],
            "apis_used": [],
            "search_mode": None
        }

        # Parse event context if present
        event_context = None
        if request.message:
            event_context = parse_event_context(request.message)
            result["event_context"] = event_context
            result["apis_used"].append("GPT-4o (Event Parsing)")

        # Analyze image if provided
        if request.image_base64:
            gender = event_context.get("gender", "Women") if event_context else "Women"

            # Detect user intent: do they want similar items or complementary items?
            search_mode = detect_search_intent(request.message)
            result["search_mode"] = search_mode

            match_result = get_matching_items(
                image_base64=request.image_base64,
                gender=gender,
                top_k=6,
                search_mode=search_mode
            )
            result["image_analysis"] = match_result["analysis"]
            result["recommended_items"] = match_result["matching_items"]
            result["apis_used"].append("GPT-4o (Vision)")
            result["apis_used"].append("text-embedding-3-large (RAG)")

        # Search for items based on query
        elif request.message and event_context:
            query = f"{event_context.get('event_type', '')} {event_context.get('formality_level', '')} {event_context.get('gender', '')}"

            items = search_by_description(
                description=query,
                gender=event_context.get("gender"),
                top_k=8
            )

            result["recommended_items"] = items
            result["apis_used"].append("text-embedding-3-large (RAG)")

        # Generate response text
        response_parts = []
        speech_parts = []  # Separate text for TTS (without item list)

        # Handle image upload response differently
        if result["image_analysis"]:
            analysis = result["image_analysis"]
            article_type = analysis.get("article_type", "item")
            base_colour = analysis.get("base_colour", "")
            style = analysis.get("style_description", "")
            search_mode = result.get("search_mode", "complementary")

            intro = f"G'day! I can see you've uploaded a {base_colour} {article_type}. "
            if style:
                intro += f"Nice {style} piece! "

            # Adjust message based on search mode
            if search_mode == "similar":
                action = "Here are some similar items from our collection."
            else:
                action = "Let me find you some items that would pair perfectly with it."

            response_parts.append(intro + action)
            speech_parts.append(intro + action)

        elif event_context:
            event_type = event_context.get("event_type", "")
            formality = event_context.get("formality_level", "casual")
            # Only mention event type if it's meaningful (not empty, unknown, or generic)
            if event_type and event_type.lower() not in ["unknown", "occasion", ""]:
                intro = f"G'day! Perfect - a {event_type}! Let me find you some brilliant {formality} options."
            else:
                intro = f"G'day! Let me find you some brilliant {formality} options."
            response_parts.append(intro)
            speech_parts.append(intro)

        if result["recommended_items"]:
            count_msg = f"\nI've found {len(result['recommended_items'])} great items that would be perfect:"
            response_parts.append(count_msg)
            speech_parts.append(f" I've found {len(result['recommended_items'])} great items that would be perfect.")

            # Add item list to text response only (not to speech)
            for i, item in enumerate(result["recommended_items"][:5], 1):
                response_parts.append(
                    f"\n{i}. **{item['productDisplayName']}** ({item['baseColour']} {item['articleType']})"
                )

            closing = "\n\nCheck out the recommendations panel for prices and store locations. Would you like me to create a complete outfit from these?"
            response_parts.append(closing)
            speech_parts.append(" Check out the recommendations panel for prices and store locations.")

        result["text_response"] = "".join(response_parts) or "How can I help you find the perfect outfit today?"

        # Generate audio if requested - use speech_parts (without item list) for cleaner audio
        if request.return_audio:
            speech_text = "".join(speech_parts) if speech_parts else result["text_response"]
            if speech_text:
                audio_bytes = text_to_speech_bytes(speech_text)
                if audio_bytes:
                    result["audio_response_base64"] = base64.b64encode(audio_bytes).decode('utf-8')
                    result["apis_used"].append("gpt-4o-mini-tts (Australian TTS)")

        return result

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# VOICE
# ============================================================================

@app.post("/api/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """Transcribe audio to text"""
    try:
        audio_bytes = await audio.read()
        transcript = transcribe_audio_bytes(audio_bytes, audio.filename)

        return {
            "transcript": transcript,
            "model": TRANSCRIPTION_MODEL
        }
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech"""
    try:
        audio_bytes = text_to_speech_bytes(
            text=request.text,
            use_australian_accent=request.use_australian_accent
        )

        if audio_bytes:
            return {
                "audio_base64": base64.b64encode(audio_bytes).decode('utf-8'),
                "format": "mp3"
            }
        else:
            return {
                "audio_base64": None,
                "message": "TTS unavailable"
            }

    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# INVENTORY
# ============================================================================

@app.get("/api/inventory")
async def get_inventory(
    gender: Optional[str] = None,
    article_type: Optional[str] = None,
    color: Optional[str] = None,
    limit: int = 50
):
    """Get inventory items with filters"""
    try:
        df = STYLES_DF.copy()

        if gender:
            df = df[df['gender'].isin([gender, 'Unisex'])]
        if article_type:
            df = df[df['articleType'] == article_type]
        if color:
            df = df[df['baseColour'].str.contains(color, case=False, na=False)]

        items = df.head(limit).to_dict('records')

        # Add mock prices
        for item in items:
            if 'price' not in item:
                item['price'] = int(item['id']) % 200 + 30

        return {
            "items": items,
            "count": len(items),
            "total_in_dataset": len(STYLES_DF)
        }

    except Exception as e:
        logger.error(f"Inventory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("🛍️  RetailNext Smart Stylist API V2")
    logger.info("=" * 60)
    logger.info(f"Dataset Size: {len(STYLES_DF) if STYLES_DF is not None else 0} items")
    logger.info(f"Embeddings: {EMBEDDINGS.shape if EMBEDDINGS is not None else 'None'}")
    logger.info(f"Demo Mode: {DEMO_MODE}")
    logger.info("=" * 60)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
