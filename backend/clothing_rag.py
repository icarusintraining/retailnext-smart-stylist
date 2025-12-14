"""
RetailNext Smart Stylist - RAG Implementation
Based on OpenAI Cookbook's outfit assistant approach
Uses real clothing dataset with embeddings for semantic search
"""

import os
import json
import base64
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

GPT_MODEL = os.getenv("OPENAI_GPT_MODEL", "gpt-4o")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
EMBEDDING_DIMENSIONS = 256  # Smaller for efficiency

# Image base URL
IMAGE_BASE_URL = "https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/data/sample_clothes/sample_images"

# ============================================================================
# DATA LOADING
# ============================================================================

_styles_df = None
_embeddings_cache = None

def load_clothing_data() -> pd.DataFrame:
    """Load the clothing dataset from CSV"""
    global _styles_df

    if _styles_df is not None:
        return _styles_df

    csv_path = os.path.join(os.path.dirname(__file__), 'sample_styles.csv')

    try:
        _styles_df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(_styles_df)} clothing items from dataset")

        # Add image URL column
        _styles_df['imageUrl'] = _styles_df['id'].apply(
            lambda x: f"{IMAGE_BASE_URL}/{x}.jpg"
        )

        # Create searchable text for embeddings
        _styles_df['searchText'] = _styles_df.apply(
            lambda row: f"{row['productDisplayName']} {row['articleType']} {row['baseColour']} "
                       f"{row['season']} {row['usage']} {row['gender']} {row['masterCategory']} "
                       f"{row['subCategory']}",
            axis=1
        )

        return _styles_df
    except FileNotFoundError:
        logger.error(f"Could not find sample_styles.csv at {csv_path}")
        return pd.DataFrame()

# ============================================================================
# EMBEDDING GENERATION (Based on Cookbook)
# ============================================================================

def get_openai_client():
    """Get OpenAI client instance"""
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        return OpenAI(api_key=api_key)
    except ImportError:
        logger.error("OpenAI library not installed")
        return None

def embed_texts_batch(texts: List[str], client) -> List[List[float]]:
    """
    Embed a batch of texts using OpenAI embeddings API
    Based on cookbook's embed_corpus function
    """
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
            dimensions=EMBEDDING_DIMENSIONS
        )
        return [item.embedding for item in response.data]
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        # Return mock embeddings as fallback
        return [[0.0] * EMBEDDING_DIMENSIONS for _ in texts]

def generate_embeddings(df: pd.DataFrame, batch_size: int = 64, num_workers: int = 4) -> np.ndarray:
    """
    Generate embeddings for all products with parallel processing
    Based on cookbook's approach
    """
    global _embeddings_cache

    if _embeddings_cache is not None:
        return _embeddings_cache

    client = get_openai_client()
    if client is None:
        logger.warning("No OpenAI client - using mock embeddings")
        # Create mock embeddings based on text hash
        embeddings = []
        for text in df['searchText']:
            hash_val = hash(text)
            embedding = [(hash_val >> i) % 100 / 100.0 for i in range(EMBEDDING_DIMENSIONS)]
            embeddings.append(embedding)
        _embeddings_cache = np.array(embeddings)
        return _embeddings_cache

    texts = df['searchText'].tolist()
    total = len(texts)
    all_embeddings = []

    logger.info(f"Generating embeddings for {total} items...")

    # Process in batches with parallel workers
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for i in range(0, total, batch_size):
            batch = texts[i:i + batch_size]
            future = executor.submit(embed_texts_batch, batch, client)
            futures.append(future)

        for i, future in enumerate(futures):
            embeddings = future.result()
            all_embeddings.extend(embeddings)
            logger.info(f"Processed batch {i+1}/{len(futures)}")

    _embeddings_cache = np.array(all_embeddings)
    logger.info(f"Generated {len(_embeddings_cache)} embeddings")

    return _embeddings_cache

