# Notion-Soul-Agent (SOTA)

An autonomous, multi-modal task scheduling assistant built with **Gemini 3.1 Flash-Lite**, integrated with Notion and macOS.

## Core Features
- **Intelligent Task Atomization:** Decomposes complex tasks into manageable atomic steps.
- **Cognitive Load Aware Scheduling:** Scientifically interleaves heavy and light tasks based on your energy levels.
- **Proactive Nudges:** Active macOS notifications to keep you on track.
- **Digital Soul Memory:** Local-first preference and habit learning.

## Interactive Architecture Engine
The project features a data-driven, interactive visualization of its internal cognitive state machine. 
- **View:** Navigate to the **Architecture** tab in the dashboard.
- **Interact:** Zoom, pan, and click on nodes to see detailed descriptions, implementation paths, and I/O schemas.
- **Backend:** Powered by a local SQLite metadata store and FastAPI.

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
