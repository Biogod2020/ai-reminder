from fastapi import FastAPI, Body, HTTPException
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

class TraceScoreRequest(BaseModel):
    """Data model for submitting a score to a Langfuse trace."""
    trace_id: str
    name: str  # e.g., "user-approval"
    value: float  # e.g., 1.0 or 0.0
    comment: Optional[str] = None

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

@app.post("/submit_trace_score")
async def submit_trace_score(request: TraceScoreRequest):
    """Submits a score (feedback) to a specific Langfuse trace."""
    orchestrator.langfuse.score(
        trace_id=request.trace_id,
        name=request.name,
        value=request.value,
        comment=request.comment
    )
    return {"status": "score_submitted"}

@app.get("/api/v1/viz/graph")
async def get_graph_structure():
    """Returns a rich, detailed system architecture diagram with State Schema."""
    rich_mermaid = """
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#ffffff', 'primaryBorderColor': '#e9e9e7', 'lineColor': '#9b9b9b', 'fontFamily': 'Inter'}}}%%
graph TD
    classDef user focus fill:#2383e2,stroke:#1a65b0,stroke-width:2px,color:#fff,rx:8px,ry:8px;
    classDef node fill:#fff,stroke:#e9e9e7,stroke-width:2px,color:#37352f,rx:8px,ry:8px;
    classDef model fill:#fef3c7,stroke:#f59e0b,stroke-width:2px,color:#92400e,rx:8px,ry:8px,stroke-dasharray: 5 5;
    classDef db fill:#f3f4f6,stroke:#d1d5db,stroke-width:2px,color:#374151,rx:4px,ry:4px,shape:cylinder;
    classDef system fill:#eff6ff,stroke:#93c5fd,stroke-width:2px,color:#1e3a8a,rx:8px,ry:8px;
    classDef state fill:#fff,stroke:#2383e2,stroke-width:1px,color:#2383e2,font-size:10px;

    User[User Input / Dashboard]:::user

    subgraph "AgentState (Shared Context)"
        direction LR
        S1["user_input (str)"]:::state
        S2["intent (str)"]:::state
        S3["history (list)"]:::state
        S4["proposed_actions (list)"]:::state
        S5["response (str)"]:::state
        S6["needs_approval (bool)"]:::state
    end

    subgraph "SoulOrchestrator (LangGraph Core)"
        classify["classify (Node)"]:::node
        handle_task["handle_task (Node)"]:::node
        handle_memory["handle_memory (Node)"]:::node
        handle_planner["handle_planner (Node)"]:::node
        handle_clarify["handle_clarify (Node)"]:::node
        await_approval["await_approval (Node)"]:::node
        notify["notify (Node)"]:::node
        END((END)):::node

        classify -- "intent=='task'" --> handle_task
        classify -- "intent=='memory'" --> handle_memory
        classify -- "intent=='planner'" --> handle_planner
        classify -- "intent=='clarify'" --> handle_clarify
        
        handle_task --> await_approval
        handle_planner --> await_approval
        handle_memory --> notify
        
        handle_clarify --> END
        await_approval --> END
        notify --> END
    end

    %% Data Flow to State
    classify -.->|Writes| S2
    handle_task -.->|Writes| S4
    handle_task -.->|Writes| S5
    handle_memory -.->|Writes| S5
    await_approval -.->|Writes| S6

    subgraph "Perception & Synthesis"
        VisualSampler["VisualSampler"]:::system
        SysDB["KnowledgeDB"]:::db
        SynEngine["BehaviorSynthesisEngine"]:::system
        GeminiVision{"Gemini 3.1 (Vision)"}:::model
        TruthMerger["DualAxisMerger"]:::system
    end

    subgraph "Memory & Storage"
        SqliteDB[("notion_soul.db")]:::db
        TasksDB[("Tasks [UT] Table")]:::db
        MemConsol["MemoryConsolidator"]:::system
        user_soul["user_soul.md"]:::db
    end

    User --> classify
    VisualSampler --> SynEngine
    SysDB --> SynEngine
    SynEngine --> GeminiVision
    GeminiVision --> TruthMerger
    SysDB --> TruthMerger
    TruthMerger --> SqliteDB
    
    SqliteDB --> MemConsol
    MemConsol --> user_soul
    
    user_soul -.->|Read| classify
    user_soul -.->|Read| handle_task
    
    handle_task -.->|Write| TasksDB
    handle_planner -.->|Read/Write| TasksDB
    handle_memory -.->|Write| SqliteDB
    
    classify -.->|Read| TasksDB
    """
    return {"mermaid": rich_mermaid}

@app.get("/api/v1/viz/nodes/{node_id}")
async def get_node_metadata(node_id: str):
    """Retrieves metadata for a specific architecture visualization node."""
    metadata = await orchestrator.get_node_metadata(node_id)
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return metadata

@app.get("/api/v1/viz/nodes")
async def get_all_nodes_metadata():
    """Retrieves metadata for all architecture visualization nodes."""
    return await orchestrator.get_all_nodes_metadata()
