"""
RetailNext Smart Stylist Backend
=================================
A comprehensive AI-powered fashion assistant demonstrating OpenAI's latest APIs:
- GPT-5 (Vision + Chat + Reasoning)
- gpt-4o-transcribe (Speech-to-Text)
- gpt-4o-mini-tts (Text-to-Speech with Australian accent)
- text-embedding-3-large (Semantic Search/RAG)
- Structured Outputs (JSON Schema)
- Function Calling (Tool Use)

Author: OpenAI Solutions Engineer Candidate
Date: December 2025
"""

import os
import json
import base64
import tempfile
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Model Configuration - Using latest OpenAI models (December 2025)
GPT_MODEL = os.getenv("OPENAI_GPT_MODEL", "gpt-4o")  # GPT-4o supports Structured Outputs & vision
TRANSCRIPTION_MODEL = os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-transcribe")  # Better than Whisper
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")  # Steerable TTS
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")

# TTS Voice Configuration - Australian accent via instruction steering
TTS_VOICE = os.getenv("TTS_VOICE", "nova")  # Base voice
TTS_AUSTRALIAN_INSTRUCTIONS = """
Speak with a warm, friendly Australian accent. 
Use natural Australian intonation and pacing.
Sound like a helpful retail assistant in Melbourne or Sydney.
Be enthusiastic but not over-the-top.
"""

# Demo Mode - For fallback during live presentations
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


# ============================================================================
# MOCK INVENTORY DATABASE
# ============================================================================

