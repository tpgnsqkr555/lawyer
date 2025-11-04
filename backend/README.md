# Hubble Backend

Legal timeline visualization API powered by Claude AI.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key:**
   - Copy `.env.example` to `.env`
   - Add your Anthropic API key:
     ```
     ANTHROPIC_API_KEY=sk-ant-your-key-here
     ```

3. **Run the server:**
   ```bash
   python main.py
   ```

   Or with uvicorn:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

## API Endpoints

### POST `/api/process`
Upload a PDF document for timeline extraction and visualization.

**Request:**
- `file`: PDF document (multipart/form-data)
- `request`: Optional user request string (e.g., "analyze executives")

**Response:**
Server-Sent Events stream with progress updates:
```json
{"type": "progress", "message": "📄 Document loaded successfully"}
{"type": "thinking", "message": "🧠 AI analyzing document structure..."}
{"type": "complete", "message": "✅ Analysis complete!", "data": {...}}
```

### GET `/output/{filename}`
Serve generated chart images.

### GET `/health`
Health check endpoint.

## Architecture

- **main.py**: FastAPI server with streaming endpoints
- **extractor.py**: Claude API integration for event extraction
- **visualizer.py**: Matplotlib Gantt chart generator
- **models.py**: Pydantic data models

## Event Schema

```python
{
  "actor": "Dr. Sarah Chen",
  "action": "appointed",
  "target": "Chief Financial Officer position",
  "roleType": "Executive Leadership",
  "start_date": "2018-03-15",
  "end_date": "2023-08-20",
  "context": "Brief explanation",
  "milestone": true
}
```
