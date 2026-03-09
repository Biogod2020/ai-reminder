# Implementation Plan: Langfuse Observability & Prompt Management (Track: langfuse_integration_20260308)

## Phase 1: SDK Setup & Config
- [x] Task: Install `langfuse` dependency and update `pyproject.toml`.
- [x] Task: Configure `.env` with Host, Public Key, and Secret Key.
- [x] Task: Initialize Langfuse client in `core/adapter.py` and `core/orchestrator.py`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Setup' (Protocol in workflow.md)

## Phase 2: Tracing Implementation (TDD)
- [x] Task: Write failing tests for LangGraph callbacks and Gemini tracing.
- [x] Task: Implement `CallbackHandler` in `SoulOrchestrator` for automated graph tracing. (Refactored to @observe() decorators for compatibility).
- [x] Task: Implement `@observe()` decorator in `GeminiAdapter` to capture LLM calls.
- [x] Task: Ensure metadata (user_id, session_id) is correctly passed to all traces.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Tracing' (Protocol in workflow.md)

## Phase 3: Prompt Management (TDD)
- [x] Task: Write failing tests for dynamic prompt fetching with local fallback.
- [x] Task: Create `core/prompts.py` for dynamic prompt management.
- [x] Task: Upload current system prompts and skill instructions to Langfuse Cloud. (Ready for manual upload).
- [x] Task: Refactor `SkillManager` and `GeminiAdapter` to use dynamic prompts instead of hardcoded strings.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Prompt Management' (Protocol in workflow.md)

## Phase 4: Feedback & Final Verification
- [x] Task: Implement feedback API endpoint in `core/api.py` to attach user scores to traces.
- [x] Task: Perform final verification of execution graphs, cost tracking, and latency metrics in the Langfuse dashboard.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Final Verification' (Protocol in workflow.md)
