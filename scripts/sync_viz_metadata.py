import asyncio
import json
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from core.models import Base, VizMetadata
from core.orchestrator import SoulOrchestrator

async def sync_metadata_from_langgraph():
    print("Starting comprehensive metadata synchronization...")
    db_url = "sqlite:///notion_soul.db"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    
    # Ensure tables are created
    Base.metadata.create_all(engine)
    
    # Instantiate Orchestrator to get the dynamic graph structure
    orchestrator = SoulOrchestrator()
    graph_nodes = orchestrator.graph.get_graph().nodes
    
    # 1. CORE LangGraph Nodes (Dynamic Extraction)
    core_descriptions = {
        "classify": {
            "role": "Intent Classifier",
            "description": "Analyzes user input using Gemini 3.1 Flash-Lite to determine the primary intent.",
            "code_mapping": "core/orchestrator.py:_node_classify"
        },
        "handle_task": {
            "role": "Task Atomizer",
            "description": "Decomposes goals into atomic subtasks using ADaPT and empathetic reasoning.",
            "code_mapping": "core/orchestrator.py:_node_handle_task"
        },
        "handle_memory": {
            "role": "Memory Synthesizer",
            "description": "Extracts durable facts or habits and updates the local Soul model.",
            "code_mapping": "core/orchestrator.py:_node_handle_memory"
        },
        "handle_planner": {
            "role": "Macro Planner",
            "description": "Analyzes schedule density and cognitive load to propose optimized re-planning.",
            "code_mapping": "core/orchestrator.py:_node_handle_planner"
        },
        "handle_clarify": {
            "role": "Clarification Engine",
            "description": "Generates minimal clarification questions (MCQ) when intent confidence is low.",
            "code_mapping": "core/orchestrator.py:_node_handle_clarify"
        },
        "await_approval": {
            "role": "User Validation Gateway",
            "description": "Suspends execution until user explicitly approves proposed changes.",
            "code_mapping": "core/orchestrator.py:_node_await_approval"
        },
        "notify": {
            "role": "Communication Dispatcher",
            "description": "Dispatches notifications and nudges via macOS or Bark channels.",
            "code_mapping": "core/orchestrator.py:_node_notify"
        }
    }

    # 2. SYSTEM Components (Static/Environmental Nodes in the Blueprint)
    system_nodes = [
        {
            "node_id": "VisualSampler",
            "role": "Perception",
            "description": "Captures high-resolution screen frames at regular intervals for behavioral analysis.",
            "code_mapping": "core/visual_sampler.py",
            "io_schema": json.dumps({"input": "Retina Screen", "output": "JPEG Frames"})
        },
        {
            "node_id": "KnowledgeDB",
            "role": "System DB",
            "description": "Directly interface with macOS knowledgeC.db to extract app usage and duration logs.",
            "code_mapping": "core/system_db.py",
            "io_schema": json.dumps({"input": "SQLite Binary", "output": "App Timelines"})
        },
        {
            "node_id": "BehaviorSynthesisEngine",
            "role": "Core Logic",
            "description": "Orchestrates the analysis of visual frames and system logs to reconstruct behavioral truth.",
            "code_mapping": "core/synthesis_engine.py",
            "io_schema": json.dumps({"input": "Frames + Timelines", "output": "Behavior Log"})
        },
        {
            "node_id": "GeminiVision",
            "role": "VLM",
            "description": "Gemini 3.1 multi-modal engine analyzing visual state to determine semantic intent.",
            "code_mapping": "Gemini API (External)",
            "io_schema": json.dumps({"input": "Image Batches", "output": "Intent Axis"})
        },
        {
            "node_id": "TruthMerger",
            "role": "Algorithm",
            "description": "Aligns asynchronous visual points with system duration blocks using temporal gap-filling.",
            "code_mapping": "core/truth_merger.py",
            "io_schema": json.dumps({"input": "System + AI Axis", "output": "Merged Omni Log"})
        },
        {
            "node_id": "SqliteDB",
            "role": "Persistence",
            "description": "Primary local SQLite storage (notion_soul.db) with WAL enabled for high concurrency.",
            "code_mapping": "notion_soul.db",
            "io_schema": json.dumps({"input": "Raw Logs", "output": "Structured Data"})
        },
        {
            "node_id": "TasksDB",
            "role": "Logic DB",
            "description": "The SQLite implementation of the Notion 'Tasks [UT]' mirror table.",
            "code_mapping": "SQL: tasks_table",
            "io_schema": json.dumps({"input": "Proposed Steps", "output": "Scheduled Work"})
        },
        {
            "node_id": "MemConsol",
            "role": "Agent",
            "description": "Distills daily raw logs into durable habit summaries and long-term insights.",
            "code_mapping": "core/consolidator.py",
            "io_schema": json.dumps({"input": "Omni Logs", "output": "Soul Summaries"})
        },
        {
            "node_id": "user_soul",
            "role": "Context",
            "description": "The Markdown 'Digital Soul' of the user, used as a 1M token context for every AI decision.",
            "code_mapping": "user_soul.md",
            "io_schema": json.dumps({"input": "Summaries", "output": "Context Injection"})
        },
        {
            "node_id": "evaluate_nudge",
            "role": "Proactive",
            "description": "Background loop monitoring in-progress tasks to trigger empathetic nudges.",
            "code_mapping": "core/orchestrator.py:evaluate_nudge",
            "io_schema": json.dumps({"input": "Task Status", "output": "Nudge Decision"})
        },
        {
            "node_id": "get_optimized_view",
            "role": "API",
            "description": "FastAPI endpoint serving scientifically interleaved tasks to the frontend dashboard.",
            "code_mapping": "core/api.py:get_view_data",
            "io_schema": json.dumps({"input": "Tasks [UT]", "output": "Dashboard JSON"})
        }
    ]

    with Session() as session:
        # Sync Core Nodes
        for node_id in graph_nodes.keys():
            if node_id in ["__start__", "__end__"]: continue
            desc = core_descriptions.get(node_id, {"role": "Internal", "description": "LangGraph Core Node", "code_mapping": "core/orchestrator.py"})
            payload = {
                "node_id": node_id,
                "role": desc["role"],
                "description": desc["description"],
                "code_mapping": desc["code_mapping"],
                "io_schema": json.dumps({"type": "AgentState"}),
                "load_metrics": json.dumps({"dynamic": True}),
                "metadata_json": json.dumps({"category": "LangGraph"})
            }
            existing = session.query(VizMetadata).filter_by(node_id=node_id).first()
            if existing:
                for k, v in payload.items(): setattr(existing, k, v)
            else:
                session.add(VizMetadata(**payload))

        # Sync System Nodes
        for node_data in system_nodes:
            existing = session.query(VizMetadata).filter_by(node_id=node_data["node_id"]).first()
            payload = {
                **node_data,
                "load_metrics": json.dumps({"type": "System"}),
                "metadata_json": json.dumps({"category": "Environment"})
            }
            if existing:
                for k, v in payload.items(): setattr(existing, k, v)
            else:
                session.add(VizMetadata(**payload))
        
        session.commit()
    print("Comprehensive synchronization complete.")

if __name__ == "__main__":
    asyncio.run(sync_metadata_from_langgraph())
