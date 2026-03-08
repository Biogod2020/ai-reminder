# Implementation Plan: Dual-Axis Consolidation Integration & Simulation (Track: dual_axis_consolidation_20260308)

## Phase 1: Consolidator Integration
- [ ] Task: Update `MemoryConsolidator` to read from `omni_behavior_log`.
    - [ ] Modify SQL queries in `consolidate_layer` (specifically for generating `daily_summary`) to fetch and parse `layers_json` from the `omni_behavior_log` table.
    - [ ] Update the LLM prompt to explicitly process the structured timeline JSON, ensuring it understands attributes like `focus_score` and `inferred_category`.
- [ ] Task: Conductor - User Manual Verification 'Consolidator Integration' (Protocol in workflow.md)

## Phase 2: Simulation Script Development
- [ ] Task: Create `scripts/simulate_24h_behavior.py`.
    - [ ] Write logic to generate 24 hours of mock `merged_timeline` data representing a realistic day.
    - [ ] Ensure mock data includes specific edge cases: Deep Work blocks, rapid Context Switching, and 'UNCATEGORIZED' gaps.
    - [ ] Add logic to seed this mock data into a test SQLite database to avoid polluting the actual user database.
- [ ] Task: Conductor - User Manual Verification 'Simulation Script Development' (Protocol in workflow.md)

## Phase 3: Testing and Verification
- [ ] Task: Execute the simulation script and verify hierarchical output.
    - [ ] Execute logic to trigger the Daily consolidation using the simulated 24h data.
    - [ ] Execute logic to trigger 3-Day and Weekly consolidations sequentially using the generated daily summaries.
    - [ ] Print all generated summaries clearly to the console for manual review.
- [ ] Task: Conductor - User Manual Verification 'Testing and Verification' (Protocol in workflow.md)
