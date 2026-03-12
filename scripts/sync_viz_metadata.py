import asyncio
import json
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from core.models import Base, VizMetadata
from core.orchestrator import SoulOrchestrator

async def sync_metadata_from_langgraph():
    print("Starting comprehensive metadata synchronization with State Awareness...")
    db_url = "sqlite:///notion_soul.db"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    
    orchestrator = SoulOrchestrator()
    graph_nodes = orchestrator.graph.get_graph().nodes
    
    # 1. CORE LangGraph Nodes with explicit Read/Write channels
    core_descriptions = {
        "classify": {
            "role": "Intent Classifier",
            "description": "Analyzes raw input to route intent.",
            "code_mapping": "core/orchestrator.py:_node_classify",
            "read": ["user_input", "history"],
            "write": ["intent"]
        },
        "handle_task": {
            "role": "Task Atomizer",
            "description": "Decomposes goals into atomic subtasks.",
            "code_mapping": "core/orchestrator.py:_node_handle_task",
            "read": ["user_input", "intent", "history"],
            "write": ["proposed_actions", "response"]
        },
        "handle_memory": {
            "role": "Memory Synthesizer",
            "description": "Extracts habits and updates the Soul model.",
            "code_mapping": "core/orchestrator.py:_node_handle_memory",
            "read": ["user_input"],
            "write": ["response", "notify_user"]
        },
        "handle_planner": {
            "role": "Macro Planner",
            "description": "Optimized re-planning based on cognitive load.",
            "code_mapping": "core/orchestrator.py:_node_handle_planner",
            "read": ["history", "proposed_actions"],
            "write": ["response"]
        },
        "handle_clarify": {
            "role": "Clarification Engine",
            "description": "Generates MCQ for vague inputs.",
            "code_mapping": "core/orchestrator.py:_node_handle_clarify",
            "read": ["user_input"],
            "write": ["response"]
        },
        "await_approval": {
            "role": "User Validation Gateway",
            "description": "Suspends graph for user confirmation.",
            "code_mapping": "core/orchestrator.py:_node_await_approval",
            "read": ["proposed_actions"],
            "write": ["needs_approval", "response"]
        },
        "notify": {
            "role": "Communication Dispatcher",
            "description": "Sends alerts via OS channels.",
            "code_mapping": "core/orchestrator.py:_node_notify",
            "read": ["response"],
            "write": ["notify_user"]
        }
    }

    with Session() as session:
        # Sync Core Nodes
        for node_id in graph_nodes.keys():
            if node_id in ["__start__", "__end__"]: continue
            desc = core_descriptions.get(node_id, {"role": "Internal", "description": "Node", "read": [], "write": []})
            payload = {
                "node_id": node_id,
                "role": desc["role"],
                "description": desc["description"],
                "code_mapping": desc.get("code_mapping", "core/orchestrator.py"),
                "io_schema": json.dumps({
                    "input": "AgentState (" + ", ".join(desc["read"]) + ")",
                    "output": "AgentState (" + ", ".join(desc["write"]) + ")"
                }),
                "load_metrics": json.dumps({"reads": desc["read"], "writes": desc["write"]}),
                "metadata_json": json.dumps({"category": "LangGraph"})
            }
            existing = session.query(VizMetadata).filter_by(node_id=node_id).first()
            if existing:
                for k, v in payload.items(): setattr(existing, k, v)
            else:
                session.add(VizMetadata(**payload))
        
        session.commit()
    print("Metadata sync complete.")

if __name__ == "__main__":
    asyncio.run(sync_metadata_from_langgraph())
