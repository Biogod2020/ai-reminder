# Implementation Plan: Build Universal Soul Console (MVP)

## Phase 1: Chainlit UI & Basic Dispatcher
- [ ] Task: Scaffold Chainlit UI and Multi-modal Input
    - [ ] Create `ui/console.py` with basic Chainlit setup.
    - [ ] Implement message history and thought visualization blocks.
- [ ] Task: Implement NL Intent Dispatcher (LangGraph)
    - [ ] Create `core/orchestrator.py` with a LangGraph state machine.
    - [ ] Define intent classification nodes (Memory, Task, Planner, Clarify).
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Chainlit UI & Basic Dispatcher' (Protocol in workflow.md)

## Phase 2: Memory & Task Integration
- [ ] Task: Integrate Memory Framework (mem0/Letta)
    - [ ] Install and configure `mem0` or `letta` for local use.
    - [ ] Implement `SoulMemory` class to bridge the framework with `user_soul.md`.
- [ ] Task: Implement Task Creation & Atomization Action
    - [ ] Link the dispatcher to the existing `decompose_task` logic.
    - [ ] Create a confirmation card in Chainlit for task approval.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Memory & Task Integration' (Protocol in workflow.md)

## Phase 3: Adaptive Weekly Re-planner
- [ ] Task: Implement 'Full Weekly Re-plan' Skill
    - [ ] Create `core/skills/week-planner/SKILL.md` with Interleaving and UMP logic.
    - [ ] Implement the planning tool in the orchestrator.
- [ ] Task: Implement Active Clarification Loop
    - [ ] Integrate MCQ (Minimal Clarification Question) into the console flow.
    - [ ] Verify that re-plans correctly use the updated Soul Context.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Adaptive Weekly Re-planner' (Protocol in workflow.md)
