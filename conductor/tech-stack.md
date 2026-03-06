# Technology Stack - Notion-Soul-Agent (SOTA - Decoupled Edition)

## 1. 核心语言与混合架构 (Core Languages & Architecture)
- **Python 3.11+ (Logic & AI Hub):** 
    - 负责核心推理、Notion 同步引擎、CLT 负荷计算及生物排程算法。
    - **API 驱动：** 使用 **FastAPI** 暴露本地接口，支持异步 Websocket 实时通信。
- **Flutter (Cross-Platform UI):** 
    - 构建 macOS 桌面端（MenuBar 应用）及 iOS/Android 移动端应用。
    - **视觉标准：** 采用 **Liquid Glass (BackdropFilter)** 风格，实现高质感 UI。
- **Bridge:** Flutter 前端通过 HTTP/Websocket 与 Python 后端通信。

## 2. AI 推理与 Agent 编排 (AI & Agent Orchestration)
- **Gemini 3.1 Flash-Lite:** 
    - 核心多模态 VLM，处理 1M 上下文。
- **LangGraph / PydanticAI:** 
    - 驱动任务拆解、周规划重排的状态机。
- **Langfuse:** 监控 Prompt 与推理路径。

## 3. 系统集成与感知 (System Integration & Observer)
- **macOS integration:** 
    - 使用 **System Tray (MenuBar)** 插件实现 Flutter 菜单栏常驻。
    - 使用 **Local Notifications** 实现带按钮的主动推送。
- **Notion SDK:** 用于本地数据与云端数据库的镜像同步。

## 4. 数据存储与存储系统 (Persistence & Memory)
- **Primary Source (Local SQLite):** 
    - 存储任务树、User Soul 模型、执行日志。
- **Soul Context (Markdown):** 
    - 动态维护的 \`user_soul.md\`，作为 AI 的情景记忆。

## 5. 性能与隐私工程 (Engineering Standards)
- **Headless Logic:** 后端只负责逻辑，不耦合任何 UI 库。
- **Local-First:** 核心数据不离设备，确保隐私安全。