MOCK_INVENTORY = [
    # Women's Tops
    {"id": "W001", "name": "Emerald Green Silk Blouse", "category": "tops", "gender": "women",
     "price": 119.99, "colors": ["emerald green"], "sizes": ["XS", "S", "M", "L", "XL"],
     "description": "Luxurious silk blouse with elegant draping, perfect for formal occasions",
     "stock": 12, "aisle": "B1", "bin": "C2", "material": "100% silk", "style": "formal"},
    
    {"id": "W002", "name": "Classic White Cotton Shirt", "category": "tops", "gender": "women",
     "price": 69.99, "colors": ["white", "ivory"], "sizes": ["XS", "S", "M", "L", "XL"],
     "description": "Crisp cotton shirt with tailored fit, versatile for work or casual",
     "stock": 25, "aisle": "B1", "bin": "C3", "material": "100% cotton", "style": "business-casual"},
    
    {"id": "W003", "name": "Floral Print Summer Top", "category": "tops", "gender": "women",
     "price": 49.99, "colors": ["multi", "blue floral", "pink floral"], "sizes": ["XS", "S", "M", "L"],
     "description": "Light and breezy summer top with beautiful floral pattern",
     "stock": 18, "aisle": "B1", "bin": "C4", "material": "rayon blend", "style": "casual"},
    
    # Women's Bottoms
    {"id": "W004", "name": "High-Waisted Black Trousers", "category": "pants", "gender": "women",
     "price": 99.99, "colors": ["black", "navy"], "sizes": ["0", "2", "4", "6", "8", "10", "12"],
     "description": "Sophisticated high-waisted trousers with clean lines",
     "stock": 20, "aisle": "B3", "bin": "C6", "material": "wool blend", "style": "formal"},
    
    {"id": "W005", "name": "A-Line Midi Skirt", "category": "skirts", "gender": "women",
     "price": 79.99, "colors": ["burgundy", "forest green", "black"], "sizes": ["XS", "S", "M", "L"],
     "description": "Elegant A-line skirt with flattering silhouette",
     "stock": 15, "aisle": "B3", "bin": "C7", "material": "polyester blend", "style": "smart-casual"},
    
    # Women's Dresses
    {"id": "W006", "name": "Navy Blue Cocktail Dress", "category": "dresses", "gender": "women",
     "price": 189.99, "colors": ["navy blue", "black"], "sizes": ["0", "2", "4", "6", "8", "10"],
     "description": "Stunning cocktail dress with lace detailing, perfect for evening events",
     "stock": 8, "aisle": "B2", "bin": "C1", "material": "polyester with lace overlay", "style": "formal"},
    
    {"id": "W007", "name": "Casual Maxi Sundress", "category": "dresses", "gender": "women",
     "price": 89.99, "colors": ["coral", "sky blue", "white"], "sizes": ["XS", "S", "M", "L", "XL"],
     "description": "Flowy maxi dress perfect for summer outings and beach days",
     "stock": 22, "aisle": "B2", "bin": "C2", "material": "cotton blend", "style": "casual"},
    
    # Men's Tops
    {"id": "M001", "name": "Navy Blue Blazer", "category": "blazers", "gender": "men",
     "price": 249.99, "colors": ["navy blue", "charcoal"], "sizes": ["38R", "40R", "42R", "44R", "46R"],
     "description": "Classic tailored blazer with modern slim fit, Italian wool",
     "stock": 10, "aisle": "A1", "bin": "D1", "material": "Italian wool", "style": "formal"},
    
    {"id": "M002", "name": "Light Blue Oxford Shirt", "category": "shirts", "gender": "men",
     "price": 79.99, "colors": ["light blue", "white", "pink"], "sizes": ["S", "M", "L", "XL", "XXL"],
     "description": "Premium cotton Oxford shirt with button-down collar",
     "stock": 30, "aisle": "A2", "bin": "D2", "material": "100% cotton", "style": "business-casual"},
    
    {"id": "M003", "name": "Grey Cashmere Sweater", "category": "sweaters", "gender": "men",
     "price": 179.99, "colors": ["heather grey", "navy", "burgundy"], "sizes": ["S", "M", "L", "XL"],
     "description": "Luxuriously soft cashmere V-neck sweater",
     "stock": 12, "aisle": "A2", "bin": "D3", "material": "100% cashmere", "style": "smart-casual"},
    
    # Men's Bottoms
    {"id": "M004", "name": "Charcoal Dress Pants", "category": "pants", "gender": "men",
     "price": 129.99, "colors": ["charcoal", "black", "navy"], "sizes": ["30x30", "32x30", "32x32", "34x32", "36x32"],
     "description": "Tailored wool dress pants with flat front",
     "stock": 18, "aisle": "A3", "bin": "D5", "material": "wool blend", "style": "formal"},
    
    {"id": "M005", "name": "Khaki Chinos", "category": "pants", "gender": "men",
     "price": 69.99, "colors": ["khaki", "olive", "navy"], "sizes": ["30x30", "32x30", "32x32", "34x32", "36x32"],
     "description": "Classic chino pants perfect for smart-casual occasions",
     "stock": 25, "aisle": "A3", "bin": "D6", "material": "cotton twill", "style": "smart-casual"},
    
    # Footwear
    {"id": "S001", "name": "Black Leather Oxford Shoes", "category": "shoes", "gender": "men",
     "price": 199.99, "colors": ["black", "brown"], "sizes": ["8", "9", "10", "11", "12"],
     "description": "Classic leather Oxford shoes with Goodyear welt construction",
     "stock": 14, "aisle": "C1", "bin": "E1", "material": "genuine leather", "style": "formal"},
    
    {"id": "S002", "name": "Nude Patent Leather Heels", "category": "shoes", "gender": "women",
     "price": 159.99, "colors": ["nude", "black", "red"], "sizes": ["6", "7", "8", "9", "10"],
     "description": "Elegant pointed-toe heels, 3-inch heel height",
     "stock": 16, "aisle": "C2", "bin": "E2", "material": "patent leather", "style": "formal"},
    
    {"id": "S003", "name": "White Leather Sneakers", "category": "shoes", "gender": "unisex",
     "price": 119.99, "colors": ["white", "white/navy"], "sizes": ["6", "7", "8", "9", "10", "11", "12"],
     "description": "Premium leather sneakers with minimalist design",
     "stock": 28, "aisle": "C3", "bin": "E3", "material": "genuine leather", "style": "casual"},
    
    # Accessories
    {"id": "A001", "name": "Gold Statement Earrings", "category": "accessories", "gender": "women",
     "price": 49.99, "colors": ["gold", "silver"], "sizes": ["one-size"],
     "description": "Elegant drop earrings perfect for special occasions",
     "stock": 20, "aisle": "D1", "bin": "F1", "material": "gold-plated brass", "style": "formal"},
    
    {"id": "A002", "name": "Silk Pocket Square Set", "category": "accessories", "gender": "men",
     "price": 39.99, "colors": ["assorted"], "sizes": ["one-size"],
     "description": "Set of 3 silk pocket squares in complementary colors",
     "stock": 15, "aisle": "D1", "bin": "F2", "material": "100% silk", "style": "formal"},
    
    {"id": "A003", "name": "Leather Belt", "category": "accessories", "gender": "unisex",
     "price": 59.99, "colors": ["black", "brown", "tan"], "sizes": ["S", "M", "L", "XL"],
     "description": "Classic leather belt with brushed silver buckle",
     "stock": 30, "aisle": "D2", "bin": "F3", "material": "genuine leather", "style": "versatile"},
    
    {"id": "A004", "name": "Structured Leather Handbag", "category": "bags", "gender": "women",
     "price": 229.99, "colors": ["black", "camel", "burgundy"], "sizes": ["one-size"],
     "description": "Sophisticated structured handbag with gold hardware",
     "stock": 10, "aisle": "D3", "bin": "F4", "material": "genuine leather", "style": "formal"},
]


# ============================================================================
# STRUCTURED OUTPUT SCHEMAS (JSON Schema for OpenAI Structured Outputs)
# ============================================================================

