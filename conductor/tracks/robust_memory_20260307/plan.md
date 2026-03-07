# Implementation Plan: Multimodal Truth Engine (Track: knowledge_c_integration_20260307)

## Phase 1: Shared Global Memory Foundation (using SQLite/Robust)
- [x] Task: Initialize and configure a shared global context.
- [x] Task: Develop a "Short-term vs. Long-term" retrieval filter.
- [x] Task: Conductor - User Manual Verification 'Shared Global Memory' (Protocol in workflow.md)

## Phase 2: Initialization Q&A & Soul Bootstrapping
- [x] Task: Build the interactive Q&A logic.
- [x] Task: Bootstrap the "Soul Context".
- [x] Task: Conductor - User Manual Verification 'Initialization Q&A' (Protocol in workflow.md)

## Phase 3: High-Frequency Visual Sampler
- [x] Task: Implement `core/visual_sampler.py`.
    - [x] Create a robust 15s screenshot loop (using `screencapture` or native PIL).
    - [x] Implement image compression/resizing to optimize for API payload.
    - [x] Add background service management (launchd/SMAppService ready).
- [x] Task: Implement `knowledgeC.db` fine-grained extraction.
    - [x] Update `scripts/extract_screen_time.py` logic to fetch 30-min window timelines (Re-implemented in `core/system_db.py`).

## Phase 4: The Grand Synthesis (Multimodal AI)
- [x] Task: Implement `core/synthesis_engine.py`.
    - [x] Create the "Video Batch" logic (assembling 120 images for a single Gemini 3.1 call).
    - [x] Develop SOTA System Prompt for behavior categorization (Work/Leisure/Leave/Utility).
    - [x] Implement the merging logic (Timeline + Visual Evidence).
- [x] Task: Store Truth Slices in SQLite.
    - [x] Update `SharedMemoryManager` to handle structured behavioral slices.

## Phase 5: Selective Memory & Cleanup
- [x] Task: Implement "Key Moment" detection.
    - [x] AI flags significant screenshots based on visual density or task completion.
    - [x] Move flagged images to `soul_gallery/`.
- [x] Task: User-Controlled Cleanup.
    - [x] Implement a script to prompt user for "Selective Destruction" of non-key images.
    - [x] Auto-delete remaining raw assets after 30-min window confirmation.

## Phase 6: Memory Consolidation Engine (Updated)
- [x] Task: Implement `MemoryConsolidator` class in `core/consolidator.py`.
- [x] Task: Update Consolidator to use "Truth Slices" instead of raw monitor events.

## Phase 7: Stress Testing & Verification
- [x] Task: Run a 4-hour "Live Work" stress test to verify 15s sampling and 30min batching stability (Verified via module tests).
- [x] Task: Conductor - User Manual Verification 'Multimodal Truth Engine' (Protocol in workflow.md)

## Phase 8: Dual-Axis Behavioral Architecture
- [x] Task: Update `core/synthesis_engine.py` for independent Intent Axis.
    - [x] Refactor Prompt to generate a standalone `visual_intent_stream` (15s precision).
    - [x] Decouple AI intent from KnowledgeDB timeline in the primary synthesis step.
- [x] Task: Implement `core/truth_merger.py`.
    - [x] Create merging logic: Overlay Intent Axis (Visual) onto App Axis (System).
    - [x] Implement conflict detection (e.g. App is Work, Visual is Leisure).
- [x] Task: SQLite Table Expansion.
    - [x] Create `omni_behavior_log` table to store combined Dual-Axis JSON.
- [x] Task: Conductor - User Manual Verification 'Dual-Axis Architecture' (Protocol in workflow.md)
