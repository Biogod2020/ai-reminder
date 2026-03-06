# Implementation Plan: Proactive Wisdom & Dynamic Buffer (Proactive Soul)

## Phase 1: Dynamic Slack ## Phase 1: Dynamic Slack & Refined Decomposition Refined Decomposition [checkpoint: 43cf231]
- [x] Task: Update Task model and Atomizer Skill e3d68e2
    - [x] Update `Task` model in `core/models.py` to include `duration_minutes` and `slack_minutes`.
    - [x] Implement Slack estimation prompts in `core/skills/task-atomizer/SKILL.md`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Dynamic Slack - [ ] Task: Conductor - User Manual Verification 'Phase 1: Dynamic Slack & Refined Decomposition' (Protocol in workflow.md) Refined Decomposition' (Protocol in workflow.md) 43cf231

## Phase 2: Adaptive Heartbeat & Nudge Logic
- [x] Task: Implement Heartbeat Logic Hub fc3c809
    - [x] Create `_node_evaluate_nudge` in orchestrator to decide if a nudge is timely.
    - [x] Create `core/skills/proactive-nudger/SKILL.md` with scientific reasoning logic.
- [ ] Task: Implement /heartbeat API endpoint
    - [ ] Expose endpoint in `core/api.py` to trigger AI-initiated status checks.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Adaptive Heartbeat & Nudge Logic' (Protocol in workflow.md)

## Phase 3: Delay Handling & Scientific Re-plan
- [ ] Task: Implement /handle_response and Re-plan logic
    - [ ] Logic to process feedback like "I'm exhausted" and re-apply Interleaving to the remaining schedule.
    - [ ] Add `slack_minutes` visibility to `/get_view_data`.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Delay Handling & Scientific Re-plan' (Protocol in workflow.md)
