# Quick Start - 60 Seconds to Demo

## 1. Set API Key (10 seconds)
```bash
export OPENAI_API_KEY="your-key-here"
```

## 2. Install & Start Backend (20 seconds)
```bash
cd backend
pip install -r requirements.txt
python server.py
```

## 3. Open Frontend (10 seconds)
```bash
cd ../frontend
python -m http.server 8080
```

Visit: `http://localhost:8080`

## 4. Test (20 seconds)
1. Type: "I need an outfit for a graduation"
2. Wait for response with recommendations
3. ✅ Done!

---

## Demo Mode (No API Key Needed)
```bash
export DEMO_MODE=true
cd backend
python server.py
```

---

## Troubleshooting

**Backend won't start?**
```bash
pip install fastapi uvicorn openai python-multipart
```

**Frontend won't connect?**
- Check backend is running: `curl http://localhost:8000/health`
- Use `http://localhost:8080` not `file://`

**Need help?**
- Read: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- Check: [README.md](README.md)
- Test: Open `frontend/demo.html`

---

## Sample Queries to Try

```
"I need an outfit for my daughter's graduation next Saturday. It's outdoors."

"I have a job interview at a tech company next week."

"What should I wear to a beach wedding?"

"Find me something elegant for a formal dinner."
```

---

**Ready to present? Check [PRESENTATION_GUIDE.md](PRESENTATION_GUIDE.md)!**
