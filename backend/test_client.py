#!/usr/bin/env python3
"""
RetailNext Smart Stylist - API Test Client
==========================================
Quick test client for verifying API endpoints.
Use during demo to show endpoints working in real-time.

Usage:
    python test_client.py                # Run all tests
    python test_client.py --endpoint chat  # Test specific endpoint
    python test_client.py --base-url http://localhost:8000

Author: OpenAI Solutions Engineer Candidate
Date: December 2025
"""

import argparse
import json
import time
import sys

try:
    import requests
except ImportError:
    print("Please install requests: pip install requests")
    sys.exit(1)


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"  {status} {name}")
    if details and not passed:
        print(f"       {Colors.YELLOW}{details}{Colors.END}")


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}{Colors.END}\n")


class APITestClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.results = {"passed": 0, "failed": 0}
    
    def test(self, name, method, endpoint, **kwargs):
        """Run a single test."""
        url = f"{self.base_url}{endpoint}"
        try:
            start = time.time()
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, timeout=30, **kwargs)
            elapsed = (time.time() - start) * 1000
            
            passed = response.status_code == 200
            details = f"Status: {response.status_code}, Time: {elapsed:.0f}ms"
            
            if passed:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
                details += f", Response: {response.text[:100]}"
            
            print_test(name, passed, details if not passed else "")
            return response.json() if passed else None
            
        except requests.exceptions.ConnectionError:
            self.results["failed"] += 1
            print_test(name, False, "Connection refused - is server running?")
            return None
        except Exception as e:
            self.results["failed"] += 1
            print_test(name, False, str(e))
            return None
    
    def test_health(self):
        """Test health endpoints."""
        print_header("Health Endpoints")
        self.test("Root endpoint", "GET", "/")
        self.test("Health check", "GET", "/health")
    
    def test_chat(self):
        """Test chat endpoints."""
        print_header("Chat Endpoints")
        
        self.test(
            "Text chat",
            "POST", "/chat",
            json={
                "message": "I need an outfit for a graduation",
                "return_audio": False
            }
        )
        
        self.test(
            "Text chat with context",
            "POST", "/chat",
            json={
                "message": "What about something more casual?",
                "conversation_history": [
                    {"role": "user", "content": "I need help"},
                    {"role": "assistant", "content": "I'd love to help!"}
                ],
                "return_audio": False
            }
        )
    
    def test_parse_event(self):
        """Test event parsing."""
        print_header("Event Parsing (Structured Outputs)")
        
        result = self.test(
            "Parse graduation event",
            "POST", "/parse-event",
            json={
                "user_input": "I need an outfit for my daughter's outdoor graduation ceremony next Saturday"
            }
        )
        
        if result:
            context = result.get("event_context", {})
            print(f"       Event: {context.get('event_type', 'N/A')}")
            print(f"       Formality: {context.get('formality_level', 'N/A')}")
        
        self.test(
            "Parse interview event",
            "POST", "/parse-event",
            json={
                "user_input": "Job interview at a tech company, business casual"
            }
        )
    
    def test_inventory(self):
        """Test inventory endpoints."""
        print_header("Inventory Endpoints")
        
        self.test("List inventory", "GET", "/inventory")
        self.test("Get categories", "GET", "/inventory/categories")
        
        self.test(
            "Search inventory",
            "POST", "/inventory/search",
            json={"query": "silk blouse", "gender": "women"}
        )
        
        result = self.test(
            "Semantic search",
            "POST", "/inventory/semantic-search",
            json={"description": "elegant formal top", "gender": "women"}
        )
        
        if result and result.get("items"):
            print(f"       Found {len(result['items'])} items via semantic search")
    
    def test_outfit_bundle(self):
        """Test outfit bundle generation."""
        print_header("Outfit Bundle (Function Calling)")
        
        result = self.test(
            "Generate outfit bundle",
            "POST", "/outfit-bundle",
            json={
                "occasion": "graduation ceremony",
                "gender": "women",
                "formality": "smart-casual"
            }
        )
        
        if result:
            print(f"       Items: {len(result.get('items', []))}")
            print(f"       Total: ${result.get('total_price', 0):.2f}")
    
    def test_tts(self):
        """Test text-to-speech."""
        print_header("Text-to-Speech (Australian Accent)")
        
        self.test(
            "TTS base64",
            "POST", "/tts/base64",
            json={
                "text": "G'day! Welcome to RetailNext.",
                "use_australian_accent": True
            }
        )
    
    def test_demo_helpers(self):
        """Test demo helper endpoints."""
        print_header("Demo Helpers")
        
        self.test("Quick test", "GET", "/demo/quick-test")
        self.test("Sample queries", "GET", "/demo/sample-queries")
    
    def run_all(self):
        """Run all tests."""
        print(f"\n{Colors.BOLD}RetailNext Smart Stylist - API Test Suite{Colors.END}")
        print(f"Base URL: {self.base_url}\n")
        
        self.test_health()
        self.test_chat()
        self.test_parse_event()
        self.test_inventory()
        self.test_outfit_bundle()
        self.test_tts()
        self.test_demo_helpers()
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        total = self.results["passed"] + self.results["failed"]
        
        print_header("Test Summary")
        print(f"  {Colors.GREEN}Passed: {self.results['passed']}{Colors.END}")
        print(f"  {Colors.RED}Failed: {self.results['failed']}{Colors.END}")
        print(f"  Total:  {total}")
        
        if self.results["failed"] == 0:
            print(f"\n  {Colors.GREEN}{Colors.BOLD}All tests passed! ✓{Colors.END}")
        else:
            print(f"\n  {Colors.YELLOW}Some tests failed - check server logs{Colors.END}")


def main():
    parser = argparse.ArgumentParser(description="Test RetailNext API endpoints")
    parser.add_argument("--base-url", default="http://localhost:8000",
                       help="API base URL")
    parser.add_argument("--endpoint", choices=[
        "health", "chat", "parse", "inventory", "bundle", "tts", "demo"
    ], help="Test specific endpoint group")
    
    args = parser.parse_args()
    
    client = APITestClient(args.base_url)
    
    if args.endpoint:
        tests = {
            "health": client.test_health,
            "chat": client.test_chat,
            "parse": client.test_parse_event,
            "inventory": client.test_inventory,
            "bundle": client.test_outfit_bundle,
            "tts": client.test_tts,
            "demo": client.test_demo_helpers,
        }
        tests[args.endpoint]()
        client.print_summary()
    else:
        client.run_all()


if __name__ == "__main__":
    main()
