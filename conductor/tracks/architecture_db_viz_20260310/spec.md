# Track Specification: Standalone Architecture Visualization Tool (architecture_db_viz_20260310)

## Overview
This track refactors the architecture visualization from a dashboard-integrated feature into a **standalone tool**. The goal is to provide a dedicated interactive HTML view that calls a metadata database, while keeping the main project UI clean. Additionally, we will leverage LangGraph's internal structure to automate data extraction.

## Goals
- **Decoupled Integration**: Revert the main dashboard (`App.tsx`) to its original state.
- **Dynamic Data Extraction**: Use LangGraph's built-in graph introspection to extract node structure and sync it to the SQLite database.
- **Standalone Interactive Tool**: Create a dedicated HTML/JS tool (independent of the main React SPA) that visualizes the graph and fetches detailed metadata from the database.
- **Simplicity**: Use LangGraph's native capabilities where possible to reduce manual metadata entry.

## Functional Requirements
1. **Frontend Reversion**: Remove the "Architecture" tab and related logic from the main application.
2. **LangGraph Sync**: Update the sync script to dynamically traverse the `SoulOrchestrator.graph` to identify nodes and edges.
3. **Standalone Viewer**: Implement a standalone HTML viewer (e.g., `docs/viz.html` or a separate Vite build target) using the interactive React Flow components developed previously.
4. **Metadata API**: Ensure the existing FastAPI metadata endpoints support the standalone viewer.

## Acceptance Criteria
- [ ] Main Dashboard no longer contains architecture visualization logic.
- [ ] A dedicated standalone entry point (HTML file or URL) exists for viewing the architecture.
- [ ] Visualization data is automatically derived from the LangGraph instance.
- [ ] Clicking nodes in the standalone viewer displays full metadata from the database.
