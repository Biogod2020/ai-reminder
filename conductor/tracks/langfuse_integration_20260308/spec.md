# Specification: Langfuse Observability & Prompt Management (Track: langfuse_integration_20260308)

## Overview
This track implements deep observability and professional prompt management for the Notion-Soul-Agent using Langfuse Cloud. By integrating Langfuse, we will gain visibility into AI reasoning paths, monitor latency and costs, decouple prompts from the source code, and collect structured user feedback to drive future RLHF improvements.

## Goals
- **Full Traceability:** Monitor every step of the LangGraph execution and Gemini 3.1 generations.
- **Prompt Decoupling:** Migrate all system prompts and skill-specific instructions to Langfuse Prompt Management.
- **Performance Monitoring:** Track latency, token usage, and cost for the Gemini 3.1 Flash-Lite model.
- **Feedback Loop:** Enable capturing user "Approve/Reject" signals directly into Langfuse traces.
- **Workflow Visualization:** Leverage LangGraph + Langfuse integration to visualize execution graphs.

## Functional Requirements
1. **Core Integration:**
   - Configure Langfuse SDK with the provided credentials in `.env`.
   - Wrap `GeminiAdapter.generate_content` using the `@observe()` decorator or manual trace methods to capture inputs, outputs, and metadata.
2. **LangGraph Observability:**
   - Integrate the `CallbackHandler` into the `SoulOrchestrator` to automatically trace node transitions and state changes.
3. **Prompt Management System:**
   - Create a `PromptManager` utility to fetch prompts from Langfuse with local caching.
   - Refactor `SkillManager` and `GeminiAdapter` to use dynamic prompts instead of hardcoded strings.
4. **Feedback & Scores:**
   - Implement an API hook to attach scores (e.g., `user-approval`) to specific traces when a user interacts with a nudge or task suggestion.
5. **Visualization:**
   - Ensure the execution graph is correctly represented in the Langfuse UI, showing the relationship between memory retrieval, intent classification, and task decomposition.

## Non-Functional Requirements
- **Robustness:** The agent must fall back to local hardcoded prompts if Langfuse Cloud is unreachable.
- **Efficiency:** Use asynchronous logging to ensure observability doesn't block the main execution loop.
- **Security:** Ensure credentials are never committed to the repository (stored in `.env`).

## Acceptance Criteria
- [ ] Every user interaction generates a complete trace in Langfuse Cloud.
- [ ] Modifying a prompt in the Langfuse UI immediately updates the agent's behavior without code changes.
- [ ] Detailed token usage and cost analysis are visible in the Langfuse dashboard.
- [ ] User feedback (Approve/Reject) is correctly linked to the corresponding trace.

## Out of Scope
- Self-hosting Langfuse (using Cloud).
- Monitoring non-AI metrics (e.g., database performance).