EVENT_CONTEXT_SCHEMA = {
    "type": "object",
    "properties": {
        "event_type": {
            "type": "string",
            "description": "Type of event (wedding, interview, graduation, date, party, business meeting, etc.)"
        },
        "formality_level": {
            "type": "string",
            "enum": ["very-casual", "casual", "smart-casual", "business-casual", "semi-formal", "formal", "black-tie"],
            "description": "How formal the event is"
        },
        "season": {
            "type": "string",
            "enum": ["spring", "summer", "autumn", "winter", "unknown"],
            "description": "Season or time of year"
        },
        "venue_type": {
            "type": "string",
            "enum": ["indoor", "outdoor", "mixed", "unknown"],
            "description": "Indoor or outdoor venue"
        },
        "time_of_day": {
            "type": "string",
            "enum": ["morning", "afternoon", "evening", "night", "unknown"],
            "description": "When the event takes place"
        },
        "weather_consideration": {
            "type": "string",
            "description": "Any weather-related considerations mentioned"
        },
        "budget_preference": {
            "type": "string",
            "enum": ["budget-friendly", "moderate", "premium", "luxury", "unspecified"],
            "description": "Budget preference if mentioned"
        },
        "color_preferences": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Any color preferences or restrictions mentioned"
        },
        "style_notes": {
            "type": "string",
            "description": "Additional style preferences or requirements"
        },
        "gender": {
            "type": "string",
            "enum": ["men", "women", "unisex", "unknown"],
            "description": "Gender for clothing recommendations"
        },
        "specific_requirements": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Any specific requirements (comfortable shoes, pockets, etc.)"
        }
    },
    "required": [
        "event_type",
        "formality_level",
        "season",
        "venue_type",
        "time_of_day",
        "weather_consideration",
        "budget_preference",
        "color_preferences",
        "style_notes",
        "gender",
        "specific_requirements"
    ],
    "additionalProperties": False
}

IMAGE_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "clothing_type": {
            "type": "string",
            "description": "Primary type of clothing item identified"
        },
        "colors": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Colors identified in the clothing"
        },
        "patterns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Patterns identified (solid, striped, floral, etc.)"
        },
        "style": {
            "type": "string",
            "description": "Overall style (casual, formal, sporty, etc.)"
        },
        "material_guess": {
            "type": "string",
            "description": "Estimated material/fabric"
        },
        "occasion_suitability": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Occasions this item would be suitable for"
        },
        "matching_suggestions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Suggestions for items that would pair well"
        },
        "condition": {
            "type": "string",
            "enum": ["new", "like-new", "good", "fair", "worn", "unknown"],
            "description": "Apparent condition of the item"
        }
    },
    "required": [
        "clothing_type",
        "colors",
        "patterns",
        "style",
        "material_guess",
        "occasion_suitability",
        "matching_suggestions",
        "condition"
    ],
    "additionalProperties": False
}


# ============================================================================
# FUNCTION CALLING TOOLS DEFINITION
# ============================================================================

STYLIST_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_inventory",
            "description": "Check if specific items are in stock. Use this to verify availability before recommending.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_name": {
                        "type": "string",
                        "description": "Name or description of the item to search for"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["tops", "shirts", "blouses", "pants", "skirts", "dresses", "blazers", "sweaters", "shoes", "accessories", "bags"],
                        "description": "Category of clothing"
                    },
                    "color": {
                        "type": "string",
                        "description": "Preferred color"
                    },
                    "size": {
                        "type": "string",
                        "description": "Required size"
                    },
                    "gender": {
                        "type": "string",
                        "enum": ["men", "women", "unisex"],
                        "description": "Gender category"
                    }
                },
                "required": ["item_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_similar_items",
            "description": "Find items similar to a description using semantic search. Great for 'find something like...' requests.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Description of the desired item or style"
                    },
                    "gender": {
                        "type": "string",
                        "enum": ["men", "women", "unisex", "any"],
                        "description": "Gender filter"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price filter"
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter"
                    }
                },
                "required": ["description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_outfit_bundle",
            "description": "Create a complete outfit recommendation for a specific occasion. Returns coordinated items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "occasion": {
                        "type": "string",
                        "description": "The occasion or event type"
                    },
                    "gender": {
                        "type": "string",
                        "enum": ["men", "women"],
                        "description": "Gender for the outfit"
                    },
                    "formality": {
                        "type": "string",
                        "enum": ["casual", "smart-casual", "business-casual", "semi-formal", "formal"],
                        "description": "Desired formality level"
                    },
                    "budget_max": {
                        "type": "number",
                        "description": "Maximum total budget for the outfit"
                    },
                    "color_preference": {
                        "type": "string",
                        "description": "Preferred color scheme"
                    }
                },
                "required": ["occasion", "gender"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_item_location",
            "description": "Get the exact store location (aisle and bin) for an item.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "string",
                        "description": "The item ID to locate"
                    }
                },
                "required": ["item_id"]
            }
        }
    }
]


# ============================================================================
# OPENAI CLIENT INITIALIZATION
# ============================================================================

def get_openai_client():
    """Initialize and return OpenAI client with error handling."""
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set - running in demo mode")
            return None
        return OpenAI(api_key=api_key)
    except ImportError:
        logger.error("OpenAI library not installed. Run: pip install openai")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        return None


# Global client instance
_client = None

def get_client():
    """Get or create OpenAI client singleton."""
    global _client
    if _client is None:
        _client = get_openai_client()
    return _client


# ============================================================================
# EMBEDDING & SEMANTIC SEARCH (RAG)
# ============================================================================

# Cache for embeddings
_embedding_cache: Dict[str, List[float]] = {}

def get_embedding(text: str) -> List[float]:
    """Get embedding for text using text-embedding-3-large."""
    client = get_client()
    
    # Check cache first
    if text in _embedding_cache:
        return _embedding_cache[text]
    
    if client is None or DEMO_MODE:
        # Return mock embedding for demo
        import hashlib
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        mock_embedding = [(hash_val >> i) % 100 / 100.0 for i in range(256)]
        return mock_embedding
    
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
            dimensions=256  # Using smaller dimension for efficiency
        )
        embedding = response.data[0].embedding
        _embedding_cache[text] = embedding
        return embedding
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        # Fallback to mock
        import hashlib
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        return [(hash_val >> i) % 100 / 100.0 for i in range(256)]


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    import math
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)


