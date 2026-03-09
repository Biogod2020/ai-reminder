# Specification: Architecture Visualization & Documentation (Track: architecture_viz_20260309)

## Overview
This track aims to create a SOTA-level, interactive HTML document that visualizes the current architecture and workflow of the Notion-Soul-Agent project. The focus will be heavily on the Backend & AI Core, including the LangGraph orchestrator, the Dual-Axis memory system, and the AI routing logic. The document will feature an interactive Mermaid diagram linked to detailed, easy-to-read UI cards documenting each node's specifications.

## Goals
- **SOTA Visualization:** Generate a highly detailed, styled Mermaid flowchart representing the Backend & AI Core architecture.
- **Interactive Experience:** Embed the diagram in an HTML file where clicking a node dynamically highlights or scrolls to its detailed documentation.
- **Comprehensive Documentation:** Accompany the diagram with detailed specifications (Input, Output, Functionality) for every node, presented in modern, readable UI cards to facilitate review and future iterations.

## Functional Requirements
1. **Mermaid Diagram Generation:**
   - Map out the `SoulOrchestrator` LangGraph workflow (classify -> handle_task/memory/clarify/planner -> await_approval/notify).
   - Map out the Memory Architecture (`SharedMemoryManager`, `MemoryConsolidator`, Dual-Axis Merger, SQLite `omni_behavior_log`).
   - Map out the Perception Pipeline (`VisualSampler`, `KnowledgeDB`, `BehaviorSynthesisEngine`).
   - Use distinct styling (colors/shapes) for different types of nodes (e.g., AI Models, Databases, Logic Nodes).
2. **HTML Generation:**
   - Create a standalone `docs/architecture.html` file.
   - Use a modern CSS framework (e.g., Tailwind via CDN) or custom styling for a polished look.
   - Integrate `mermaid.js` to render the diagram.
3. **Interactivity Logic:**
   - Implement JavaScript to listen for click events on the rendered Mermaid SVG nodes.
   - Clicking a node should smoothly scroll the viewport to the corresponding Node Detail Card and visually highlight it.
4. **Node Detail Cards (The "SOTA" Format):**
   - For each identified node, create a visual card containing:
     - **Node Name & Icon**
     - **Functionality:** A concise, clear description of what the node does.
     - **Input:** Expected data structures or triggers (e.g., `AgentState`, `15s Image Batch`, `User Feedback`).
     - **Output:** The resulting data or state changes (e.g., `Updated AgentState`, `Merged Timeline JSON`).
   - Use visual badges for Input/Output types to make reading and reviewing extremely easy.

## Non-Functional Requirements
- **Maintainability:** The HTML/JS/CSS should be clean and structured so it can be easily updated as the architecture evolves.
- **Self-Contained:** The HTML file should rely on CDNs for libraries (Mermaid, Tailwind/CSS) so it doesn't require a build step to view.

## Acceptance Criteria
- [ ] A file named `docs/architecture.html` is successfully created.
- [ ] Opening the file reveals a detailed Mermaid diagram of the Backend & AI Core.
- [ ] Clicking on nodes in the diagram successfully navigates to the corresponding detail cards.
- [ ] All critical components (Orchestrator, Adapter, Memory Managers, Synthesis Engine) are documented with their specific inputs and outputs.
