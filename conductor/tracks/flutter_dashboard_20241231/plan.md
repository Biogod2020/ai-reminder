# Implementation Plan: Build Flutter Liquid Glass Dashboard (Track 6)

## Phase 1: Flutter Scaffolding & Theme
- [ ] Task: Initialize Flutter Project & Essential Packages
    - [ ] Create `frontend_flutter` project.
    - [ ] Add dependencies: `http`, `provider`, `system_tray`, `flutter_local_notifications`.
- [ ] Task: Implement 'Liquid Glass' Theme & Layout
    - [ ] Define the Notion-Minimalist color palette and typography.
    - [ ] Create a reusable `GlassContainer` using `BackdropFilter`.
    - [ ] Scaffold the main layout with a sidebar and content area.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Flutter Scaffolding & Theme' (Protocol in workflow.md)

## Phase 2: Core Views & Data Binding
- [ ] Task: Implement Chat/Command Center Widget
    - [ ] Connect to FastAPI `/chat` endpoint.
    - [ ] Implement Thought visualization stream (Thought blocks).
- [ ] Task: Implement Interleaved Calendar View
    - [ ] Fetch data from `/get_view_data`.
    - [ ] Build a vertical timeline showing tasks and their AI-predicted slack buffers.
- [ ] Task: Implement Recursive Kanban Board
    - [ ] Build a task board that supports nested/recursive task expansion.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Core Views & Data Binding' (Protocol in workflow.md)

## Phase 3: System Integration & Polish
- [ ] Task: Implement macOS Menu Bar & System Tray
    - [ ] Permanent icon with a 'Quick Task' summary menu.
- [ ] Task: Integrate Cognitive Metrics Visualization
    - [ ] Add charts for CLT/UMP energy peaks (using `fl_chart` or similar).
- [ ] Task: Final Polish & Interaction refinement
    - [ ] Ensure smooth transitions and hover effects.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: System Integration & Polish' (Protocol in workflow.md)
