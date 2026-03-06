# Implementation Plan: Build Web-Native Liquid Dashboard (Track 6)

## Phase 1: Web-Native Scaffolding [checkpoint: 1766be1]
- [x] Task: Initialize React + Vite Project 485da9d
    - [x] Run `npm create vite@latest frontend -- --template react-ts`.
    - [x] Configure Tailwind CSS for Notion-Minimalist styling.
- [x] Task: Integrate Electron Wrapper b06e5fd
    - [x] Setup basic Electron main process with Tray support.
    - [x] Enable transparency and backdrop-blur settings.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Web-Native Scaffolding' (Protocol in workflow.md) 1766be1

## Phase 2: Core Views & Real-time Bridge
- [ ] Task: Implement Interleaved Calendar Widget
    - [ ] Fetch and render tasks from `/get_view_data`.
    - [ ] Visually differentiate 'Task' and 'Slack' blocks.
- [ ] Task: Implement Chat & Thought Stream
    - [ ] Connect to `/chat` and visualize the AI reasoning step-by-step.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Core Views & Real-time Bridge' (Protocol in workflow.md)
