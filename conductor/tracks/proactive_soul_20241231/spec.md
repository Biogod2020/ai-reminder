# Specification: Proactive Wisdom & Dynamic Buffer (Proactive Soul)

## Overview
This track transforms the Notion-Soul-Agent (NSA) from a reactive task manager into a proactive "Executive Function Assistant." It implements the logic for the agent to initiate contact, manage unexpected delays empathy-first, and ensure scientific system redundancy (Slack Time) in all schedules.

## Functional Requirements
- **Dynamic Slack Engine:** 
    - Gemini 3.1 must predict a specific `slack_minutes` buffer for every atomic task during decomposition.
    - Buffers must be larger for high-cognitive load tasks or domain context-switching.
- **Adaptive Heartbeat Loop:**
    - A logic hub that determines when the agent should "wake up" to check progress.
    - Frequency is determined by the AI based on current task load and duration.
- **Proactive Nudger:**
    - Active inquiry via macOS/Mobile notifications: "Is the current task done?"
    - Every nudge must include a "Scientific Reason" (e.g., UMP alertness peak or CLT warning).
- **Graceful Delay & Re-plan:**
    - If a user reports a delay (due to fatigue or interruption) or if `slack_minutes` are exceeded, the agent must propose a new scientifically valid schedule.
    - Empathy-first: Validate user fatigue and propose lower-load tasks if necessary.
- **Conflict-Driven Adaptation:** 
    - Automatically propose a re-plan if a new urgent task arrives or an existing task overruns its buffer significantly.

## Technical Requirements
- **Frameworks:** Python, FastAPI, LangGraph.
- **Skills:**
    - Update `task-atomizer` to include Slack estimation logic.
    - Implement `proactive-nudger` skill for support-driven inquiries.
- **API Endpoints:**
    - `POST /heartbeat`: Evaluates the current state and decides if a nudge is needed.
    - `POST /handle_response`: Processes user feedback from a nudge (e.g., "I'm tired") and triggers re-planning.

## Acceptance Criteria
- Tasks generated in the dashboard now include explicit "Buffer" zones.
- The agent initiates a notification when a task is nearing its AI-predicted end.
- Notifications include empathetic, data-backed reasoning (CLT/UMP).
- Users can request a delay, and the backend returns a new, scientifically interleaved task sequence.

## Out of Scope
- Direct integration with biometric hardware (reserved for Phase 6).
- Flutter UI implementation for the "Slack" visuals.
