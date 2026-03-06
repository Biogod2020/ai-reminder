from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from core.orchestrator import SoulOrchestrator

app = FastAPI(title="Notion-Soul-Agent API Hub")
orchestrator = SoulOrchestrator()

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = None

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
