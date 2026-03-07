# Technology Stack - Notion-Soul-Agent (SOTA - Decoupled Edition)

## 1. 核心语言与混合架构 (Core Languages & Architecture)
- **Python 3.11+ (Logic & AI Hub):** 
    - 负责核心推理、Notion 同步引擎、CLT 负荷计算及生物排程算法。
    - **API 驱动：** 使用 **FastAPI** 暴露本地接口，支持异步 Websocket 实时通信。
- **React + Vite (Frontend Core):** 
    - 构建响应式、高像素完美的“类 Notion”界面。
    - **Vite:** 确保极速的热重载与构建性能。
    - **Libraries:** \`recharts\` (数据可视化), \`framer-motion\` (动画), \`lucide-react\` (图标)。
- **Electron (Mac Container):** 
    - 为 macOS 提供原生外壳，支持菜单栏 (Tray)、系统通知及磨砂玻璃效果。
- **Capacitor (Mobile Bridge):** 
    - 负责将 Web 项目打包为 iOS/Android 原生 App，调用系统级推送与传感器。

## 2. AI 推理与 Agent 编排 (AI & Agent Orchestration)
- **Gemini 3.1 Flash-Lite:** 
    - 核心多模态 VLM，处理 1M 上下文。
- **LangGraph / PydanticAI:** 
    - 驱动任务拆解、周规划重排的状态机。
- **Langfuse:** 监控 Prompt 与推理路径。

## 3. 系统集成与感知 (System Integration & Observer)
- **macOS integration (via Electron API):** 
    - 自定义菜单栏图标与悬浮窗逻辑。
    - 使用原生 macOS 通信层实现交互式通知。
- **Notion SDK:** 用于本地数据与云端数据库的镜像同步。

## 4. 数据存储与存储系统 (Persistence & Memory)
- **Primary Source (Local SQLite):** 
    - 存储任务树、User Soul 模型、执行日志。
- **Soul Context (Markdown):** 
    - 动态维护的 `user_soul.md`，作为 AI 的情景记忆。

## 5. 性能与隐私工程 (Engineering Standards)
- **Zero-SDK Weight:** 相比于 Flutter，React + Electron 方案不需要安装庞大的 SDK，安装与分发更轻量。
- **Local-First:** 核心数据不离设备，确保隐私安全。
