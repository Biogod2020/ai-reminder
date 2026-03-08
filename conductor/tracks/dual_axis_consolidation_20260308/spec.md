# Specification: Dual-Axis Consolidation Integration & Simulation (Track: dual_axis_consolidation_20260308)

## Overview
This track focuses on ensuring the `MemoryConsolidator` fully utilizes the newly created Dual-Axis timeline data (`omni_behavior_log`). It also involves designing and implementing a comprehensive, realistic 24-hour simulation test to verify the memory consolidation and hierarchical compression logic across various edge cases and complex transitions.

## Goals
- Audit and update `core/consolidator.py` to ensure it ingests the full `merged_timeline` from the Dual-Axis architecture.
- Build a robust 24-hour simulation script (`scripts/simulate_24h_behavior.py`).
- Verify that the hierarchical consolidation (Daily -> 3-Day -> Weekly) accurately summarizes complex behavioral patterns, handles gaps, and extracts high-signal insights.

## Functional Requirements
1. **Consolidator Integration:**
   - Update `MemoryConsolidator.consolidate_layer` (specifically for the 'daily_summary' tier) to fetch data from `omni_behavior_log` instead of just raw `user_soul` session facts.
   - Refine the LLM prompt to explicitly process structured JSON timelines (duration, app, category, focus_score, intent).
2. **Realistic 24h Simulation Script:**
   - **Data Generation:** Programmatically generate mock `omni_behavior_log` entries representing a full 24-hour day.
   - **Complex Transitions:** Include transitions from Deep Work -> Leisure -> Deep Work.
   - **Missing Data:** Simulate periods of 'UNCATEGORIZED' blocks to test the AI's interpolation and summary capabilities.
3. **Hierarchical Testing Execution:**
   - The script must sequentially trigger the Daily, 3-Day, and Weekly consolidations using the seeded data.
   - Print the generated summaries to the console for manual review and qualitative assessment.

## Non-Functional Requirements
- **Test Isolation:** The simulation script should use a separate test database (e.g., `.sim_mem_db.sqlite`) to avoid polluting the actual user memory during testing.
- **Reproducibility:** The simulated data should be deterministic enough to consistently test the prompt's parsing logic.

## Acceptance Criteria
- [ ] `core/consolidator.py` successfully reads and parses `omni_behavior_log`.
- [ ] A 24-hour simulation script is created and runs successfully.
- [ ] The generated Daily Summary accurately reflects the complex transitions and handles gaps in the simulated data.
- [ ] The output is printed clearly to the console for manual review, demonstrating the extraction of behavioral habits.

## Out of Scope
- Changes to the actual `KnowledgeDB` extraction logic or the `BehaviorSynthesisEngine` visual sampling.
