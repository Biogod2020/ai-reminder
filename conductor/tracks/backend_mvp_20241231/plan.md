# Implementation Plan: Backend MVP Refinement & API Optimization

## Phase 1: API Optimization ## Phase 1: API Optimization & Observability Observability [checkpoint: e2d7611]
- [x] Task: Implement API Proxy - [~] Task: Implement API Proxy & Authentication Authentication a4e7816
    - [x] Update `GeminiAdapter` to support local proxy switch and password auth.
    - [x] Add `USE_LOCAL_PROXY` and `PROXY_PASSWORD` to `.env`.
- [x] Task: Integrate Langfuse Tracing e975465
    - [x] Install `langfuse` and configure in `orchestrator.py`.
    - [x] Add tracing decorators/calls to LangGraph nodes.
- [x] Task: Conductor - User Manual Verification 'Phase 1: API Optimization - [ ] Task: Conductor - User Manual Verification 'Phase 1: API Optimization & Observability' (Protocol in workflow.md) Observability' (Protocol in workflow.md) e2d7611

## Phase 2: Persistence ## Phase 2: Persistence & Recursive Logic (ADaPT) Recursive Logic (ADaPT) [checkpoint: 3866728]
- [x] Task: Implement Task Tree Persistence d9c16c0
    - [x] Replace placeholders in `_node_handle_task` with real SQLAlchemy commits.
    - [x] Ensure ADaPT sub-tasks are correctly linked via `parent_id`.
- [x] Task: Implement Memory - [~] Task: Implement Memory & Action Persistence Action Persistence d1f7a7e
    - [x] Implement actual write-back for `handle_memory` and user approvals.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Persistence - [ ] Task: Conductor - User Manual Verification 'Phase 2: Persistence & Recursive Logic' (Protocol in workflow.md) Recursive Logic' (Protocol in workflow.md) 3866728

## Phase 3: Strategic Features ## Phase 3: Strategic Features & Seeding Seeding [checkpoint: d117508]
- [x] Task: Implement Interleaving Algorithm 888a9b4
    - [x] Logic to sequence tasks by alternating cognitive loads.
    - [x] Update `get_optimized_view` to use this scientific ordering.
- [x] Task: Create Data Seeding Script 8167d14
    - [x] Script to populate `notion_soul.db` with diverse sample tasks.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Strategic Features - [ ] Task: Conductor - User Manual Verification 'Phase 3: Strategic Features & Seeding' (Protocol in workflow.md) Seeding' (Protocol in workflow.md) d117508

## Phase 4: Validation & Tooling
- [x] Task: Build CLI End-to-End Tester f07c353
    - [x] Create `scripts/test_agent.py` to simulate multi-turn chats.
- [x] Task: Comprehensive Integration Tests 1b988d4
    - [x] Expand `tests/test_api.py` to cover full persistence and re-planning.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Validation & Tooling' (Protocol in workflow.md)