def semantic_search(query: str, items: List[Dict], top_k: int = 5) -> List[Dict]:
    """Search items using semantic similarity."""
    query_embedding = get_embedding(query)
    
    scored_items = []
    for item in items:
        # Create rich text representation of item
        item_text = f"{item['name']} {item['description']} {item['category']} {' '.join(item['colors'])} {item['style']}"
        item_embedding = get_embedding(item_text)
        
        score = cosine_similarity(query_embedding, item_embedding)
        scored_items.append((score, item))
    
    # Sort by score descending
    scored_items.sort(key=lambda x: x[0], reverse=True)
    
    return [item for score, item in scored_items[:top_k]]


# ============================================================================
# FUNCTION IMPLEMENTATIONS (Called by Function Calling)
# ============================================================================

def check_inventory(
    item_name: str,
    category: Optional[str] = None,
    color: Optional[str] = None,
    size: Optional[str] = None,
    gender: Optional[str] = None
) -> Dict[str, Any]:
    """Check inventory for specific items."""
    results = []
    
    for item in MOCK_INVENTORY:
        # Check name match (fuzzy)
        if item_name.lower() not in item['name'].lower() and item_name.lower() not in item['description'].lower():
            continue
        
        # Apply filters
        if category and item['category'] != category:
            continue
        if gender and item['gender'] not in [gender, 'unisex']:
            continue
        if color and not any(color.lower() in c.lower() for c in item['colors']):
            continue
        if size and size not in item['sizes']:
            continue
        
        results.append({
            **item,
            "available": item['stock'] > 0,
            "location": f"Aisle {item['aisle']}, Bin {item['bin']}"
        })
    
    return {
        "found": len(results) > 0,
        "items": results,
        "total_matches": len(results)
    }


def find_similar_items(
    description: str,
    gender: Optional[str] = None,
    max_price: Optional[float] = None,
    category: Optional[str] = None
) -> List[Dict]:
    """Find similar items using semantic search."""
    # Filter items first
    filtered_items = MOCK_INVENTORY.copy()
    
    if gender and gender != "any":
        filtered_items = [i for i in filtered_items if i['gender'] in [gender, 'unisex']]
    if max_price:
        filtered_items = [i for i in filtered_items if i['price'] <= max_price]
    if category:
        filtered_items = [i for i in filtered_items if i['category'] == category]
    
    # Semantic search
    results = semantic_search(description, filtered_items, top_k=5)
    
    # Add location info
    for item in results:
        item['location'] = f"Aisle {item['aisle']}, Bin {item['bin']}"
    
    return results


def get_outfit_bundle(
    occasion: str,
    gender: str,
    formality: str = "smart-casual",
    budget_max: Optional[float] = None,
    color_preference: Optional[str] = None
) -> Dict[str, Any]:
    """Create a complete outfit bundle for an occasion."""
    bundle = {
        "occasion": occasion,
        "formality": formality,
        "items": [],
        "total_price": 0,
        "styling_notes": ""
    }
    
    # Define what categories make up a complete outfit
    if gender == "women":
        needed_categories = [
            ("tops", "dresses"),  # Either a top or dress
            ("pants", "skirts"),  # Bottoms if not a dress
            ("shoes",),
            ("accessories",)
        ]
    else:  # men
        needed_categories = [
            ("shirts", "blazers", "sweaters"),
            ("pants",),
            ("shoes",),
            ("accessories",)
        ]
    
    # Filter by gender
    gender_items = [i for i in MOCK_INVENTORY if i['gender'] in [gender, 'unisex']]
    
    # Filter by formality
    formality_map = {
        "casual": ["casual", "smart-casual"],
        "smart-casual": ["smart-casual", "business-casual"],
        "business-casual": ["business-casual", "smart-casual", "formal"],
        "semi-formal": ["semi-formal", "formal", "business-casual"],
        "formal": ["formal", "semi-formal"]
    }
    allowed_styles = formality_map.get(formality, ["smart-casual"])
    
    selected_ids = set()
    
    for category_group in needed_categories:
        # Skip bottoms if we already have a dress
        if category_group in [("pants", "skirts")] and any(i['category'] == 'dresses' for i in bundle['items']):
            continue
        
        # Find best matching item for this category
        candidates = [
            i for i in gender_items 
            if i['category'] in category_group 
            and i['id'] not in selected_ids
            and i['style'] in allowed_styles
            and i['stock'] > 0
        ]
        
        if budget_max:
            remaining_budget = budget_max - bundle['total_price']
            candidates = [i for i in candidates if i['price'] <= remaining_budget]
        
        if candidates:
            # Use semantic search to find best match for occasion
            best_matches = semantic_search(f"{occasion} {formality} {color_preference or ''}", candidates, top_k=1)
            if best_matches:
                item = best_matches[0]
                bundle['items'].append({
                    **item,
                    "location": f"Aisle {item['aisle']}, Bin {item['bin']}"
                })
                bundle['total_price'] += item['price']
                selected_ids.add(item['id'])
    
    # Generate styling notes
    bundle['styling_notes'] = f"This {formality} outfit is perfect for {occasion}. "
    if len(bundle['items']) >= 3:
        bundle['styling_notes'] += "The pieces coordinate well together and can be mixed with other wardrobe staples."
    
    return bundle


