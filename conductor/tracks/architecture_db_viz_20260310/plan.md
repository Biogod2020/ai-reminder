# Implementation Plan: Standalone Architecture Visualization Tool (architecture_db_viz_20260310)

## Phase 1: Reversion & Standalone Setup
Clean up the main UI and prepare the independent environment.

- [ ] Task: Revert `frontend/src/App.tsx` to remove the Architecture tab and related state.
- [ ] Task: Configure a standalone entry point for the visualization (e.g., `frontend/viz.html` or a dedicated Vite configuration).
- [ ] Task: Move `ArchitectureDashboard.tsx` logic to the standalone viewer.

## Phase 2: LangGraph Data Extraction
Automate the "Code -> DB" pipeline using LangGraph internals.

- [ ] Task: Refactor `scripts/sync_viz_metadata.py` to instantiate the Orchestrator and use `orchestrator.graph.get_graph()` to extract nodes/edges.
- [ ] Task: Ensure dynamic extraction handles new nodes automatically.
- [ ] Task: Verify sync script successfully updates `notion_soul.db`.

## Phase 3: Interactive HTML Development
Finalize the standalone viewing experience.

- [ ] Task: Ensure the standalone HTML tool can communicate with the FastAPI backend.
- [ ] Task: Implement a "Single-File Export" mode or a lightweight distribution method for the visualization.
- [ ] Task: Verify interactivity (zoom, pan, click for details) in the standalone tool.

## Phase 4: Final Refinement
- [ ] Task: Update documentation to explain how to access and update the standalone visualization tool.
- [ ] Task: Conductor - User Manual Verification 'Final Acceptance'
