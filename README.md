# Notion-Soul-Agent (SOTA)

An autonomous, multi-modal task scheduling assistant built with **Gemini 3.1 Flash-Lite**, integrated with Notion and macOS.

## Core Features
- **Intelligent Task Atomization:** Decomposes complex tasks into manageable atomic steps.
- **Cognitive Load Aware Scheduling:** Scientifically interleaves heavy and light tasks based on your energy levels.
- **Proactive Nudges:** Active macOS notifications to keep you on track.
- **Digital Soul Memory:** Local-first preference and habit learning.

## Standalone Architecture Engine
The project features a dedicated, data-driven visualization tool for its internal cognitive state machine.

- **Viewer:** Open `docs/interactive_viz.html` directly in your browser.
- **Sync:** To update the visualization after adding new nodes to the code, run:
  ```bash
  PYTHONPATH=. ./.venv/bin/python3 scripts/sync_viz_metadata.py
  ```
- **Backend:** Ensure the FastAPI server is running (`python core/api.py`) to fetch detailed node metadata.

## Tech Stack
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, LangGraph.
- **AI:** Gemini 3.1 Flash-Lite (via Gemini API).
- **Frontend:** React + Vite, @xyflow/react, TailwindCSS, Framer Motion.
- **Integration:** Notion SDK, macOS App Intents.

## Development
```bash
# Backend
pip install -r requirements.txt
python main.py

# Frontend
cd frontend
npm install
npm run dev
```
