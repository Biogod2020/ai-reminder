# Implementation Plan: Build Web-Native Liquid Dashboard (Track 6)

## Phase 1: Web-Native Scaffolding
- [ ] Task: Initialize React + Vite Project
    - [ ] Run `npm create vite@latest frontend -- --template react-ts`.
    - [ ] Configure Tailwind CSS for Notion-Minimalist styling.
- [ ] Task: Integrate Electron Wrapper
    - [ ] Setup basic Electron main process with Tray support.
    - [ ] Enable transparency and backdrop-blur settings.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Web-Native Scaffolding' (Protocol in workflow.md)

## Phase 2: Core Views & Real-time Bridge
- [ ] Task: Implement Interleaved Calendar Widget
    - [ ] Fetch and render tasks from `/get_view_data`.
    - [ ] Visually differentiate 'Task' and 'Slack' blocks.
- [ ] Task: Implement Chat & Thought Stream
    - [ ] Connect to `/chat` and visualize the AI reasoning step-by-step.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Core Views & Real-time Bridge' (Protocol in workflow.md)
