# Specification: Build Universal Soul Console (MVP)

## Overview
The Universal Soul Console is the primary command and control interface for the Notion-Soul-Agent (NSA). It provides a central chat-based entry point where users can interact with their "Digital Soul" using natural language to perform complex task management, memory updates, and adaptive re-planning.

## Functional Requirements
- **Unified Chat Interface (Chainlit):** A web-based local UI providing multi-modal input support and visibility into the agent's reasoning process.
- **Natural Language Intent Dispatcher:**
    - **Update Memory:** Edit and refine the `user_soul.md` via structured memory management (e.g., mem0/Letta-style extraction).
    - **Task Creation & Atomization:** Ingest new tasks and automatically apply the ADaPT protocol for recursive decomposition.
    - **Intelligent Weekly Re-plan:** Dynamically adjust the entire schedule based on life events (e.g., "I'm going on a trip this Thursday").
    - **Active Clarification:** Trigger the Clarification Loop (MCQ) when user intent is low-confidence (< 0.8).
- **Confirmation Gating:** Always display a structured "Action Preview" (e.g., a card or JSON summary) for user approval before modifying the local database or memory file.
- **SOTA Alignment:** Every re-plan or task creation must adhere to the principles of Interleaving, Cognitive Load Theory (CLT), and UMP (Unified Model of Performance).

## Technical Requirements
- **Framework:** Python + Chainlit + LangGraph.
- **Memory Integration:** Implement a `SoulMemory` class that abstracts the chosen framework (mem0 or Letta) to manage `user_soul.md`.
- **Action Dispatcher:** A LangGraph state machine that routes user messages to specific tool-calling nodes (Memory, Task, Planner).

## Acceptance Criteria
- User can successfully re-plan their week by saying "I'm busy on Thursday" and see the schedule update.
- User can add a complex task and see it broken down into atomic sub-tasks.
- Memory updates are persistent and reflected in subsequent AI reasoning steps.
- The UI displays an explicit "Approval" button before any data persistence happens.

## Out of Scope
- Direct write-back to Notion (reserved for Track 4).
- Native macOS Menu Bar/System integrations (reserved for Track 5).
- Advanced 3D/Liquid Glass UI.
