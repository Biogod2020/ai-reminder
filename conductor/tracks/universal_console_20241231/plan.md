# Implementation Plan: Build Universal Soul Console (MVP)

## Phase 1: Chainlit UI & Basic Dispatcher [checkpoint: f17052e]
- [x] Task: Scaffold Chainlit UI and Multi-modal Input f17052e
    - [x] Create `ui/console.py` with basic Chainlit setup.
    - [x] Implement message history and thought visualization blocks.
- [x] Task: Implement NL Intent Dispatcher (LangGraph) f17052e
    - [x] Create `core/orchestrator.py` with a LangGraph state machine.
    - [x] Define intent classification nodes (Memory, Task, Planner, Clarify).
- [x] Task: Conductor - User Manual Verification 'Phase 1: Chainlit UI & Basic Dispatcher' (Protocol in workflow.md)

## Phase 2: Memory & Task Integration [checkpoint: 765239b]
- [x] Task: Integrate Memory Framework (mem0/Letta) 7dda6c0
    - [x] Install and configure `mem0` or `letta` for local use.
    - [x] Implement `SoulMemory` class to bridge the framework with `user_soul.md`.
- [x] Task: Implement Task Creation & Atomization Action 4c06370
    - [x] Link the dispatcher to the existing `decompose_task` logic.
    - [x] Create a confirmation card in Chainlit for task approval.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Memory & Task Integration' (Protocol in workflow.md)

## Phase 3: Headless API Service (FastAPI Hub)
- [x] Task: Scaffold FastAPI Service and Local Hooks 3212767
    - [x] Install `fastapi` and `uvicorn`.
    - [x] Create `core/api.py` to wrap the Orchestrator.
- [x] Task: Implement Structured Dashboard Endpoints e1a804a
    - [x] Define `/get_view_data` to return interleaved calendar/kanban JSON.
    - [x] Define `/chat` for Flutter-to-Python communication.
- [ ] Task: Integrate Bark/Mobile Notification Hook
    - [ ] Implement a tool node for cross-platform push notifications.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Headless API Service' (Protocol in workflow.md)
