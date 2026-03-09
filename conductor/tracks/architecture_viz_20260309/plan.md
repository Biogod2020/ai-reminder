# Implementation Plan: Architecture Visualization & Documentation (Track: architecture_viz_20260309)

## Phase 1: Architecture Analysis & Mermaid Drafting
- [x] Task: Analyze current codebase to map out the Backend & AI Core. [82c6fb9]
    - [ ] Map the `SoulOrchestrator` LangGraph nodes and edges.
    - [ ] Map the Memory Architecture (`SharedMemoryManager`, `MemoryConsolidator`, `omni_behavior_log`).
    - [ ] Map the Perception Pipeline (`VisualSampler`, `KnowledgeDB`, `BehaviorSynthesisEngine`).
- [x] Task: Draft the SOTA Mermaid flowchart. [3758b73]
    - [ ] Create a comprehensive Mermaid diagram integrating the mapped components.
    - [ ] Apply distinct classes/styles to differentiate component types (e.g., Databases, Logic Nodes, AI Models).
- [~] Task: Conductor - User Manual Verification 'Phase 1: Architecture Analysis' (Protocol in workflow.md)

## Phase 2: HTML Scaffold & Styling
- [ ] Task: Set up the standalone HTML document.
    - [ ] Create `docs/architecture.html` (or `docs/index.html` within an architecture folder).
    - [ ] Integrate Mermaid.js via CDN.
    - [ ] Integrate Tailwind CSS via CDN for rapid, modern styling.
- [ ] Task: Design the layout and UI components.
    - [ ] Create a split-pane or stacked layout accommodating the large diagram and the documentation section.
    - [ ] Design the HTML structure for the "Node Detail Cards" featuring input/output badges.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: HTML Scaffold & Styling' (Protocol in workflow.md)

## Phase 3: Interactivity Implementation
- [ ] Task: Implement JavaScript for interactive node clicking.
    - [ ] Add event listeners to the rendered Mermaid SVG nodes.
    - [ ] Implement smooth scrolling to the corresponding Node Detail Card when a node is clicked.
    - [ ] Add a visual highlight effect to the selected card.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Interactivity Implementation' (Protocol in workflow.md)

## Phase 4: Documentation Population
- [ ] Task: Populate Node Detail Cards with accurate specifications.
    - [ ] Write detailed Input, Output, and Functionality descriptions for all Orchestrator nodes.
    - [ ] Write detailed specifications for Memory and Perception pipeline components.
    - [ ] Ensure formatting matches the designed UI cards (using Tailwind classes for badges/styling).
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Documentation Population' (Protocol in workflow.md)