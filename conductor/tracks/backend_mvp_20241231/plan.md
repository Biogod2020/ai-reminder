# Implementation Plan: Backend MVP Refinement & API Optimization

## Phase 1: API Optimization ## Phase 1: API Optimization & Observability Observability [checkpoint: e2d7611]
- [x] Task: Implement API Proxy - [~] Task: Implement API Proxy & Authentication Authentication a4e7816
    - [x] Update `GeminiAdapter` to support local proxy switch and password auth.
    - [x] Add `USE_LOCAL_PROXY` and `PROXY_PASSWORD` to `.env`.
- [x] Task: Integrate Langfuse Tracing e975465
    - [x] Install `langfuse` and configure in `orchestrator.py`.
    - [x] Add tracing decorators/calls to LangGraph nodes.
- [x] Task: Conductor - User Manual Verification 'Phase 1: API Optimization - [ ] Task: Conductor - User Manual Verification 'Phase 1: API Optimization & Observability' (Protocol in workflow.md) Observability' (Protocol in workflow.md) e2d7611

## Phase 2: Persistence & Recursive Logic (ADaPT)
- [ ] Task: Implement Task Tree Persistence
    - [ ] Replace placeholders in `_node_handle_task` with real SQLAlchemy commits.
    - [ ] Ensure ADaPT sub-tasks are correctly linked via `parent_id`.
- [ ] Task: Implement Memory & Action Persistence
    - [ ] Implement actual write-back for `handle_memory` and user approvals.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Persistence & Recursive Logic' (Protocol in workflow.md)

## Phase 3: Strategic Features & Seeding
- [ ] Task: Implement Interleaving Algorithm
    - [ ] Logic to sequence tasks by alternating cognitive loads.
    - [ ] Update `get_optimized_view` to use this scientific ordering.
- [ ] Task: Create Data Seeding Script
    - [ ] Script to populate `notion_soul.db` with diverse sample tasks.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Strategic Features & Seeding' (Protocol in workflow.md)

## Phase 4: Validation & Tooling
- [ ] Task: Build CLI End-to-End Tester
    - [ ] Create `scripts/test_agent.py` to simulate multi-turn chats.
- [ ] Task: Comprehensive Integration Tests
    - [ ] Expand `tests/test_api.py` to cover full persistence and re-planning.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Validation & Tooling' (Protocol in workflow.md)
