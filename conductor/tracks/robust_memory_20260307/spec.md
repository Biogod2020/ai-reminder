# Specification: Robust Memory & Initialization Q&A (Track: robust_memory_20260307)

## Overview
This track implements a robust, SOTA memory system for the Notion-Soul-Agent using a custom SQLite-based management system. It introduces an interactive "Initialization" Q&A session to capture user preferences and habits, ensures all agent nodes have shared global memory access, and implements a multi-tier "Time-Pyramid" memory consolidation system to synthesize raw behavioral data into long-term habits.

## Goals
- Implement a hierarchical memory structure: **Short-term** (current task/context) and **Long-term** (habits, goals, persistent user "Soul").
- Develop an "Initialization" Q&A module to bootstrap the user's "Soul" profile.
- Integrate macOS system metrics (Daily/Weekly/Monthly) to trigger automatic memory updates.
- **Memory Consolidation:** Implement a tiered compression mechanism (Daily -> 3-Day -> Weekly -> Monthly -> Yearly) to refine raw behavioral data into high-signal insights.
- Ensure all agent nodes (Atomizer, Nudger, etc.) have access to a **Shared Global Memory**.
- Stress test the memory engine for performance, concurrency, and temporal accuracy.

## Functional Requirements
1. **Initialization Q&A:**
   - Interactive CLI/Web session to capture circadian rhythm, work preferences, and goals.
   - Initial population of `user_soul.md` and the SQLite database.
2. **Hierarchical Memory Management:**
   - **Short-term Memory:** Session-based, task-specific context (e.g., active App monitoring).
   - **Long-term Memory:** Persistent storage of user habits, preferences, and long-term goals.
3. **Automatic Update Engine & Consolidation:**
   - Monitor macOS system events for active app tracking.
   - **Daily Maintenance (6 AM):** Summarize past 24h raw data into a "Daily Insight".
   - **Multi-tier Compression:** 
     - 3-Day summary (every 3 days).
     - Weekly summary (every Monday).
     - Monthly summary (1st of the month).
     - Quarterly/Yearly summaries for deep long-term drift detection.
   - All summaries must be backed up in `user_soul.md` while keeping the "Active Soul" model lean.
4. **Shared Global Access:**
   - Unified API for all agent nodes to query and store memories.
   - Contextual injection into all AI generations (top relevant facts).
5. **Stress Test Suite:**
   - Volume and concurrency verification for the SQLite engine.

## Non-Functional Requirements
- **Robustness:** 100% success rate for local proxy calls via deep monkeypatching/httpx fallback.
- **Performance:** Memory retrieval latency < 50ms.
- **Privacy:** Local-First storage.

## Acceptance Criteria
- [x] Initialization Q&A successfully populates the `user_soul.md` and database.
- [x] All agent nodes retrieve relevant user context for generations.
- [ ] Memory consolidator successfully runs at 6 AM and generates hierarchical summaries.
- [ ] Active memory remains lean by deactivating older raw data while preserving summaries.
- [x] Stress tests pass with sub-millisecond local DB latency.

## Out of Scope
- Cloud-based memory synchronization.
