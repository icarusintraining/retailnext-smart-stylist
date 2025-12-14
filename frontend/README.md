# RetailNext Smart Stylist - Interactive Frontend

> Professional, demo-ready UI for showcasing OpenAI's latest APIs in a retail context

## Overview

This is a modern, interactive web interface for the RetailNext Smart Stylist AI assistant. Built specifically for video call demonstrations during the OpenAI Solutions Engineer interview process.

## Features

### Core Capabilities

1. **💬 Intelligent Chat Interface**
   - Natural language conversation
   - Real-time typing indicators
   - Message history with context
   - Beautiful, modern design optimized for screen sharing

2. **📸 Vision Integration**
   - Image upload support
   - Camera capture (for mobile demos)
   - Clothing analysis with GPT-5 Vision
   - Visual feedback in chat

3. **🎤 Voice Capabilities**
   - Audio file upload for transcription
   - Australian-accented text-to-speech playback
   - Seamless voice-to-text-to-response flow
   - Auto-play audio responses

4. **🛍️ Product Recommendations**
   - Dynamic product cards with animations
   - Real-time recommendation updates
   - Event context display
   - Outfit summary with pricing
   - Store location information (aisle/bin)

5. **🎯 Demo-Optimized UX**
   - Large, readable fonts for video calls
   - Clear visual hierarchy
   - Smooth animations and transitions
   - Professional color scheme
   - Quick action buttons for common scenarios
   - API usage indicators

## File Structure

```
frontend/
├── index.html          # Main application interface
├── demo.html           # Demo helper page for API testing
├── styles.css          # Comprehensive styling (professional retail theme)
├── app.js              # Full application logic and API integration
└── README.md           # This file
```

## Setup Instructions

### 1. Prerequisites

Ensure the backend server is running:

```bash
cd ../backend
python server.py
```

The backend should be running at `http://localhost:8000`

### 2. Launch Frontend

Simply open `index.html` in a modern web browser:

```bash
# Option 1: Direct file open
open index.html

# Option 2: Using Python's built-in server (recommended for demo)
python -m http.server 8080
# Then visit: http://localhost:8080

# Option 3: Using Node's http-server
npx http-server -p 8080
```

### 3. Verify Connection

The header should show a green "Connected" status indicator. If not:
- Check that the backend is running
- Verify the API_BASE_URL in `app.js` matches your backend URL
- Check browser console for errors

## Demo Preparation

### For Video Call Demonstrations

1. **Screen Setup**
   - Use 1920x1080 resolution or higher
   - Zoom browser to 110-125% for better visibility
   - Position window to show both chat and recommendations
   - Close unnecessary browser tabs/windows

2. **Quick Test Workflow**
   - Open `demo.html` in a separate tab
   - Run all API tests to verify connectivity
   - Check that status indicators are green
   - Test audio playback beforehand

3. **Sample Demo Flow**

   **For Technical Audience (CTO):**
   ```
   1. "Let me show you our AI stylist powered by OpenAI's latest APIs..."
   2. Type: "I need an outfit for a graduation ceremony"
   3. Point out: Event parsing (Structured Outputs), Semantic search (Embeddings)
   4. Upload an image of clothing
   5. Point out: Vision analysis with GPT-5
   6. Show recommended items with store locations
   7. Highlight: Function calling for inventory operations
   ```

   **For Business Audience (Head of Innovation):**
   ```
   1. "Imagine a customer walks in with an event coming up..."
   2. Use voice input (pre-recorded or typed naturally)
   3. Show how AI understands context
   4. Display complete outfit with pricing
   5. Emphasize: Time saved, increased sales, customer satisfaction
   6. Show store location feature (reduces staff workload)
   ```

### Quick Action Scenarios

The floating action button (bottom right) provides instant demo scenarios:

- **Graduation Outfit** - Shows event parsing and formal wear
- **Interview Look** - Demonstrates business context understanding
- **Wedding Guest** - Shows seasonal/venue awareness
- **Date Night** - Casual/romantic styling

## API Integration Details

### Endpoints Used

| Endpoint | Purpose | Demo Highlight |
|----------|---------|----------------|
| `/chat` | Main conversation | All APIs orchestrated |
| `/voice-chat` | Audio upload | gpt-4o-transcribe + full flow |
| `/parse-event` | Context extraction | Structured Outputs |
| `/inventory/semantic-search` | Product search | text-embedding-3-large |
| `/outfit-bundle` | Complete outfits | Function calling + RAG |
| `/tts` | Voice responses | gpt-4o-mini-tts (Australian) |

### OpenAI APIs Demonstrated

