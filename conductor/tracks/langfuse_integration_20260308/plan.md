# Implementation Plan: Langfuse Observability & Prompt Management (Track: langfuse_integration_20260308)

## Phase 1: SDK Setup & Config
- [ ] Task: Install `langfuse` dependency and update `pyproject.toml`.
- [ ] Task: Configure `.env` with Host, Public Key, and Secret Key.
- [ ] Task: Initialize Langfuse client in `core/adapter.py` and `core/orchestrator.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Setup' (Protocol in workflow.md)

## Phase 2: Tracing Implementation (TDD)
- [ ] Task: Write failing tests for LangGraph callbacks and Gemini tracing.
- [ ] Task: Implement `CallbackHandler` in `SoulOrchestrator` for automated graph tracing.
- [ ] Task: Implement `@observe()` decorator in `GeminiAdapter` to capture LLM calls.
- [ ] Task: Ensure metadata (user_id, session_id) is correctly passed to all traces.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Tracing' (Protocol in workflow.md)

## Phase 3: Prompt Management (TDD)
- [ ] Task: Write failing tests for dynamic prompt fetching with local fallback.
- [ ] Task: Create `core/prompts.py` for dynamic prompt management.
- [ ] Task: Upload current system prompts and skill instructions to Langfuse Cloud.
- [ ] Task: Refactor `SkillManager` and `GeminiAdapter` to fetch prompts dynamically.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Prompt Management' (Protocol in workflow.md)

## Phase 4: Feedback & Final Verification
- [ ] Task: Implement feedback API endpoint in `core/api.py` to attach user scores to traces.
- [ ] Task: Perform final verification of execution graphs, cost tracking, and latency metrics in the Langfuse dashboard.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Verification' (Protocol in workflow.md)
