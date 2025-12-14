# RetailNext Smart Stylist - Complete Setup Guide

## Quick Start (5 Minutes)

### Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Required packages:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `openai` - OpenAI API client
- `python-dotenv` - Environment management
- `python-multipart` - File upload support

### Step 2: Configure OpenAI API Key

**Option A: Environment Variable (Recommended)**

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

**Option B: .env File**

Create `backend/.env`:

```
OPENAI_API_KEY=your-openai-api-key-here
```

**IMPORTANT SECURITY NOTE:**
- Never commit your API key to git
- Never share your API key in screenshots or videos
- Revoke any exposed keys immediately at platform.openai.com

### Step 3: Start Backend Server

```bash
cd backend
python server.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Open Frontend

**Option A: Simple File Open**

```bash
cd frontend
open index.html  # macOS
# or
start index.html  # Windows
# or
xdg-open index.html  # Linux
```

**Option B: Local Web Server (Better for CORS)**

```bash
cd frontend
python -m http.server 8080
```

Then visit: `http://localhost:8080`

### Step 5: Verify Everything Works

1. **Check Status Indicator**: Header should show green "Connected"
2. **Open Demo Helper**: `http://localhost:8080/demo.html`
3. **Run Tests**: Click each test button to verify APIs
4. **Try Main App**: Go back to main interface and type: "I need an outfit for a graduation"

## Demo Mode (For Presentations)

If you want to demo without using OpenAI credits or need a fallback for network issues:

```bash
export DEMO_MODE=true
cd backend
python server.py
```

In demo mode:
- All API calls return realistic mock data
- No OpenAI API calls are made
- Perfect for practice runs and testing UI

## For OpenAI Interview Demo

### Pre-Demo Checklist

**1 Day Before:**
- [ ] Test full workflow end-to-end
- [ ] Record backup video (in case of technical issues)
- [ ] Prepare slides with architecture diagrams
- [ ] Test screen sharing setup

**1 Hour Before:**
- [ ] Restart backend server
- [ ] Clear browser cache
- [ ] Open frontend in incognito mode
- [ ] Run all demo.html tests
- [ ] Verify audio playback works
- [ ] Test quick action buttons

**Just Before Demo:**
- [ ] Close unnecessary applications
- [ ] Set browser zoom to 125%
- [ ] Disable notifications
- [ ] Have backup tab with demo.html open
- [ ] Keep terminal with backend visible (for technical depth)

### Demo Flow Recommendations

**For Technical Stakeholders (CTO):**

1. **Architecture First** (2 min)
   - Show slides with architecture diagram
   - Explain API orchestration
   - Highlight 6 OpenAI APIs used

2. **Code Walkthrough** (3 min)
   - Show `backend.py` key functions
   - Explain structured outputs with JSON schema
   - Show function calling implementation
   - Demonstrate RAG with embeddings

3. **Live Demo** (3 min)
   - Event parsing: "I need an outfit for a graduation"
   - Show structured output extraction
   - Semantic search demonstration
   - Function calling in action
   - Complete outfit bundle generation

4. **Advanced Features** (2 min)
   - Vision API: Upload clothing image
   - TTS: Play Australian accent response
   - Show API usage indicators

**For Business Stakeholders (Head of Innovation):**

1. **Business Problem** (1 min)
   - RetailNext customers leaving poor reviews
   - Can't find items for specific events
   - Staff overwhelmed with styling requests

2. **Solution Demo** (5 min)
   - Natural conversation: "My daughter's graduation is next week..."
   - AI understands context automatically
   - Finds perfect items with locations
   - Complete outfit with pricing
   - Voice interaction option

3. **Business Value** (2 min)
   - 30% reduction in walk-outs
   - 25% increase in basket size
   - 24/7 availability
   - Frees staff for high-value interactions
   - Improved customer satisfaction

4. **Scalability** (2 min)
   - Handles multiple languages
   - Works across product categories
   - Integrates with existing inventory
   - Extensible to mobile app

## Troubleshooting

### Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'openai'`

**Solution:**
```bash
pip install -r requirements.txt
```

**Error:** `Port 8000 already in use`

**Solution:**
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
# or change port
PORT=8001 python server.py
```

**Error:** `API key not configured`

**Solution:**
```bash
export OPENAI_API_KEY="sk-..."
```

### Frontend Issues

**Issue:** "Connection Failed" status

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check browser console for CORS errors
3. Ensure using `http://localhost` not `file://`

**Issue:** Images not uploading

**Solution:**
1. Check image file size (< 5MB recommended)
2. Use supported formats: JPG, PNG, WEBP
3. Check browser console for errors

**Issue:** Audio not playing

**Solution:**
1. Verify TTS is working: `demo.html` → Test TTS button
2. Check browser supports MP3 playback
3. Ensure autoplay is allowed
4. Note: Audio disabled in DEMO_MODE

### API Issues

**Issue:** OpenAI API errors

