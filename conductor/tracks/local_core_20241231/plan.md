# Implementation Plan: Build AI-Native Core & Soul Memory

## Phase 1: Native Skill System & Recursive Models [checkpoint: b5de428]
- [x] Task: Initialize Skill Architecture & Update Models (1a59a5a)
    - [x] Create `core/skills/` directory and define `SkillManager`
    - [x] Implement initial `task-atomizer/SKILL.md` with ADaPT protocol
    - [x] Update `Task` model in `core/models.py` to support `parent_id` (recursive)
    - [x] Implement `MemoryManager` for `user_soul.md`
- [x] Task: Conductor - User Manual Verification 'Phase 1: Native Skill System & Recursive Models' (Protocol in workflow.md)

## Phase 2: AI Strategist Integration
- [x] Task: Implement Skill-based Reasoning in Adapter (555170a)
    - [x] Update `GeminiAdapter` to support dynamic skill mounting
    - [x] Implement `decompose_task` using `task-atomizer` skill
    - [x] Create `narrative-soul` skill for rewarding micro-feedback
- [~] Task: Conductor - User Manual Verification 'Phase 2: AI Strategist Integration' (Protocol in workflow.md)