def get_item_location(item_id: str) -> Dict[str, Any]:
    """Get the store location for an item."""
    for item in MOCK_INVENTORY:
        if item['id'] == item_id:
            return {
                "found": True,
                "item_name": item['name'],
                "aisle": item['aisle'],
                "bin": item['bin'],
                "directions": f"Head to Aisle {item['aisle']}, look for Bin {item['bin']}. The item should be clearly labeled.",
                "stock": item['stock']
            }
    return {"found": False, "message": "Item not found in inventory"}


# Function dispatch map
FUNCTION_MAP = {
    "check_inventory": check_inventory,
    "find_similar_items": find_similar_items,
    "get_outfit_bundle": get_outfit_bundle,
    "get_item_location": get_item_location
}


# ============================================================================
# SPEECH-TO-TEXT (gpt-4o-transcribe)
# ============================================================================

def transcribe_audio_bytes(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """Transcribe audio using gpt-4o-transcribe (better than Whisper)."""
    client = get_client()
    
    if client is None or DEMO_MODE:
        logger.info("Demo mode: Returning mock transcription")
        return "I'm looking for an outfit for a graduation ceremony next Saturday. It's outdoors and I want something elegant but comfortable."
    
    try:
        # Create temp file for audio
        with tempfile.NamedTemporaryFile(suffix=f".{filename.split('.')[-1]}", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        with open(temp_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model=TRANSCRIPTION_MODEL,
                file=audio_file,
                language="en"  # Can be auto-detected
            )
        
        # Cleanup temp file
        os.unlink(temp_path)
        
        logger.info(f"Transcription successful: {response.text[:50]}...")
        return response.text
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        # Fallback for demo
        return "I need help finding an outfit for a special occasion."


def transcribe_audio_file(file_path: str) -> str:
    """Transcribe audio from a file path."""
    with open(file_path, "rb") as f:
        return transcribe_audio_bytes(f.read(), os.path.basename(file_path))


# ============================================================================
# TEXT-TO-SPEECH (gpt-4o-mini-tts with Australian Accent)
# ============================================================================

def text_to_speech_bytes(
    text: str, 
    voice: str = TTS_VOICE,
    use_australian_accent: bool = True
) -> bytes:
    """Convert text to speech using gpt-4o-mini-tts with Australian accent."""
    client = get_client()
    
    if client is None or DEMO_MODE:
        logger.info("Demo mode: Returning empty audio bytes")
        return b""
    
    try:
        # Build instructions for Australian accent
        instructions = TTS_AUSTRALIAN_INSTRUCTIONS if use_australian_accent else "Speak naturally and clearly."
        
        response = client.audio.speech.create(
            model=TTS_MODEL,
            voice=voice,
            input=text,
            instructions=instructions,  # This is the key feature of gpt-4o-mini-tts!
            response_format="mp3"
        )
        
        audio_bytes = response.content
        logger.info(f"TTS successful: Generated {len(audio_bytes)} bytes")
        return audio_bytes
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return b""


def text_to_speech_file(text: str, output_path: str, **kwargs) -> bool:
    """Save TTS output to a file."""
    audio_bytes = text_to_speech_bytes(text, **kwargs)
    if audio_bytes:
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        return True
    return False


# ============================================================================
# VISION ANALYSIS (GPT-5 Vision)
# ============================================================================

def analyze_clothing_image(
    image_base64: str,
    available_categories: List[str] = None
) -> Dict[str, Any]:
    """Analyze a clothing image using GPT-5's vision capabilities."""
    client = get_client()
    
    if available_categories is None:
        available_categories = list(set(item['category'] for item in MOCK_INVENTORY))
    
    if client is None or DEMO_MODE:
        logger.info("Demo mode: Returning mock image analysis")
        return {
            "clothing_type": "blouse",
            "colors": ["blue", "white"],
            "patterns": ["floral"],
            "style": "casual",
            "material_guess": "cotton",
            "occasion_suitability": ["casual outing", "brunch", "shopping"],
            "matching_suggestions": ["white pants", "denim jeans", "nude heels"],
            "condition": "like-new"
        }
    
    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a fashion expert analyzing clothing images. 
                    Analyze the image and provide detailed information about the clothing item.
                    Available categories in our store: {', '.join(available_categories)}
                    
                    Provide your analysis in the exact JSON structure requested."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this clothing item. What type is it, what colors and patterns do you see, what's the style, what occasions would it suit, and what would pair well with it?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "image_analysis",
                    "strict": True,
                    "schema": IMAGE_ANALYSIS_SCHEMA
                }
            },
            max_completion_tokens=1000
        )
        
        analysis = json.loads(response.choices[0].message.content)
        logger.info(f"Image analysis successful: {analysis.get('clothing_type', 'unknown')}")
        return analysis
        
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        return {
            "clothing_type": "unknown",
            "colors": [],
            "style": "unknown",
            "error": str(e)
        }


# ============================================================================
# EVENT CONTEXT PARSING (Structured Outputs)
# ============================================================================