# ============================================================================
# SIMILARITY SEARCH (Based on Cookbook)
# ============================================================================

def cosine_similarity_manual(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors
    From cookbook implementation
    """
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)

def find_similar_items(
    query: str,
    df: pd.DataFrame,
    embeddings: np.ndarray,
    threshold: float = 0.5,
    top_k: int = 10,
    gender_filter: Optional[str] = None,
    article_type_exclude: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Find similar items using RAG with embeddings
    Based on cookbook's find_similar_items_with_rag
    """
    client = get_openai_client()

    # Generate query embedding
    if client:
        try:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=query,
                dimensions=EMBEDDING_DIMENSIONS
            )
            query_embedding = np.array(response.data[0].embedding)
        except Exception as e:
            logger.error(f"Query embedding error: {e}")
            hash_val = hash(query)
            query_embedding = np.array([(hash_val >> i) % 100 / 100.0 for i in range(EMBEDDING_DIMENSIONS)])
    else:
        hash_val = hash(query)
        query_embedding = np.array([(hash_val >> i) % 100 / 100.0 for i in range(EMBEDDING_DIMENSIONS)])

    # Calculate similarities
    similarities = []
    for idx, emb in enumerate(embeddings):
        similarity = cosine_similarity_manual(query_embedding, emb)
        if similarity >= threshold:
            similarities.append((idx, similarity))

    # Sort by similarity descending
    similarities.sort(key=lambda x: x[1], reverse=True)

    logger.info(f"Found {len(similarities)} items above threshold {threshold} for query: '{query[:50]}...'")
    if gender_filter:
        logger.info(f"Applying gender filter: '{gender_filter}'")

    # Get top k results
    results = []
    for idx, score in similarities[:top_k]:
        item = df.iloc[idx].to_dict()

        # Apply filters (case-insensitive gender comparison)
        if gender_filter:
            item_gender = item['gender'].lower() if item.get('gender') else ''
            filter_gender = gender_filter.lower() if gender_filter else ''
            # Skip if gender doesn't match (allow Unisex for any filter)
            if item_gender not in [filter_gender, 'unisex'] and filter_gender != 'unknown':
                continue
        if article_type_exclude and item['articleType'] in article_type_exclude:
            continue

        item['similarity_score'] = float(score)

        # Add retail value data (mock but realistic)
        item = enrich_with_retail_data(item)

        results.append(item)

    logger.info(f"Returning {len(results[:top_k])} items after filtering")
    return results[:top_k]


