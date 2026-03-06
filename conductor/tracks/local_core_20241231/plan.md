# Implementation Plan: Build AI-Native Core & Soul Memory

## Phase 1: Native Skill System & Recursive Models
- [ ] Task: Initialize Skill Architecture & Update Models
    - [ ] Create `core/skills/` directory and define `SkillManager`
    - [ ] Implement initial `task-atomizer/SKILL.md` with ADaPT protocol
    - [ ] Update `Task` model in `core/models.py` to support `parent_id` (recursive)
    - [ ] Implement `MemoryManager` for `user_soul.md`
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Native Skill System & Recursive Models' (Protocol in workflow.md)

## Phase 2: AI Strategist Integration
- [ ] Task: Implement Skill-based Reasoning in Adapter
    - [ ] Update `GeminiAdapter` to support dynamic skill mounting
    - [ ] Implement `decompose_task` using `task-atomizer` skill
    - [ ] Create `narrative-soul` skill for rewarding micro-feedback
- [ ] Task: Conductor - User Manual Verification 'Phase 2: AI Strategist Integration' (Protocol in workflow.md)