1. **GPT-5** - Reasoning, vision, and conversation
2. **gpt-4o-transcribe** - Superior speech-to-text
3. **gpt-4o-mini-tts** - Instruction-steered TTS (Australian accent)
4. **text-embedding-3-large** - Semantic search
5. **Structured Outputs** - JSON Schema validation
6. **Function Calling** - Dynamic tool use

## Customization

### Changing API Base URL

Edit `app.js`:

```javascript
const API_BASE_URL = 'http://your-backend-url:port';
```

### Disabling Audio

Edit `app.js`:

```javascript
const ENABLE_AUDIO = false;
```

### Styling Adjustments

All colors and spacing are CSS variables in `styles.css`:

```css
:root {
    --primary: #6366F1;
    --secondary: #10B981;
    /* ... etc */
}
```

## Troubleshooting

### "Connection Failed" Status

**Problem:** Red status indicator in header

**Solutions:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify CORS is enabled in `server.py`
3. Check browser console for errors
4. Ensure no firewall blocking localhost

### Images Not Uploading

**Problem:** Image preview doesn't appear

**Solutions:**
1. Check file size (large images may timeout)
2. Verify file type is image/* (JPG, PNG, WEBP)
3. Check browser console for base64 encoding errors

### Audio Not Playing

**Problem:** TTS responses don't play

**Solutions:**
1. Check browser supports MP3 playback
2. Verify backend TTS is working: `demo.html` → Test TTS
3. Check browser didn't block autoplay (user interaction required)
4. Ensure DEMO_MODE is not enabled (TTS disabled in demo mode)

### Recommendations Not Showing

**Problem:** Product cards don't appear after chat

**Solutions:**
1. Check backend is actually returning items
2. Verify function calling is working (check browser console)
3. Check `recommended_items` array in API response
4. Test with a simple query: "Show me a navy blazer"

## Performance Optimization

### For Live Demos

1. **Pre-load the page** - Open 1-2 minutes before demo
2. **Pre-test connection** - Use demo.html to verify
3. **Clear browser cache** - Ensure fresh CSS/JS
4. **Disable extensions** - AdBlockers can interfere
5. **Use incognito mode** - Clean slate for demo

### For Recording

1. **Enable demo mode** - Backend falls back to mock data
2. **Pre-populate** - Have a few messages already in chat
3. **Script it** - Use quick action buttons
4. **Zoom UI** - 125% for better screen recording visibility

## Demo Script Example

### Opening (30 seconds)

> "This is RetailNext's Smart Stylist - an AI-powered fashion assistant I've built using OpenAI's latest API capabilities. It demonstrates 6 different APIs working together to solve a real business problem: helping customers find outfits for specific events."

### Technical Demo (3-4 minutes)

1. **Show Event Parsing**
   - Type: "I need an outfit for my daughter's graduation"
   - Highlight: Structured Outputs extracting event type, formality, season, venue
   - Point to Event Details card that appears

2. **Show Semantic Search**
   - AI finds matching items using embeddings
   - Point out: Not keyword matching - true semantic understanding
   - Show product recommendations with aisle locations

3. **Show Vision**
   - Upload image of clothing
   - AI analyzes: colors, patterns, style, occasion suitability
   - Suggests matching items

4. **Show Voice** (if working)
   - Upload pre-recorded audio
   - gpt-4o-transcribe transcribes
   - Response plays in Australian accent (gpt-4o-mini-tts)

5. **Show Complete Flow**
   - AI uses function calling to check inventory
   - Creates complete outfit bundle
   - Provides pricing and store locations

### Business Value (1-2 minutes)

> "For RetailNext, this solves their customer pain point: people leaving poor reviews because they can't find items for events. Now customers get instant, personalized help 24/7. Expected impact: 30% reduction in walk-outs, 25% increase in basket size, 95% customer satisfaction."

## Screenshots for Presentation

Recommended screenshots to include in slides:

1. **Chat interface** - Clean, modern conversation
2. **Event context card** - Structured data extraction
3. **Product recommendations** - Beautiful product cards
4. **Complete outfit** - Outfit summary with pricing
5. **API indicators** - Showing which APIs were used
6. **Demo helper** - Technical verification page

## Support

For issues during demo:

1. **Check demo.html status page**
2. **Review browser console** (F12)
3. **Verify backend logs**
4. **Fallback to demo mode** if needed

## Credits

Built for OpenAI Solutions Engineer Interview - December 2025

**Technologies:**
- Vanilla JavaScript (ES6+)
- Modern CSS3 (Grid, Flexbox, Animations)
- HTML5 Semantic Markup
- OpenAI API Platform (GPT-5, gpt-4o-transcribe, gpt-4o-mini-tts, text-embedding-3-large)

**Design Principles:**
- Demo-first UX
- Professional retail aesthetic
- Accessibility compliant
- Performance optimized
- Video-call friendly

---

Good luck with your presentation! 🚀
