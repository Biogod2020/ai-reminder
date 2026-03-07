from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from core.orchestrator import SoulOrchestrator

app = FastAPI(title="Notion-Soul-Agent API Hub")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = SoulOrchestrator()

class ChatRequest(BaseModel):
    """Data model for a chat request."""
    message: str
    history: Optional[List[dict]] = None

class FeedbackRequest(BaseModel):
    """Data model for user feedback on a nudge."""
    task_id: int
    user_feedback: str

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/chat")
async def chat(request: ChatRequest):
    """Processes natural language input and returns structured intent/response."""
    result = await orchestrator.run(request.message, history=request.history)
    return {
        "intent": result["intent"],
        "response": result["response"],
        "proposed_actions": result.get("proposed_actions")
    }

@app.get("/get_view_data")
async def get_view_data():
    """Returns structured data for the Flutter dashboard (Calendar/Kanban)."""
    view_data = await orchestrator.get_optimized_view()
    return view_data

@app.post("/heartbeat")
async def heartbeat():
    """AI-initiated status check. Evaluates if a nudge is needed."""
    result = await orchestrator.evaluate_nudge()
    return result

@app.post("/handle_response")
async def handle_response(request: FeedbackRequest):
    """Processes user feedback from a nudge and triggers a re-plan."""
    result = await orchestrator.handle_user_response(
        task_id=request.task_id, 
        user_feedback=request.user_feedback
    )
    return result
