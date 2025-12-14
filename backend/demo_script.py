#!/usr/bin/env python3
"""
RetailNext Smart Stylist - Demo Script
=======================================
Easy-to-run demo script for live presentations.
Demonstrates all OpenAI API integrations.

Run: python demo_script.py

Author: OpenAI Solutions Engineer Candidate
Date: December 2025
"""

import os
import sys
import time
import json
import base64
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")

def print_step(step_num, text):
    print(f"{Colors.CYAN}[Step {step_num}]{Colors.END} {text}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_api(api_name):
    print(f"  {Colors.YELLOW}→ API: {api_name}{Colors.END}")

def print_result(label, value):
    print(f"  {Colors.GREEN}{label}:{Colors.END} {value}")


def demo_1_text_chat():
    """Demo 1: Basic text chat with event parsing."""
    print_header("Demo 1: Text Chat + Event Parsing + Outfit Bundle")
    
    from backend import process_stylist_request
    
    queries = [
        "I need an outfit for my daughter's graduation next Saturday. It's outdoors and I want something elegant.",
        "I have a job interview at a law firm next week. What should I wear?",
        "What would be perfect for a beach wedding in Bali next month?"
    ]
    
    for i, query in enumerate(queries, 1):
        print_step(i, f"Query: '{query[:50]}...'")
        
        start = time.time()
        result = process_stylist_request(user_input=query, return_audio=False)
        elapsed = (time.time() - start) * 1000
        
        print_result("Event Type", result.get("event_context", {}).get("event_type", "N/A"))
        print_result("Formality", result.get("event_context", {}).get("formality_level", "N/A"))
        print_result("Gender", result.get("event_context", {}).get("gender", "N/A"))
        print_result("Processing Time", f"{elapsed:.0f}ms")
        
        for api in result.get("apis_used", []):
            print_api(api)
        
        print(f"\n  {Colors.CYAN}Response Preview:{Colors.END}")
        response_preview = result.get("text_response", "")[:200]
        print(f"  {response_preview}...")
        print()
    
    print_success("Demo 1 Complete!")


def demo_2_semantic_search():
    """Demo 2: Semantic search with embeddings (RAG)."""
    print_header("Demo 2: Semantic Search (RAG with text-embedding-3-large)")
    
    from backend import find_similar_items
    
    queries = [
        ("elegant silk top for evening event", "women"),
        ("comfortable business casual shirt", "men"),
        ("statement piece for date night", "women")
    ]
    
    for i, (query, gender) in enumerate(queries, 1):
        print_step(i, f"Query: '{query}' (Gender: {gender})")
        
        start = time.time()
        results = find_similar_items(query, gender=gender)
        elapsed = (time.time() - start) * 1000
        
        print_api("text-embedding-3-large (Semantic Similarity)")
        print_result("Results Found", len(results))
        print_result("Search Time", f"{elapsed:.0f}ms")
        
        print(f"\n  {Colors.CYAN}Top Matches:{Colors.END}")
        for item in results[:3]:
            print(f"    • {item['name']} - ${item['price']} ({item['location']})")
        print()
    
    print_success("Demo 2 Complete!")


def demo_3_outfit_bundle():
    """Demo 3: Complete outfit bundle generation."""
    print_header("Demo 3: Complete Outfit Bundle Generation")
    
    from backend import get_outfit_bundle
    
    occasions = [
        ("graduation ceremony", "women", "smart-casual"),
        ("job interview", "men", "business-casual"),
        ("cocktail party", "women", "semi-formal")
    ]
    
    for i, (occasion, gender, formality) in enumerate(occasions, 1):
        print_step(i, f"Occasion: '{occasion}' ({gender}, {formality})")
        
        start = time.time()
        bundle = get_outfit_bundle(occasion, gender, formality)
        elapsed = (time.time() - start) * 1000
        
        print_api("Function Calling + Semantic Search")
        print_result("Total Price", f"${bundle['total_price']:.2f}")
        print_result("Items in Bundle", len(bundle['items']))
        print_result("Generation Time", f"{elapsed:.0f}ms")
        
        print(f"\n  {Colors.CYAN}Bundle Items:{Colors.END}")
        for item in bundle['items']:
            print(f"    • {item['name']} - ${item['price']} ({item['location']})")
        
        print(f"\n  {Colors.CYAN}Styling Notes:{Colors.END}")
        print(f"    {bundle['styling_notes']}")
        print()
    
    print_success("Demo 3 Complete!")


def demo_4_vision_analysis():
    """Demo 4: Image analysis (simulated in demo mode)."""
    print_header("Demo 4: Vision Analysis (GPT-5 Vision)")
    
    from backend import analyze_clothing_image, DEMO_MODE
    
    print_info(f"Demo Mode: {DEMO_MODE}")
    print_info("In production, this analyzes real images via GPT-5 Vision")
    
    # Simulated analysis (would use real image in production)
    print_step(1, "Analyzing uploaded clothing image...")
    
    start = time.time()
    analysis = analyze_clothing_image("mock_base64_image")
    elapsed = (time.time() - start) * 1000
    
    print_api("GPT-5 Vision (Multimodal Analysis)")
    print_result("Clothing Type", analysis.get("clothing_type", "N/A"))
    print_result("Colors", ", ".join(analysis.get("colors", [])))
    print_result("Style", analysis.get("style", "N/A"))
    print_result("Analysis Time", f"{elapsed:.0f}ms")
    
    print(f"\n  {Colors.CYAN}Occasion Suitability:{Colors.END}")
    for occasion in analysis.get("occasion_suitability", []):
        print(f"    • {occasion}")
    
    print(f"\n  {Colors.CYAN}Matching Suggestions:{Colors.END}")
    for suggestion in analysis.get("matching_suggestions", []):
        print(f"    • {suggestion}")
    print()
    
    print_success("Demo 4 Complete!")


def demo_5_voice_flow():
    """Demo 5: Complete voice flow (transcription + response + TTS)."""
    print_header("Demo 5: Voice Flow (gpt-4o-transcribe + gpt-4o-mini-tts)")
    
    from backend import transcribe_audio_bytes, text_to_speech_bytes, DEMO_MODE
    
    print_info(f"Demo Mode: {DEMO_MODE}")
    print_info("In production, this processes real audio files")
    
    # Step 1: Transcription
    print_step(1, "Transcribing customer voice input...")
    
    start = time.time()
    transcript = transcribe_audio_bytes(b"mock_audio_bytes", "recording.wav")
    elapsed = (time.time() - start) * 1000
    
    print_api("gpt-4o-transcribe (Speech-to-Text)")
    print_result("Transcript", transcript[:80] + "...")
    print_result("Transcription Time", f"{elapsed:.0f}ms")
    
    # Step 2: Generate response
    print_step(2, "Generating AI response...")
    
    from backend import process_stylist_request
    result = process_stylist_request(user_input=transcript, return_audio=False)
    
    response_text = result.get("text_response", "")[:150]
    print_result("Response", response_text + "...")
    
    # Step 3: TTS
    print_step(3, "Converting response to Australian-accented speech...")
    
    start = time.time()
    audio_bytes = text_to_speech_bytes(result.get("text_response", "")[:200])
    elapsed = (time.time() - start) * 1000
    
    print_api("gpt-4o-mini-tts (Text-to-Speech, Australian Accent)")
    print_result("Audio Generated", f"{len(audio_bytes)} bytes" if audio_bytes else "Demo mode - no audio")
    print_result("TTS Time", f"{elapsed:.0f}ms")
    print()
    
    print_success("Demo 5 Complete!")


def demo_6_full_pipeline():
    """Demo 6: Full end-to-end pipeline with all APIs."""
    print_header("Demo 6: Full Pipeline (All 6 OpenAI APIs)")
    
    from backend import process_stylist_request
    
    query = "I'm looking for an outfit for a spring wedding. I want to show you a dress I already have to match it. Budget around $500."
    
    print_step(1, f"Processing: '{query}'")
    print_info("This demonstrates all 6 OpenAI APIs working together")
    
    start = time.time()
    result = process_stylist_request(
        user_input=query,
        image_base64="mock_image",  # Would be real image
        return_audio=True
    )
    total_elapsed = (time.time() - start) * 1000
    
    print(f"\n{Colors.CYAN}APIs Used:{Colors.END}")
    for api in result.get("apis_used", []):
        print_api(api)
    
    print(f"\n{Colors.CYAN}Results:{Colors.END}")
    print_result("Event Type", result.get("event_context", {}).get("event_type", "N/A"))
    print_result("Formality", result.get("event_context", {}).get("formality_level", "N/A"))
    print_result("Items Recommended", len(result.get("recommended_items", [])))
    print_result("Audio Response", "Generated" if result.get("audio_response_base64") else "N/A")
    print_result("Total Time", f"{total_elapsed:.0f}ms")
    
    print(f"\n{Colors.CYAN}Recommended Items:{Colors.END}")
    for item in result.get("recommended_items", [])[:4]:
        print(f"    • {item['name']} - ${item['price']} ({item.get('location', 'N/A')})")
    
    print(f"\n{Colors.CYAN}Response Preview:{Colors.END}")
    print(f"  {result.get('text_response', '')[:300]}...")
    print()
    
    print_success("Demo 6 Complete!")


def demo_api_health():
    """Check API health and connectivity."""
    print_header("API Health Check")
    
    from backend import health_check
    
    health = health_check()
    
    print_result("Status", health.get("status", "unknown"))
    print_result("Demo Mode", str(health.get("demo_mode", False)))
    print_result("OpenAI Connected", str(health.get("openai_connected", False)))
    print_result("Inventory Items", health.get("inventory_count", 0))
    
    print(f"\n{Colors.CYAN}Models Configured:{Colors.END}")
    for model_type, model_name in health.get("models", {}).items():
        print(f"    • {model_type}: {model_name}")
    
    if health.get("api_test"):
        print_result("\nAPI Test", health.get("api_test"))
    
    print()


def run_all_demos():
    """Run all demos in sequence."""
    print_header("🛍️ RetailNext Smart Stylist - Complete Demo")
    print_info("This demo showcases all OpenAI API integrations")
    print_info("Perfect for live demonstration during video calls")
    
    demos = [
        ("API Health Check", demo_api_health),
        ("Text Chat + Event Parsing", demo_1_text_chat),
        ("Semantic Search (RAG)", demo_2_semantic_search),
        ("Outfit Bundle Generation", demo_3_outfit_bundle),
        ("Vision Analysis", demo_4_vision_analysis),
        ("Voice Flow", demo_5_voice_flow),
        ("Full Pipeline", demo_6_full_pipeline),
    ]
    
    for name, func in demos:
        try:
            func()
            input(f"{Colors.YELLOW}Press Enter to continue to next demo...{Colors.END}")
        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user")
            break
        except Exception as e:
            print_error(f"Error in {name}: {e}")
            continue
    
    print_header("🎉 Demo Complete!")
    print_info("Thank you for watching!")
    print_info("All 6 OpenAI APIs demonstrated:")
    print("  1. GPT-5 (Vision + Reasoning)")
    print("  2. gpt-4o-transcribe (Speech-to-Text)")
    print("  3. gpt-4o-mini-tts (Text-to-Speech, Australian Accent)")
    print("  4. text-embedding-3-large (Semantic Search/RAG)")
    print("  5. Structured Outputs (JSON Schema)")
    print("  6. Function Calling (Tool Use)")


def main():
    parser = argparse.ArgumentParser(
        description="RetailNext Smart Stylist Demo Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo_script.py                 # Run all demos interactively
  python demo_script.py --demo 1        # Run specific demo
  python demo_script.py --health        # Check API health only
  python demo_script.py --quick         # Quick run without pauses
        """
    )
    
    parser.add_argument("--demo", type=int, choices=[1,2,3,4,5,6],
                       help="Run specific demo (1-6)")
    parser.add_argument("--health", action="store_true",
                       help="Run health check only")
    parser.add_argument("--quick", action="store_true",
                       help="Run all demos without pauses")
    parser.add_argument("--api-key", type=str,
                       help="Set OpenAI API key")
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
        print_info("API key set from command line")
    
    # Run requested demo
    if args.health:
        demo_api_health()
    elif args.demo:
        demos = {
            1: demo_1_text_chat,
            2: demo_2_semantic_search,
            3: demo_3_outfit_bundle,
            4: demo_4_vision_analysis,
            5: demo_5_voice_flow,
            6: demo_6_full_pipeline,
        }
        demos[args.demo]()
    elif args.quick:
        # Run without pauses
        demo_api_health()
        demo_1_text_chat()
        demo_2_semantic_search()
        demo_3_outfit_bundle()
        demo_4_vision_analysis()
        demo_5_voice_flow()
        demo_6_full_pipeline()
    else:
        run_all_demos()


if __name__ == "__main__":
    main()