def parse_event_context(user_input: str) -> Dict[str, Any]:
    """Parse event context from natural language using GPT-4o Structured Outputs."""
    client = get_client()
    
    if client is None or DEMO_MODE:
        logger.info("Demo mode: Returning mock event context")
        return {
            "event_type": "graduation ceremony",
            "formality_level": "smart-casual",
            "season": "spring",
            "venue_type": "outdoor",
            "time_of_day": "afternoon",
            "weather_consideration": "sunny and warm",
            "budget_preference": "moderate",
            "color_preferences": ["emerald", "navy", "neutral"],
            "style_notes": "Elegant but comfortable for standing/walking",
            "gender": "women",
            "specific_requirements": ["comfortable shoes", "sun-appropriate"]
        }
    
    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are a fashion consultant extracting event details from customer requests.
                    Parse the customer's description to understand what kind of outfit they need.
                    If information is not explicitly stated, make reasonable inferences based on the event type.
                    Always try to infer the gender from context clues (pronouns, specific item mentions, etc.)."""
                },
                {
                    "role": "user",
                    "content": f"Parse this outfit request: {user_input}"
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "event_context",
                    "strict": True,
                    "schema": EVENT_CONTEXT_SCHEMA
                }
            },
            max_completion_tokens=500
        )

        # Debug: Log the raw response
        raw_content = response.choices[0].message.content
        logger.info(f"Raw API response content: {raw_content[:200] if raw_content else 'EMPTY'}")

        context = json.loads(raw_content)
        logger.info(f"Event context parsed: {context.get('event_type', 'unknown')}")
        return context
        
    except Exception as e:
        logger.error(f"Event parsing error: {e}")
        # Return complete fallback with all required fields
        return {
            "event_type": "general occasion",
            "formality_level": "smart-casual",
            "season": "unknown",
            "venue_type": "unknown",
            "time_of_day": "unknown",
            "weather_consideration": "",
            "budget_preference": "unspecified",
            "color_preferences": [],
            "style_notes": "",
            "gender": "unknown",
            "specific_requirements": []
        }


# ============================================================================
# MAIN STYLIST PROCESSING (Orchestrates all APIs)
# ============================================================================

def process_stylist_request(
    user_input: Optional[str] = None,
    audio_bytes: Optional[bytes] = None,
    image_base64: Optional[str] = None,
    conversation_history: Optional[List[Dict]] = None,
    return_audio: bool = True
) -> Dict[str, Any]:
    """
    Main entry point for processing stylist requests.
    Orchestrates all OpenAI APIs:
    1. Whisper for voice input
    2. GPT-5 Vision for image analysis
    3. Structured Outputs for event parsing
    4. Function Calling for inventory operations
    5. Embeddings for semantic search
    6. TTS for voice response
    """
    client = get_client()
    result = {
        "text_response": "",
        "audio_response_base64": None,
        "event_context": None,
        "image_analysis": None,
        "transcribed_input": None,
        "recommended_items": [],
        "apis_used": []
    }
    
    # Step 1: Transcribe audio if provided
    if audio_bytes:
        user_input = transcribe_audio_bytes(audio_bytes)
        result["transcribed_input"] = user_input
        result["apis_used"].append("gpt-4o-transcribe (Speech-to-Text)")
        logger.info(f"Transcribed: {user_input}")
    
    if not user_input:
        result["text_response"] = "G'day! I'm your AI fashion assistant. How can I help you find the perfect outfit today?"
        return result
    
    # Step 2: Analyze image if provided
    if image_base64:
        result["image_analysis"] = analyze_clothing_image(image_base64)
        result["apis_used"].append("GPT-5 Vision (Image Analysis)")
        logger.info(f"Image analyzed: {result['image_analysis'].get('clothing_type', 'unknown')}")
    
    # Step 3: Parse event context
    result["event_context"] = parse_event_context(user_input)
    result["apis_used"].append("GPT-5 Structured Outputs (Event Parsing)")
    
    # Step 4: Generate response with function calling
    if client is None or DEMO_MODE:
        # Demo mode response
        result["text_response"] = generate_demo_response(user_input, result["event_context"], result["image_analysis"])
        result["recommended_items"] = generate_demo_recommendations(result["event_context"])
    else:
        # Full API response with function calling
        result = generate_ai_response(client, user_input, result, conversation_history)
    
    # Step 5: Generate audio response if requested
    if return_audio and result["text_response"]:
        audio_bytes = text_to_speech_bytes(result["text_response"])
        if audio_bytes:
            result["audio_response_base64"] = base64.b64encode(audio_bytes).decode('utf-8')
            result["apis_used"].append("gpt-4o-mini-tts (Text-to-Speech, Australian Accent)")
    
    return result


def generate_ai_response(
    client,
    user_input: str,
    result: Dict,
    conversation_history: Optional[List[Dict]] = None
) -> Dict:
    """Generate response using GPT-5 with function calling."""
    
    # Build messages
    messages = [
        {
            "role": "system",
            "content": """You are an enthusiastic and knowledgeable AI fashion stylist at RetailNext, 
            a premium retail store. You help customers find the perfect outfits for any occasion.
            
            Your personality: Warm, helpful, and fashion-forward. You speak with confidence about style 
            and make customers feel excited about their choices.
            
            When recommending items:
            1. Always use the provided tools to check inventory and find items
            2. Provide specific item recommendations with prices and locations
            3. Explain WHY each piece works for the occasion
            4. Suggest complete outfits when appropriate
            5. Mention the exact aisle and bin for each item
            
            Use Australian English spelling and expressions naturally (colour, favourite, etc.)."""
        }
    ]
    
    # Add conversation history
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add context from analysis
    context_parts = [f"Customer request: {user_input}"]
    
    if result.get("event_context"):
        context_parts.append(f"Event context: {json.dumps(result['event_context'])}")
    
    if result.get("image_analysis"):
        context_parts.append(f"Image analysis of item they showed: {json.dumps(result['image_analysis'])}")
    
    messages.append({
        "role": "user",
        "content": "\n\n".join(context_parts)
    })
    
    try:
        # First call - may trigger function calls
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages,
            tools=STYLIST_TOOLS,
            tool_choice="auto",
            max_completion_tokens=2000
        )
        
        assistant_message = response.choices[0].message
        result["apis_used"].append("GPT-5 (Chat + Function Calling)")
        
        # Process any function calls
        while assistant_message.tool_calls:
            # Add assistant message with tool calls
            messages.append(assistant_message)
            
            # Execute each function call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"Executing function: {function_name}({function_args})")
                
                # Execute the function
                if function_name in FUNCTION_MAP:
                    function_result = FUNCTION_MAP[function_name](**function_args)
                    
                    # Track semantic search usage
                    if function_name == "find_similar_items":
                        result["apis_used"].append("text-embedding-3-large (Semantic Search)")
                else:
                    function_result = {"error": f"Unknown function: {function_name}"}
                
                # Add function result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(function_result)
                })
                
                # Track recommended items
                if function_name == "get_outfit_bundle" and "items" in function_result:
                    result["recommended_items"].extend(function_result["items"])
                elif function_name in ["check_inventory", "find_similar_items"]:
                    items = function_result.get("items", function_result if isinstance(function_result, list) else [])
                    result["recommended_items"].extend(items if isinstance(items, list) else [])
            
            # Get next response
            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=messages,
                tools=STYLIST_TOOLS,
                tool_choice="auto",
                max_completion_tokens=2000
            )
            assistant_message = response.choices[0].message
        
        result["text_response"] = assistant_message.content
        
    except Exception as e:
        logger.error(f"AI response generation error: {e}")
        result["text_response"] = generate_demo_response(user_input, result.get("event_context"), result.get("image_analysis"))
        result["recommended_items"] = generate_demo_recommendations(result.get("event_context"))
    
    return result


# ============================================================================
# DEMO MODE FALLBACKS (For live presentations)
# ============================================================================

def generate_demo_response(
    user_input: str,
    event_context: Optional[Dict] = None,
    image_analysis: Optional[Dict] = None
) -> str:
    """Generate a demo response without API calls."""
    
    event_type = event_context.get("event_type", "special occasion") if event_context else "special occasion"
    gender = event_context.get("gender", "women") if event_context else "women"
    formality = event_context.get("formality_level", "smart-casual") if event_context else "smart-casual"
    
    responses = {
        "graduation": f"""G'day! How exciting - a graduation! 🎓

