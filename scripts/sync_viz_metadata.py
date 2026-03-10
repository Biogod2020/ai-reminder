import asyncio
import json
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from core.models import Base, VizMetadata
from core.orchestrator import SoulOrchestrator

async def sync_metadata_from_langgraph():
    print("Starting dynamic metadata synchronization from LangGraph...")
    db_url = "sqlite:///notion_soul.db"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    
    # Ensure tables are created
    Base.metadata.create_all(engine)
    
    # Instantiate Orchestrator to get the graph structure
    orchestrator = SoulOrchestrator()
    graph = orchestrator.graph.get_graph()
    
    # Extract nodes and edges
    # LangGraph's get_graph() returns a CompiledGraph which has nodes and edges
    graph_nodes = graph.nodes
    
    # Predefined descriptive metadata (to complement dynamic structure)
    # We map node names to their roles and descriptions
    node_descriptions = {
        "classify": {
            "role": "Intent Classifier",
            "description": "Analyzes user input using Gemini 3.1 Flash-Lite to determine the primary intent (task, memory, planner, or clarify).",
            "code_mapping": "core/orchestrator.py:_node_classify"
        },
        "handle_task": {
            "role": "Task Atomizer",
            "description": "Decomposes complex user requests into atomic, scientifically scheduled sub-tasks using the ADaPT protocol.",
            "code_mapping": "core/orchestrator.py:_node_handle_task"
        },
        "handle_memory": {
            "role": "Memory Synthesizer",
            "description": "Processes preferences and habits shared by the user, updating the local Soul model.",
            "code_mapping": "core/orchestrator.py:_node_handle_memory"
        },
        "handle_planner": {
            "role": "Macro Planner",
            "description": "Handles high-level daily/weekly re-scheduling and cognitive load balancing.",
            "code_mapping": "core/orchestrator.py:_node_handle_planner"
        },
        "handle_clarify": {
            "role": "Clarification Engine",
            "description": "Generates minimal clarification questions (MCQ) when user intent is too vague.",
            "code_mapping": "core/orchestrator.py:_node_handle_clarify"
        },
        "await_approval": {
            "role": "User Validation Gateway",
            "description": "Acts as a safety buffer, waiting for explicit user confirmation before finalizing changes.",
            "code_mapping": "core/orchestrator.py:_node_await_approval"
        },
        "notify": {
            "role": "Communication Dispatcher",
            "description": "Dispatches notifications and nudges via macOS / Bark notification channels.",
            "code_mapping": "core/orchestrator.py:_node_notify"
        }
    }

    with Session() as session:
        # 1. Clear or Update existing nodes from graph
        for node_id, node_obj in graph_nodes.items():
            if node_id in ["__start__", "__end__"]:
                continue
                
            desc_data = node_descriptions.get(node_id, {
                "role": "Internal Node",
                "description": f"Internal LangGraph node: {node_id}",
                "code_mapping": "core/orchestrator.py"
            })
            
            existing = session.query(VizMetadata).filter_by(node_id=node_id).first()
            
            metadata_payload = {
                "node_id": node_id,
                "role": desc_data["role"],
                "description": desc_data["description"],
                "code_mapping": desc_data["code_mapping"],
                "io_schema": json.dumps({"type": "AgentState"}), # Default for LangGraph nodes
                "load_metrics": json.dumps({"dynamic": True}),
                "metadata_json": json.dumps({
                    "type": str(type(node_obj)),
                    "is_dynamic": True
                })
            }
            
            if existing:
                print(f"Updating metadata for node: {node_id}")
                for key, value in metadata_payload.items():
                    setattr(existing, key, value)
            else:
                print(f"Creating metadata for node: {node_id}")
                new_node = VizMetadata(**metadata_payload)
                session.add(new_node)
        
        session.commit()
    print("Synchronization complete.")

if __name__ == "__main__":
    asyncio.run(sync_metadata_from_langgraph())
