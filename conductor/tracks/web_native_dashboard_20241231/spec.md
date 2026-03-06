# Specification: Build Web-Native Liquid Dashboard (Track 6)

## Overview
使用 React + Vite + Electron 构建 NSA 的主要用户界面。该界面将具备类 Notion 的极简美学，并通过 Electron 接入 macOS 系统原生能力。

## Functional Requirements
- **Notion-Minimalist UI:** 使用 React 实现响应式的、高像素完美的极简界面。
- **Glassmorphism Design:** 通过 CSS `backdrop-filter` 实现高质感的磨砂玻璃悬浮效果。
- **Interleaved Calendar:** 可视化展示科学穿插后的任务流与冗余时间。
- **Recursive Kanban:** 支持 ADaPT 结构的递归任务看板。
- **macOS Native Integration:**
    - 菜单栏图标 (Tray)。
    - 系统级交互通知。
    - 全局快捷键呼出。

## Technical Requirements
- **Frontend:** React 18+, Vite.
- **Desktop Container:** Electron.
- **Styling:** CSS Modules 或 Tailwind CSS.
- **Bridge:** 通过 HTTP/WebSocket 与 FastAPI 后端通信。
