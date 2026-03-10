import asyncio
import json
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from core.models import Base, VizMetadata
from core.orchestrator import SoulOrchestrator

async def sync_metadata():
    print("Starting metadata synchronization...")
    db_url = "sqlite:///notion_soul.db"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    
    # Predefined metadata for the core LangGraph nodes
    nodes_metadata = [
        {
            "node_id": "classify",
            "role": "Intent Classifier",
            "description": "Analyzes user input using Gemini 3.1 Flash-Lite to determine the primary intent (task, memory, planner, or clarify) based on global context.",
            "code_mapping": "core/orchestrator.py:_node_classify",
            "io_schema": json.dumps({
                "input": "AgentState (user_input)",
                "output": "AgentState (intent)"
            }),
            "load_metrics": json.dumps({
                "cognitive_load_impact": "Medium (Analysis phase)"
            }),
            "metadata_json": json.dumps({
                "tags": ["AI", "Routing"]
            })
        },
        {
            "node_id": "handle_task",
            "role": "Task Atomizer",
            "description": "Decomposes complex user requests into atomic, scientifically scheduled sub-tasks using the ADaPT protocol and empathetic narrative reasoning.",
            "code_mapping": "core/orchestrator.py:_node_handle_task",
            "io_schema": json.dumps({
                "input": "AgentState (user_input)",
                "output": "AgentState (proposed_actions, response)"
            }),
            "load_metrics": json.dumps({
                "cognitive_load_impact": "High (Planning phase)"
            }),
            "metadata_json": json.dumps({
                "tags": ["ADaPT", "Persistence"]
            })
        },
        {
            "node_id": "handle_memory",
            "role": "Memory Synthesizer",
            "description": "Processes preferences and habits shared by the user, updating both the local Markdown 'Soul' and the SQLite persistence layer.",
            "code_mapping": "core/orchestrator.py:_node_handle_memory",
            "io_schema": json.dumps({
                "input": "AgentState (user_input)",
                "output": "AgentState (response, notify_user)"
            }),
            "load_metrics": json.dumps({
                "cognitive_load_impact": "Low (Information capture)"
            }),
            "metadata_json": json.dumps({
                "tags": ["Memory", "Soul"]
            })
        },
        {
            "node_id": "handle_planner",
            "role": "Macro Planner",
            "description": "Handles high-level daily/weekly re-scheduling and cognitive load balancing across all active tasks.",
            "code_mapping": "core/orchestrator.py:_node_handle_planner",
            "io_schema": json.dumps({
                "input": "AgentState",
                "output": "AgentState (response)"
            }),
            "load_metrics": json.dumps({
                "cognitive_load_impact": "Very High (Strategy phase)"
            }),
            "metadata_json": json.dumps({
                "status": "Pending implementation"
            })
        },
        {
            "node_id": "handle_clarify",
            "role": "Clarification Engine",
            "description": "Generates minimal clarification questions (MCQ) when user intent is too vague to be scientifically scheduled.",
            "code_mapping": "core/orchestrator.py:_node_handle_clarify",
            "io_schema": json.dumps({
                "input": "AgentState (user_input)",
                "output": "AgentState (response)"
            }),
            "load_metrics": json.dumps({
                "cognitive_load_impact": "Low (Interaction phase)"
            }),
            "metadata_json": json.dumps({
                "tags": ["MCQ", "UX"]
            })
        },
        {
            "node_id": "await_approval",
            "role": "User Validation Gateway",
            "description": "Acts as a safety buffer, waiting for explicit user confirmation before finalizing task persistence or significant schedule changes.",
            "code_mapping": "core/orchestrator.py:_node_await_approval",
            "io_schema": json.dumps({
                "input": "AgentState",
                "output": "AgentState (response)"
            }),
            "load_metrics": json.dumps({
                "cognitive_load_impact": "Zero (Passive wait)"
            }),
            "metadata_json": json.dumps({
                "tags": ["Safety", "UX"]
            })
        },
        {
            "node_id": "notify",
            "role": "Communication Dispatcher",
            "description": "Dispatches notifications and nudges via macOS / Bark notification channels based on the agent's active state.",
            "code_mapping": "core/orchestrator.py:_node_notify",
            "io_schema": json.dumps({
                "input": "AgentState (response)",
                "output": "AgentState"
            }),
            "load_metrics": json.dumps({
                "cognitive_load_impact": "Zero (I/O operation)"
            }),
            "metadata_json": json.dumps({
                "channels": ["macOS", "Bark"]
            })
        }
    ]

    # Ensure tables are created
    Base.metadata.create_all(engine)
    
    with Session() as session:
        for node_data in nodes_metadata:
            # Check if exists
            existing = session.query(VizMetadata).filter_by(node_id=node_data["node_id"]).first()
            if existing:
                print(f"Updating metadata for node: {node_data['node_id']}")
                for key, value in node_data.items():
                    setattr(existing, key, value)
            else:
                print(f"Creating metadata for node: {node_data['node_id']}")
                new_node = VizMetadata(**node_data)
                session.add(new_node)
        
        session.commit()
    print("Synchronization complete.")

if __name__ == "__main__":
    asyncio.run(sync_metadata())
