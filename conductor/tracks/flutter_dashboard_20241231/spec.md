# Specification: Build Flutter Liquid Glass Dashboard (Track 6)

## Overview
This track focuses on the implementation of the primary user interface for the Notion-Soul-Agent (NSA). Using Flutter, we will build a high-performance macOS desktop application that embodies a "Notion-Minimalist" aesthetic while providing deep, data-driven insights into task scheduling and cognitive well-being.

## Functional Requirements
- **Notion-Minimalist Aesthetic:** Clean, high-whitespace design with subtle "Liquid Glass" (transparency/blur) accents for a modern macOS feel.
- **Interleaved Calendar View:**
    - A specialized timeline visualizing task sequences.
    - Explicitly displays AI-predicted "Slack Time" (redundancy zones) between tasks.
- **Recursive Kanban Board:**
    - A task board that supports the ADaPT hierarchical structure.
    - Allows expanding/collapsing parent tasks to view atomized sub-tasks.
- **Integrated Chat/Command Center:**
    - A central interaction zone for the "Universal Soul Console."
    - Real-time display of AI reasoning (Thought visualization).
- **Cognitive Metrics Dashboard:**
    - Visualization of predicted energy peaks (UMP) and real-time cognitive load (CLT) indicators.
- **macOS System Integration:**
    - **Menu Bar (Tray) Support:** A permanent icon for quick-glance status and task switching.
    - **Native Notifications:** Actionable macOS alerts for "Nudges" and "Status Inquiries."
    - **macOS System Widgets:** (Optional/Initial Support) Quick task indicators for the Notification Center.

## Technical Requirements
- **Framework:** Flutter (Desktop/macOS).
- **State Management:** Provider or Riverpod for handling asynchronous API data from the Python Logic Hub.
- **Styling:** Custom "Liquid Glass" theme with `BackdropFilter` and minimalist typography.
- **Communication:** HTTP and WebSockets for real-time interaction with the FastAPI backend.
- **macOS Specifics:** Use `system_tray` and `local_notifications` plugins.

## Acceptance Criteria
- The app launches as a native macOS application with a functional Menu Bar icon.
- User can view a scientifically interleaved schedule fetched from the backend.
- Complex tasks can be expanded into their atomic sub-tasks within the Kanban view.
- Cognitive load metrics are displayed as a visually appealing graph or chart.
- The app responds instantly to chat inputs, displaying the AI's "Thought" process as it happens.

## Out of Scope
- Full iPhone/Mobile implementation (Desktop-only for this track).
- Final Notion bidirectional sync (handled by Track 7).