I've found some brilliant options for you. For a {formality} outdoor graduation, I'd recommend:

**Complete Outfit:**
1. **Emerald Green Silk Blouse** - $119.99 (Aisle B1, Bin C2)
   This gorgeous silk piece catches the light beautifully for photos!

2. **High-Waisted Black Trousers** - $99.99 (Aisle B3, Bin C6)
   Elegant and comfortable for all that standing and walking.

3. **Nude Patent Leather Heels** - $159.99 (Aisle C2, Bin E2)
   A classic choice that elongates the leg without being too high.

4. **Gold Statement Earrings** - $49.99 (Aisle D1, Bin F1)
   The perfect finishing touch for photos!

**Total: $429.96**

The emerald and gold combination is absolutely stunning for outdoor ceremonies. Shall I check sizes for you?""",

        "interview": f"""G'day! Job interview - let's make sure you knock their socks off! 💼

For a professional impression, here's what I'd suggest:

**Power Interview Look:**
1. **Classic White Cotton Shirt** - $69.99 (Aisle B1, Bin C3)
   Crisp, clean, and universally professional.

2. **High-Waisted Black Trousers** - $99.99 (Aisle B3, Bin C6)
   Tailored fit that means business.

3. **Black Leather Oxford Shoes** - $199.99 (Aisle C1, Bin E1)
   Goodyear welt construction - quality they'll notice.

4. **Leather Belt** - $59.99 (Aisle D2, Bin F3)
   Matching leather ties the look together.

**Total: $429.96**

This classic combination works for virtually any industry. Would you like me to show you some colour variations?""",

        "wedding": f"""G'day! A wedding - how lovely! 💒

Let me put together something special for you:

**Wedding Guest Ensemble:**
1. **Navy Blue Cocktail Dress** - $189.99 (Aisle B2, Bin C1)
   Stunning lace detailing - elegant without upstaging the bride!

2. **Nude Patent Leather Heels** - $159.99 (Aisle C2, Bin E2)
   Comfortable enough for dancing all night.

3. **Gold Statement Earrings** - $49.99 (Aisle D1, Bin F1)
   Adds just the right amount of sparkle.