def enrich_with_retail_data(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich item with retail-valuable data: price, location, stock
    This demonstrates value for both customers and store operations
    """
    import hashlib

    # Generate deterministic but realistic price based on item attributes
    item_id = str(item.get('id', 0))
    article_type = item.get('articleType', 'Item').lower()

    # Price ranges by category (realistic retail pricing)
    price_ranges = {
        'shirts': (45, 120),
        'tshirts': (25, 65),
        'trousers': (55, 150),
        'jeans': (60, 180),
        'dresses': (75, 250),
        'jackets': (90, 350),
        'blazers': (120, 400),
        'shoes': (65, 220),
        'sandals': (35, 95),
        'heels': (70, 200),
        'watches': (80, 500),
        'bags': (45, 280),
        'kurtas': (40, 120),
        'tops': (30, 85),
        'shorts': (35, 80),
        'skirts': (40, 120),
        'sweaters': (50, 150),
        'sweatshirts': (45, 120),
    }

    # Get price range for this article type
    min_price, max_price = price_ranges.get(article_type, (40, 150))

    # Generate consistent price from item ID
    hash_val = int(hashlib.md5(item_id.encode()).hexdigest()[:8], 16)
    price = min_price + (hash_val % (max_price - min_price))
    item['price'] = price

    # Generate store location (Aisle + Rack format)
    gender = item.get('gender', 'Unisex')
    category = item.get('masterCategory', 'Apparel')

    # Aisle assignment based on gender/category
    aisle_map = {
        'Men': {'Apparel': 'A', 'Footwear': 'C', 'Accessories': 'E'},
        'Women': {'Apparel': 'B', 'Footwear': 'D', 'Accessories': 'F'},
        'Unisex': {'Apparel': 'G', 'Footwear': 'H', 'Accessories': 'J'},
        'Boys': {'Apparel': 'K', 'Footwear': 'L', 'Accessories': 'M'},
        'Girls': {'Apparel': 'N', 'Footwear': 'P', 'Accessories': 'Q'},
    }

    aisle = aisle_map.get(gender, {}).get(category, 'A')
    rack = (hash_val % 12) + 1  # Racks 1-12
    shelf = (hash_val % 4) + 1  # Shelves 1-4

    item['storeLocation'] = {
        'aisle': f"Aisle {aisle}",
        'rack': f"Rack {rack}",
        'shelf': f"Shelf {shelf}",
        'display': f"Aisle {aisle}, Rack {rack}"
    }

    # Stock level (realistic distribution: most in stock, some low, few out)
    stock_seed = (hash_val >> 8) % 100
    if stock_seed < 70:  # 70% in stock
        stock_qty = 5 + (hash_val % 20)  # 5-24 items
        stock_status = 'in_stock'
        stock_label = 'In Stock'
    elif stock_seed < 90:  # 20% low stock
        stock_qty = 1 + (hash_val % 4)  # 1-4 items
        stock_status = 'low_stock'
        stock_label = f'Only {stock_qty} left'
    else:  # 10% out of stock (for demo realism)
        stock_qty = 0
        stock_status = 'out_of_stock'
        stock_label = 'Out of Stock'

    item['stock'] = {
        'quantity': stock_qty,
        'status': stock_status,
        'label': stock_label
    }

    # Add usage context for upselling
    usage = item.get('usage', 'Casual')
    season = item.get('season', 'Fall')

    item['retailContext'] = {
        'usage': usage,
        'season': season,
        'perfectFor': get_occasion_suggestions(usage, season),
        'pairsWellWith': get_pairing_suggestions(article_type, gender)
    }

    return item


def get_occasion_suggestions(usage: str, season: str) -> List[str]:
    """Get occasion suggestions based on usage and season"""
    occasions = {
        'Formal': ['Business meetings', 'Weddings', 'Interviews', 'Galas'],
        'Casual': ['Weekend outings', 'Brunch', 'Shopping trips', 'Casual Fridays'],
        'Sports': ['Gym sessions', 'Running', 'Yoga', 'Active weekends'],
        'Ethnic': ['Festivals', 'Cultural events', 'Family gatherings', 'Ceremonies'],
        'Smart Casual': ['Date nights', 'Dinners', 'Office parties', 'Networking events'],
        'Party': ['Clubs', 'Birthday parties', 'New Year celebrations', 'Concerts'],
    }
    return occasions.get(usage, ['Everyday wear', 'Various occasions'])[:2]


def get_pairing_suggestions(article_type: str, gender: str) -> List[str]:
    """Get pairing suggestions for upselling"""
    pairings = {
        'shirts': ['Trousers', 'Blazers', 'Chinos', 'Ties'],
        'tshirts': ['Jeans', 'Shorts', 'Sneakers', 'Caps'],
        'trousers': ['Shirts', 'Belts', 'Oxford shoes', 'Blazers'],
        'jeans': ['T-shirts', 'Sneakers', 'Casual shirts', 'Jackets'],
        'dresses': ['Heels', 'Clutch bags', 'Jewelry', 'Cardigans'],
        'shoes': ['Matching belt', 'Socks', 'Shoe care kit'],
        'blazers': ['Dress shirts', 'Ties', 'Pocket squares', 'Dress pants'],
    }
    return pairings.get(article_type.lower(), ['Accessories', 'Matching items'])[:3]

# ============================================================================
# IMAGE ANALYSIS (GPT-4o Vision)
# ============================================================================

def analyze_clothing_image(image_base64: str) -> Dict[str, Any]:
    """
    Analyze clothing image using GPT-4o vision
    Returns structured analysis of the clothing item
    """
    client = get_openai_client()

    if not client:
        return {
            "article_type": "shirt",
            "base_colour": "blue",
            "pattern": "solid",
            "style_description": "casual",
            "suggested_occasions": ["casual", "everyday"],
            "complementary_items": ["jeans", "sneakers"],
            "gender": "Men"
        }

    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a fashion expert analyzing clothing images. Always respond with valid JSON using the exact keys specified."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this clothing item and return JSON with these EXACT keys:
{
    "article_type": "the type of clothing (shirt, dress, pants, jeans, jacket, etc.)",
    "base_colour": "the main color (blue, red, black, white, etc.)",
    "pattern": "pattern type (solid, striped, floral, checkered, etc.)",
    "style_description": "brief style description (casual, formal, sporty, etc.)",
    "suggested_occasions": ["array", "of", "occasions"],
    "complementary_items": ["array", "of", "items", "that", "would", "match"],
    "gender": "Men or Women based on the clothing style"
}

Use lowercase for article_type and base_colour values."""
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
            response_format={"type": "json_object"},
            max_tokens=500
        )

        analysis = json.loads(response.choices[0].message.content)

        # Normalize keys to ensure consistency (handle any variations GPT might return)
        normalized = {
            "article_type": analysis.get("article_type") or analysis.get("articleType") or analysis.get("type") or "clothing",
            "base_colour": analysis.get("base_colour") or analysis.get("baseColour") or analysis.get("base_color") or analysis.get("color") or "neutral",
            "pattern": analysis.get("pattern") or "solid",
            "style_description": analysis.get("style_description") or analysis.get("styleDescription") or analysis.get("style") or "casual",
            "suggested_occasions": analysis.get("suggested_occasions") or analysis.get("suggestedOccasions") or analysis.get("occasions") or ["everyday"],
            "complementary_items": analysis.get("complementary_items") or analysis.get("complementaryItems") or analysis.get("matches") or [],
            "gender": analysis.get("gender") or "Unisex"
        }

        logger.info(f"Image analysis result: article_type={normalized['article_type']}, base_colour={normalized['base_colour']}, gender={normalized['gender']}")

        return normalized

    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        return {
            "article_type": "clothing",
            "base_colour": "neutral",
            "style_description": "casual",
            "suggested_occasions": ["everyday"],
            "complementary_items": ["accessories", "matching items"],
            "gender": "Unisex"
        }

