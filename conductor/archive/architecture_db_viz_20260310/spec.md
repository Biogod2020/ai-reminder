# Track Specification: Architecture Visualization & Node Database (architecture_db_viz_20260310)

## Overview
This track aims to upgrade the project's architecture visualization (`architecture_v2.html`) from a static, limited view to a dynamic, data-driven, and interactive experience. The core improvement involves moving node metadata into a centralized SQLite database and enhancing the frontend with modern navigation (zoom/pan, responsiveness, and collapsible groups), leveraging LangGraph's native capabilities where applicable.

## Goals
- **Data-Driven Visualization:** Decouple node metadata (descriptions, schemas, metrics) from the visual layout code into a database.
- **Enhanced UI/UX:** Resolve the "small view" issue by implementing a responsive, zoomable, and pannable canvas.
- **Comprehensive Information:** Ensure every node has detailed hover/click information covering roles, code mapping, and cognitive load metrics.
- **LangGraph Integration:** Explore and utilize LangGraph's native graph-drawing or state-tracking features to simplify maintenance.

## Functional Requirements

### 1. Database Schema (`viz_metadata`)
Create a table in `notion_soul.db` (or a dedicated `viz_soul.db`) to store:
- `node_id`: Unique identifier matching the graph node.
- `role`: The primary purpose of the node (e.g., "Synthesizer", "Classifier").
- `description`: A detailed explanation of the node's logic.
- `code_mapping`: Path to the relevant Python file/function.
- `io_schema`: Input and output data structures.
- `load_metrics`: Estimated cognitive load or energy cost (for the scheduler).
- `metadata_json`: A flexible field for additional context (tags, links).

### 2. Frontend Enhancement (`architecture_v3.html` or similar)
- **Responsive Canvas:** A full-screen container that adapts to browser resizing.
- **Interactive Controls:** Zoom-to-fit, pan-to-explore, and node-search capabilities.
- **Detail Overlay/Hover:** A sidebar or tooltip that fetches data from the database for the active node.
- **Collapsible Hierarchies:** Support for "sub-graphs" or grouped nodes that can be collapsed to manage visual complexity.

### 3. Backend Integration
- **Metadata API:** A lightweight FastAPI endpoint (or simple local fetch script) to serve node data to the HTML view.
- **Auto-Sync (Optional):** A script to parse LangGraph definitions and seed/update the metadata database.

## Non-Functional Requirements
- **Performance:** Zooming and panning should be smooth even with 50+ nodes.
- **Maintainability:** Adding a new node to the LangGraph should automatically or semi-automatically update the visualization metadata.

## Acceptance Criteria
- [ ] `architecture_v2.html` is replaced by or upgraded to a new version with a large, responsive view.
- [ ] All nodes in the graph have a corresponding entry in the SQLite database.
- [ ] Hovering over or clicking a node displays comprehensive metadata (Role, Code, I/O, Load).
- [ ] The visualization supports zoom and pan.
- [ ] The solution is integrated with the existing LangGraph structure where possible.

## Out of Scope
- Real-time "live" execution monitoring (showing nodes light up as they run) is deferred to a later track unless natively supported by a chosen library.