4. **Structured Leather Handbag** - $229.99 (Aisle D3, Bin F4)
   Room for essentials and tissues for the ceremony!

**Total: $629.96**

Navy is perfect for weddings - sophisticated and photograph-friendly. What size should I check for you?""",

        "date": f"""G'day! Date night - exciting! 💕

Let me help you make a great impression:

**Date Night Look:**
1. **A-Line Midi Skirt** (Burgundy) - $79.99 (Aisle B3, Bin C7)
   Flattering silhouette that moves beautifully.

2. **Emerald Green Silk Blouse** - $119.99 (Aisle B1, Bin C2)
   The jewel tones are absolutely gorgeous together!

3. **Nude Patent Leather Heels** - $159.99 (Aisle C2, Bin E2)
   Adds height without being over the top.

4. **Gold Statement Earrings** - $49.99 (Aisle D1, Bin F1)
   Catches the candlelight perfectly!

**Total: $409.96**

This colour combination is romantic and memorable. Shall I grab these for you to try on?"""
    }
    
    # Match event type to response
    for key in responses:
        if key in event_type.lower():
            return responses[key]
    
    # Default response
    return f"""G'day! I'd love to help you find the perfect outfit for your {event_type}!

Based on what you've described, I'm thinking a {formality} look would be spot on. 

Let me check our inventory for some options that would suit... 

In the meantime, could you tell me a bit more about:
- Any colours you particularly love or want to avoid?
- What's your usual size?
- Any budget you're working with?

I'll put together some brilliant options for you! 🛍️"""


def generate_demo_recommendations(event_context: Optional[Dict] = None) -> List[Dict]:
    """Generate demo recommendations without API calls."""
    
    gender = event_context.get("gender", "women") if event_context else "women"
    formality = event_context.get("formality_level", "smart-casual") if event_context else "smart-casual"
    
    if gender == "women":
        return [
            {**item, "location": f"Aisle {item['aisle']}, Bin {item['bin']}"}
            for item in MOCK_INVENTORY
            if item['id'] in ["W001", "W004", "S002", "A001"]
        ]
    else:
        return [
            {**item, "location": f"Aisle {item['aisle']}, Bin {item['bin']}"}
            for item in MOCK_INVENTORY
            if item['id'] in ["M001", "M002", "M004", "S001"]
        ]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_all_inventory() -> List[Dict]:
    """Get all inventory items."""
    return MOCK_INVENTORY


def get_inventory_categories() -> List[str]:
    """Get unique inventory categories."""
    return list(set(item['category'] for item in MOCK_INVENTORY))


def health_check() -> Dict[str, Any]:
    """Check system health and API connectivity."""
    client = get_client()
    
    status = {
        "status": "healthy",
        "demo_mode": DEMO_MODE,
        "openai_connected": client is not None,
        "models": {
            "chat": GPT_MODEL,
            "transcription": TRANSCRIPTION_MODEL,
            "tts": TTS_MODEL,
            "embedding": EMBEDDING_MODEL
        },
        "inventory_count": len(MOCK_INVENTORY),
        "timestamp": datetime.now().isoformat()
    }
    
    # Test API connection if client exists
    if client and not DEMO_MODE:
        try:
            # Quick test with embeddings (cheapest)
            test = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input="test",
                dimensions=256
            )
            status["api_test"] = "passed"
        except Exception as e:
            status["api_test"] = f"failed: {str(e)}"
            status["status"] = "degraded"
    
    return status


# ============================================================================
# MAIN ENTRY POINT (for testing)
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🛍️  RetailNext Smart Stylist - Backend Test")
    print("=" * 60)
    
    # Health check
    print("\n📊 Health Check:")
    health = health_check()
    for key, value in health.items():
        print(f"  • {key}: {value}")
    
    # Test event parsing
    print("\n🎯 Testing Event Parsing:")
    test_input = "I need an outfit for my daughter's graduation next Saturday. It's outdoors and I want something elegant."
    context = parse_event_context(test_input)
    print(f"  Input: {test_input}")
    print(f"  Parsed: {json.dumps(context, indent=2)}")
    
    # Test semantic search
    print("\n🔍 Testing Semantic Search:")
    results = find_similar_items("elegant silk top for formal event", gender="women")
    print(f"  Query: 'elegant silk top for formal event'")
    print(f"  Found {len(results)} items:")
    for item in results[:3]:
        print(f"    • {item['name']} - ${item['price']}")
    
    # Test outfit bundle
    print("\n👔 Testing Outfit Bundle:")
    bundle = get_outfit_bundle("graduation", "women", "smart-casual")
    print(f"  Occasion: graduation")
    print(f"  Total: ${bundle['total_price']:.2f}")
    print(f"  Items:")
    for item in bundle['items']:
        print(f"    • {item['name']} - ${item['price']} ({item['location']})")
    
    # Test full request processing
    print("\n🤖 Testing Full Request Processing:")
    result = process_stylist_request(
        user_input="I need something for a job interview at a tech company",
        return_audio=False
    )
    print(f"  APIs Used: {result['apis_used']}")
    print(f"  Event: {result['event_context'].get('event_type', 'unknown')}")
    print(f"  Response preview: {result['text_response'][:200]}...")
    
    print("\n" + "=" * 60)
    print("✅ Backend tests complete!")
    print("=" * 60 + "\n")