# ============================================================================
# OUTFIT GENERATION
# ============================================================================

def create_outfit_bundle(
    occasion: str,
    gender: str,
    df: pd.DataFrame,
    embeddings: np.ndarray,
    formality: str = "casual",
    color_preference: Optional[str] = None,
    max_items: int = 5
) -> Dict[str, Any]:
    """
    Create a complete outfit using RAG search
    """
    # Build search query
    query = f"{occasion} {formality} {gender} outfit"
    if color_preference:
        query += f" {color_preference}"

    # Search for items
    items = find_similar_items(
        query=query,
        df=df,
        embeddings=embeddings,
        threshold=0.4,
        top_k=max_items * 3,  # Get more to filter
        gender_filter=gender
    )

    # Organize by category
    outfit = {
        "occasion": occasion,
        "formality": formality,
        "items": [],
        "total_price": 0,
        "categories_covered": []
    }

    # Try to get diverse categories
    categories_added = set()
    for item in items:
        article_type = item['articleType']

        # Avoid duplicates from same category
        if article_type not in categories_added and len(outfit['items']) < max_items:
            # Add price if not present (mock for demo)
            if 'price' not in item:
                item['price'] = np.random.randint(30, 200)

            outfit['items'].append(item)
            outfit['total_price'] += item.get('price', 0)
            categories_added.add(article_type)
            outfit['categories_covered'].append(article_type)

    return outfit

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_rag_system():
    """
    Initialize the RAG system by loading data and generating embeddings
    """
    logger.info("Initializing RAG system...")

    df = load_clothing_data()
    if len(df) == 0:
        logger.error("No clothing data loaded!")
        return None, None

    embeddings = generate_embeddings(df)

    logger.info(f"RAG system ready with {len(df)} items")
    return df, embeddings

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def search_by_description(description: str, gender: Optional[str] = None, top_k: int = 5) -> List[Dict]:
    """Search for items by natural language description"""
    df, embeddings = initialize_rag_system()

    return find_similar_items(
        query=description,
        df=df,
        embeddings=embeddings,
        threshold=0.3,
        top_k=top_k,
        gender_filter=gender
    )

