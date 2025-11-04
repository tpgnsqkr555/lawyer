# Hubble - Quick Start Guide

## Setup (One-time)

### 1. Add your Anthropic API Key

Edit `backend/.env` and add your API key:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

Get your API key from: https://console.anthropic.com/

### 2. Verify installations

Backend dependencies should already be installed. If you need to reinstall:
```bash
cd backend
pip install -r requirements.txt
```

Frontend should already be set up. If needed:
```bash
cd hubble
npm install
```

## Running the Application

### Option 1: Manual (Two Terminals)

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```
Server runs on http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd hubble
npm run dev
```
Frontend runs on http://localhost:5173

### Option 2: Quick Script

```bash
# Start backend (in one terminal)
cd backend && python main.py

# Start frontend (in another terminal)
cd hubble && npm run dev
```

## Using Hubble

1. Open http://localhost:5173 in your browser

2. **(Optional)** Type a request in the chat:
   - "Analyze the executive timeline"
   - "Show regulatory investigation events"
   - "Create timeline for all stakeholders"

3. **Upload a PDF**: Click the upload icon (📎) and select a legal document

4. **Watch the magic**:
   - Left panel shows real-time AI thinking
   - Right panel displays the generated Gantt chart

5. **Export**: Click "Export PNG" to download your visualization

## What it does

- Extracts structured events from legal documents using Claude AI
- Identifies: actors, actions, targets, role types, dates, context
- Generates professional Gantt chart visualizations
- Real-time streaming progress updates
- Adaptive color palettes based on extracted roles

## Troubleshooting

**"ANTHROPIC_API_KEY environment variable is required"**
→ Make sure you added your API key to `backend/.env`

**Backend won't start (Port 8000 in use)**
```bash
lsof -i :8000
kill [PID]
```

**Frontend won't start (Port 5173 in use)**
```bash
lsof -i :5173
kill [PID]
```

**CORS errors**
→ Make sure both backend (port 8000) and frontend (port 5173) are running

## Next Steps (Future Phases)

- Interactive chart editing ("make this color blue")
- Multiple chart types (timeline, swimlane, network graph)
- Multi-document analysis
- Export to PowerPoint/PDF with annotations
