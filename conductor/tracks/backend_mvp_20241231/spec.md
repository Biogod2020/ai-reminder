# Specification: Backend MVP Refinement & API Optimization

## Overview
This track aims to mature the Notion-Soul-Agent backend to a robust MVP level. It transitions from placeholders to functional implementations of task persistence, recursive atomization, and strategic interleaving, while optimizing API usage via a local proxy.

## Functional Requirements
- **Full Database Persistence:** Replace placeholders in `SoulOrchestrator` with real SQLAlchemy logic to commit tasks, sub-tasks, and memory updates to the local SQLite database.
- **Strategic Recursive Logic (ADaPT):** Implement the full ADaPT protocol to recursively decompose tasks and store them in the hierarchical `parent_id` tree.
- **Interleaving Algorithm:** Implement the logic to return task sequences that interleave different cognitive loads (heavy/light) based on SOTA principles.
- **API Proxy Integration:**
    - Support `localhost:8888` as a configurable base URL.
    - Implement authentication for the proxy (Password: 123456).
    - Manage the switch via an environment variable or auto-detection for easy maintenance.
- **Observability Hub:** Integrate Langfuse to trace all AI reasoning steps, intent classifications, and task decompositions.
- **Data Seeding:** Provide a script to populate the local database with a representative set of tasks for testing.

## Technical Requirements
- **Frameworks:** FastAPI, SQLAlchemy, LangGraph, Langfuse.
- **Persistence:** Local SQLite (`notion_soul.db`).
- **Validation Tools:** 
    - Automated Integration Tests (`TestClient`).
    - A specialized CLI Tester script for simulating end-to-end user flows.
- **API Security:** Securely handle the proxy password without hardcoding (via `.env`).

## Acceptance Criteria
- Tasks added via `/chat` are correctly atomized and saved to the SQLite task tree.
- The `/get_view_data` endpoint returns a scientific sequence of tasks (Interleaving).
- AI reasoning steps are visible in the Langfuse dashboard.
- The system can toggle between local proxy and Google native API without code changes.
- A seed script successfully populates the database for immediate testing.