def get_matching_items(image_base64: str, gender: str, top_k: int = 5, search_mode: str = "complementary") -> Dict[str, Any]:
    """
    Get matching items for an uploaded clothing image
    Based on cookbook's approach

    Args:
        image_base64: Base64 encoded image
        gender: Gender filter (Men/Women/Unisex)
        top_k: Number of results to return
        search_mode: "similar" to find same type of item, "complementary" to find items that go with it
    """
    # Analyze the image
    analysis = analyze_clothing_image(image_base64)

    # Use gender from image analysis if not provided or is default
    detected_gender = analysis.get('gender', 'Unisex')
    if gender in ['Women', None, ''] or detected_gender != 'Unisex':
        gender = detected_gender

    # Build search query from analysis - ensure we have meaningful content
    article_type = analysis.get('article_type', 'clothing')
    base_colour = analysis.get('base_colour', '')
    style_desc = analysis.get('style_description', 'casual')
    complementary_items = analysis.get('complementary_items', [])

    df, embeddings = initialize_rag_system()

    if search_mode == "similar":
        # User wants similar items of the SAME type
        # Search for items matching the same article type, color, and style
        query = f"{base_colour} {article_type} {style_desc} {gender}"
        logger.info(f"Similar search query: '{query}'")

        matches = find_similar_items(
            query=query,
            df=df,
            embeddings=embeddings,
            threshold=0.3,
            top_k=top_k,
            gender_filter=gender,
            article_type_exclude=[]  # Don't exclude - we WANT the same type
        )

    else:
        # Default: search for complementary items (things that go with it)
        if complementary_items:
            complementary_query = " ".join(complementary_items)
            query = f"{complementary_query} {style_desc} {gender}"
        else:
            query = f"{style_desc} {base_colour} {gender} fashion"

        logger.info(f"Complementary search query: '{query}' for {article_type}")

        matches = find_similar_items(
            query=query,
            df=df,
            embeddings=embeddings,
            threshold=0.3,
            top_k=top_k,
            gender_filter=gender,
            article_type_exclude=[article_type] if article_type != 'clothing' else []
        )

    # If no matches found, try a broader search
    if len(matches) == 0:
        logger.info("No matches found, trying broader search...")
        broader_query = f"{style_desc} {gender} outfit"
        matches = find_similar_items(
            query=broader_query,
            df=df,
            embeddings=embeddings,
            threshold=0.25,
            top_k=top_k,
            gender_filter=gender
        )

    return {
        "analysis": analysis,
        "matching_items": matches,
        "search_mode": search_mode
    }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test the system
    print("Initializing RAG system...")
    df, embeddings = initialize_rag_system()

    print(f"\nLoaded {len(df)} clothing items")
    print(f"Embeddings shape: {embeddings.shape}")

    # Test search
    print("\n=== Test Search ===")
    results = search_by_description("blue formal shirt for men", gender="Men", top_k=3)
    for item in results:
        print(f"- {item['productDisplayName']} (similarity: {item['similarity_score']:.3f})")
        print(f"  Color: {item['baseColour']}, Type: {item['articleType']}")
        print(f"  Image: {item['imageUrl']}")
