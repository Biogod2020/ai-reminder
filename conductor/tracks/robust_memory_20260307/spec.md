# Specification: Multimodal Truth Engine (Track: knowledge_c_integration_20260307)

## Overview
This track implements a high-fidelity behavioral "Truth Engine" by merging macOS `knowledgeC.db` duration data with high-frequency visual streams (15s screenshots). Every 30 minutes, these data sources are synthesized by Gemini 3.1 Flash-Lite to reconstruct an objective, context-aware timeline of user activity.

## Goals
- **High-Frequency Perception:** Capture full-screen snapshots every 15 seconds to eliminate "semantic blind spots."
- **Multimodal Synthesis:** Merge exact app durations from `knowledgeC.db` with the visual context of the screen.
- **SOTA Behavioral Categorization:** Classify time slices into `Work`, `Leisure`, `Utility`, or `Away` with scientific reasoning.
- **Selective Memory:** Allow for the retention of "Key Moments" (screenshots) while managing automated cleanup for the rest.

## Functional Requirements
1. **High-Frequency Sampler:**
   - Capture 1 screenshot every 15s (configurable).
   - No automatic filtering (full transparency as requested).
   - Store locally in a temporary `captures/` directory.
2. **Grand Synthesis (30-min Window):**
   - Every 30 minutes, bundle ~120 images + the corresponding `knowledgeC.db` timeline.
   - **SOTA Prompting:** Instruct Gemini to act as a "High-Performance Execution Coach."
   - **Output Format:** A structured timeline merging App Names + Visual Actions + Category + Cognitive Load Score.
3. **Selective Retention & Cleanup:**
   - AI identifies "Key Snapshots" (e.g., a complex architecture diagram or a significant milestone).
   - These key images are moved to a `soul_gallery/` for user review.
   - All other raw images in `captures/` are queued for deletion after summarization (User-optional/Selective).
4. **Context Injection:**
   - Final summarized timelines are injected into the agent nodes' context.

## Non-Functional Requirements
- **Performance:** Image processing (scaling/grayscaling) to keep payload sizes manageable for the API.
- **Robustness:** Handle "Database Locked" errors via temporary SQLite copies.
- **AI Model:** Exclusively use Gemini 3.1+ for its 1M context and multimodal excellence.

## Acceptance Criteria
- [ ] 15s sampler runs stably in the background.
- [ ] 30-min batch successfully generates a merged timeline summary.
- [ ] UI/Prompt allows user to selectively destroy or keep screenshots.
- [ ] Daily summary includes "Deep Flow" and "Context Switch" analysis.
