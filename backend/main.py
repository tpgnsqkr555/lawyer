from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import os
from typing import AsyncGenerator
import pdfplumber
from dotenv import load_dotenv

from extractor import EventExtractor
from visualizer import GanttVisualizer
from models import ProgressUpdate, TimelineData

# Load environment variables
load_dotenv()

app = FastAPI(title="Hubble Legal Timeline API")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

extractor = EventExtractor(ANTHROPIC_API_KEY)
visualizer = GanttVisualizer()

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# In-memory conversation store (for MVP - use Redis/database in production)
conversation_store = {}


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using pdfplumber"""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


async def process_document(file_path: str, user_request: str = None) -> AsyncGenerator[str, None]:
    """
    Process document with real-time progress updates via Server-Sent Events.

    Yields JSON progress updates in format:
    {"type": "progress"|"thinking"|"complete"|"error", "message": "...", "data": {...}}
    """

    try:
        # Step 1: Document loaded
        yield f"data: {json.dumps({'type': 'progress', 'message': '📄 Document loaded successfully'})}\n\n"
        await asyncio.sleep(0.5)

        # Step 2: Extracting text
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Extracting text from document...'})}\n\n"
        text = extract_text_from_pdf(file_path)
        word_count = len(text.split())
        yield f"data: {json.dumps({'type': 'progress', 'message': f'✓ Extracted {word_count:,} words from document'})}\n\n"
        await asyncio.sleep(0.5)

        # Step 3: AI analysis with TRUE live streaming
        yield f"data: {json.dumps({'type': 'thinking', 'message': '🧠 Claude AI is analyzing the document...'})}\n\n"
        await asyncio.sleep(0.5)

        # Call Claude API with TRUE streaming - get chunks as they happen
        timeline_data = None
        async for chunk in extractor.extract_events(text, user_request):
            if chunk["type"] == "thinking":
                # Stream thinking line by line AS IT HAPPENS (no fake delays)
                thinking_msg = f"💭 {chunk['content']}"
                yield f"data: {json.dumps({'type': 'thinking', 'message': thinking_msg})}\n\n"
                await asyncio.sleep(0)  # Yield control to event loop
            elif chunk["type"] == "complete":
                # Got final data
                timeline_data = chunk["data"]

        if not timeline_data:
            raise ValueError("No timeline data received from Claude")

        event_count = len(timeline_data.events)
        actor_count = len(set(e.actor for e in timeline_data.events))
        milestone_count = sum(1 for e in timeline_data.events if e.milestone)

        yield f"data: {json.dumps({'type': 'progress', 'message': f'✓ Extracted {event_count} events involving {actor_count} actors'})}\n\n"
        yield f"data: {json.dumps({'type': 'progress', 'message': f'✓ Identified {milestone_count} key milestones'})}\n\n"
        await asyncio.sleep(0.5)

        # Step 4: Generate visualization
        yield f"data: {json.dumps({'type': 'thinking', 'message': '📊 Generating Gantt chart visualization...'})}\n\n"
        await asyncio.sleep(1)

        yield f"data: {json.dumps({'type': 'thinking', 'message': '🎨 Applying color palette based on role types...'})}\n\n"

        # Generate color map
        color_map = extractor.generate_color_palette(timeline_data.events)

        # Generate chart - returns tuple (html_path, png_path)
        html_path, png_path = visualizer.generate_gantt(timeline_data, color_map, "output/timeline.png")

        # Set URLs for both formats
        chart_url = "/output/timeline.html"  # For viewing (interactive)
        download_url = "/output/timeline.png"  # For downloading

        yield f"data: {json.dumps({'type': 'progress', 'message': '✓ Visualization complete'})}\n\n"
        await asyncio.sleep(0.5)

        # Step 5: Complete - include TimelineData for regeneration
        # Generate session ID based on file name
        import hashlib
        session_id = hashlib.md5(file_path.encode()).hexdigest()

        # Store TimelineData for regeneration
        conversation_store[session_id] = timeline_data.dict()

        result_data = {
            "chart_url": chart_url,  # HTML for viewing
            "download_url": download_url,  # PNG for downloading
            "case": timeline_data.case.dict(),
            "event_count": event_count,
            "actor_count": actor_count,
            "milestone_count": milestone_count,
            "session_id": session_id  # Return session ID for regeneration
        }

        yield f"data: {json.dumps({'type': 'complete', 'message': '✅ Analysis complete! Your timeline is ready.', 'data': result_data})}\n\n"

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[BACKEND ERROR] {error_details}")
        error_msg = f"Error during processing: {str(e)}"
        yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"


@app.post("/api/process")
async def process_upload(
    file: UploadFile = File(...),
    request: str = Form(None)
):
    """
    Accept document upload and return streaming progress updates.

    Query params:
    - request: Optional user request like "analyze executives" or "show regulatory timeline"
    """

    # Save uploaded file temporarily
    temp_path = f"output/temp_{file.filename}"

    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Return streaming response
    return StreamingResponse(
        process_document(temp_path, request),
        media_type="text/event-stream"
    )


@app.get("/output/{filename}")
async def serve_output(filename: str):
    """Serve generated chart images"""
    file_path = f"output/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}


@app.post("/api/regenerate")
async def regenerate_timeline(
    session_id: str = Form(...),
    modification: str = Form(...)
):
    """
    Regenerate timeline with user modifications.

    Examples:
    - "Make title bold"
    - "Change suspicious actors to orange"
    - "Move legend to right side"
    - "Add animation"
    """
    # Retrieve stored TimelineData
    if session_id not in conversation_store:
        return {"error": "Session not found. Please upload a document first."}

    timeline_data_dict = conversation_store[session_id]
    timeline_data = TimelineData(**timeline_data_dict)

    # TODO: Use Claude to interpret modification and update VisualizationConfig
    # For now, return a simple message
    return {
        "status": "success",
        "message": f"Modification received: {modification}",
        "note": "Regeneration feature coming soon"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Hubble API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
