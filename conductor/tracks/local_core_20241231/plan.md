# Implementation Plan: Build Local Core Foundation

## Phase 1: Local Database Design [checkpoint: 204857c]
- [x] Task: Define SQLite Schema with SQLAlchemy/Pydantic (a3bdf85)
    - [x] Create Task model with cognitive load and sync status fields
    - [x] Create UserSoul model for habit tracking
- [x] Task: Conductor - User Manual Verification 'Phase 1: Local Database Design' (Protocol in workflow.md)

## Phase 2: AI Adapter Implementation
- [x] Task: Implement Multi-modal Gemini Adapter (c42f5a9)
    - [x] Support flexible base_url and API key loading
    - [x] Implement asynchronous image/text hybrid request method
- [ ] Task: Conductor - User Manual Verification 'Phase 2: AI Adapter Implementation' (Protocol in workflow.md)