**Solution:**
1. Check API key is valid: `platform.openai.com/api-keys`
2. Verify account has credits
3. Check rate limits not exceeded
4. Try DEMO_MODE as fallback

**Issue:** Slow responses

**Solution:**
1. This is normal for GPT-5 (large model)
2. Expected: 2-5 seconds per request
3. During demo, prepare audience for slight delay
4. Consider using DEMO_MODE for instant responses

## Testing Checklist

Before the demo, verify each feature:

### Core Features
- [ ] Chat conversation works
- [ ] Messages display correctly
- [ ] Event context extraction works
- [ ] Product recommendations appear
- [ ] Product details modal opens
- [ ] Outfit summary calculates correctly

### Advanced Features
- [ ] Image upload works
- [ ] Image analysis returns results
- [ ] Voice file upload works
- [ ] Audio transcription works
- [ ] TTS playback works
- [ ] Quick action buttons work

### API Integration
- [ ] Event parsing endpoint works
- [ ] Semantic search endpoint works
- [ ] Outfit bundle endpoint works
- [ ] Chat endpoint works
- [ ] All 6 APIs demonstrate successfully

### UI/UX
- [ ] Animations smooth
- [ ] No console errors
- [ ] Responsive on different screen sizes
- [ ] Text readable at demo resolution
- [ ] Status indicators update correctly

## Environment Variables

Full list of supported environment variables:

### Backend
```bash
# Required
OPENAI_API_KEY=sk-...

# Optional - Model Selection
OPENAI_GPT_MODEL=gpt-5
OPENAI_TRANSCRIBE_MODEL=gpt-4o-transcribe
OPENAI_TTS_MODEL=gpt-4o-mini-tts
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# Optional - TTS Configuration
TTS_VOICE=nova

# Optional - Server Configuration
PORT=8000
HOST=0.0.0.0
DEMO_MODE=false
```

### Frontend
Edit `frontend/app.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
const ENABLE_AUDIO = true;
```

## File Structure

```
Retail_Solution/
├── background.md           # Project requirements
├── SETUP_GUIDE.md         # This file
├── backend/
│   ├── backend.py         # Core AI logic (6 APIs)
│   ├── server.py          # FastAPI REST server
│   ├── demo_script.py     # CLI demo tool
│   ├── test_client.py     # API test client
│   ├── requirements.txt   # Python dependencies
│   └── README.md          # Backend documentation
└── frontend/
    ├── index.html         # Main UI
    ├── demo.html          # Demo helper page
    ├── styles.css         # Professional styling
    ├── app.js             # API integration
    └── README.md          # Frontend documentation
```

## Demo Best Practices

1. **Practice First**
   - Run through demo 3-5 times
   - Time yourself (aim for 10-15 min total)
   - Prepare for questions

2. **Have Backups**
   - DEMO_MODE configured
   - Screenshot of working demo
   - Pre-recorded video

3. **Explain As You Go**
   - Don't just click buttons
   - Explain what's happening
   - Connect to business value

4. **Show Technical Depth**
   - Open browser console (briefly)
   - Show backend terminal with logs
   - Mention specific API endpoints
   - Reference JSON schemas

5. **Handle Issues Gracefully**
   - If API times out: "This is GPT-5, very powerful but sometimes takes a moment"
   - If network fails: Switch to DEMO_MODE
   - If demo fails completely: Show pre-recorded video

## Getting Help

- Check `frontend/demo.html` for API status
- Review browser console (F12) for errors
- Check backend terminal for server logs
- Test individual endpoints with curl/Postman

## For Video Submission

If recording for submission:

1. **Screen Setup**
   - 1920x1080 resolution
   - Browser zoom 125%
   - Hide bookmarks bar
   - Clean desktop

2. **Recording Tips**
   - Use QuickTime (macOS) or OBS
   - Enable system audio
   - Test mic levels first
   - Aim for 4-5 minutes total

3. **Narration Script**
   - Introduction (30s): "I built this AI fashion assistant using 6 OpenAI APIs..."
   - Architecture (1min): Show code, explain approach
   - Demo (2-3min): Walk through key features
   - Business value (30s): Impact for RetailNext
   - Wrap up (30s): Thank you

## Production Deployment (Bonus)

Not required for interview, but if asked:

**Backend:**
- Deploy on Railway, Render, or Heroku
- Set environment variables in dashboard
- Use gunicorn for production ASGI server

**Frontend:**
- Deploy on Netlify, Vercel, or GitHub Pages
- Update API_BASE_URL to production backend
- Enable CORS for production domain

**Security:**
- Add authentication (API keys, OAuth)
- Rate limiting
- Input validation
- HTTPS only

---

## Support During Interview

If technical issues occur during live demo:

1. **Stay Calm** - Technical hiccups happen
2. **Explain** - "Let me switch to demo mode to continue"
3. **Show Knowledge** - "This would be a CORS issue, here's how I'd debug..."
4. **Keep Moving** - Don't spend 5 minutes debugging
5. **Show Backup** - Have screenshots/video ready

Good luck! You've got this! 🚀
