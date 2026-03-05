# Technology Stack - Notion-Soul-Agent (SOTA)

## Core Languages & Architecture: Python + Swift
- **Python 3.11+ (Logic & AI):** The primary language for the agent's reasoning, Notion integration, and data processing.
- **Swift / SwiftUI (UI & macOS Integration):** Used to build a high-performance, native macOS experience, including the Menu Bar app and system-level integrations (App Intents, Push Notifications).
- **Architecture:** A hybrid model where a Python-based core handles the "brain" (Gemini 3.1, Notion sync) and a Swift-based wrapper manages the "body" (UI, macOS system services).

## AI & Agent Orchestration: LangGraph & Gemini
- **LangGraph / PydanticAI:** Used to orchestrate the stateful, multi-step "Clarification Loop" and "Proactive Scheduling" workflows.
- **google-generativeai SDK:** Direct integration with **Gemini 3.1 Flash-Lite** for multimodal task extraction and reasoning.
- **Langfuse:** Integrated for observability, tracing, and prompt management, ensuring a high-quality "Clarification Loop."

## UI & System Integration: Webview & macOS Services
- **Webview / Custom UI:** A lightweight, Notion-inspired interface that can be embedded or opened within a floating panel to maintain a consistent workspace feel.
- **macOS System Services:**
    - **`SMAppService` / `LaunchAgent`:** For background persistence.
    - **`UserNotifications` Framework:** For proactive, interactive push notifications.
    - **Accessibility API (`AXUIElement`):** To intelligently perceive the user's current onscreen context (e.g., in Notion).
- **Notion SDK:** For deep, bidirectional synchronization with the `Tasks [UT]` database.

## Data Persistence & Memory: SQLite & SwiftData
- **SQLite + SwiftData:** The primary local-first storage for task history, user preferences, and "User Soul" (habits/patterns).
- **JSON / YAML:** For human-readable configuration, environment settings, and lightweight state management.
- **Privacy-First:** All sensitive user data and cognitive load metrics are stored locally to ensure maximum privacy and offline availability.
