# Implementation Plan: Proactive Wisdom & Dynamic Buffer (Proactive Soul)

## Phase 1: Dynamic Slack & Refined Decomposition
- [~] Task: Update Task model and Atomizer Skill
    - [ ] Update `Task` model in `core/models.py` to include `duration_minutes` and `slack_minutes`.
    - [ ] Implement Slack estimation prompts in `core/skills/task-atomizer/SKILL.md`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Dynamic Slack & Refined Decomposition' (Protocol in workflow.md)

## Phase 2: Adaptive Heartbeat & Nudge Logic
- [ ] Task: Implement Heartbeat Logic Hub
    - [ ] Create `_node_evaluate_nudge` in orchestrator to decide if a nudge is timely.
    - [ ] Create `core/skills/proactive-nudger/SKILL.md` with scientific reasoning logic.
- [ ] Task: Implement /heartbeat API endpoint
    - [ ] Expose endpoint in `core/api.py` to trigger AI-initiated status checks.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Adaptive Heartbeat & Nudge Logic' (Protocol in workflow.md)

## Phase 3: Delay Handling & Scientific Re-plan
- [ ] Task: Implement /handle_response and Re-plan logic
    - [ ] Logic to process feedback like "I'm exhausted" and re-apply Interleaving to the remaining schedule.
    - [ ] Add `slack_minutes` visibility to `/get_view_data`.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Delay Handling & Scientific Re-plan' (Protocol in workflow.md)
