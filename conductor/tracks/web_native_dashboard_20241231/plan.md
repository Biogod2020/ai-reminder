# Implementation Plan: Build Web-Native Liquid Dashboard (Track 6)

## Phase 1: Web-Native Scaffolding [checkpoint: 1766be1]
- [x] Task: Initialize React + Vite Project 485da9d
    - [x] Run `npm create vite@latest frontend -- --template react-ts`.
    - [x] Configure Tailwind CSS for Notion-Minimalist styling.
- [x] Task: Integrate Electron Wrapper b06e5fd
    - [x] Setup basic Electron main process with Tray support.
    - [x] Enable transparency and backdrop-blur settings.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Web-Native Scaffolding' (Protocol in workflow.md) 1766be1

## Phase 2: Core Views & Real-time Bridge [checkpoint: 42d1121]
- [x] Task: Implement Interleaved Calendar Widget 4f02219
    - [x] Fetch and render tasks from `/get_view_data`.
    - [x] Visually differentiate 'Task' and 'Slack' blocks.
- [x] Task: Implement Chat & Thought Stream e57d76e
    - [x] Connect to `/chat` and visualize the AI reasoning step-by-step.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Core Views & Real-time Bridge' (Protocol in workflow.md) 42d1121

## Phase 3: System Integration & Polish
- [x] Task: Implement macOS Menu Bar - [~] Task: Implement macOS Menu Bar & System Tray System Tray 492ae8a
    - [x] Permanent icon with a 'Quick Task' summary menu.
- [ ] Task: Integrate Cognitive Metrics Visualization
    - [ ] Add charts for CLT/UMP energy peaks (using `fl_chart` or similar).
- [ ] Task: Final Polish & Interaction refinement
    - [ ] Ensure smooth transitions and hover effects.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: System Integration & Polish' (Protocol in workflow.md)
