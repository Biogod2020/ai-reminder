# Technology Stack - Notion-Soul-Agent (SOTA - AI-Native Edition)

## 1. 核心语言与混合架构 (Core Languages & Architecture)
- **Python 3.11+ (Logic & AI Core):** 
    - 负责核心推理逻辑、Notion 数据流、以及**动态记忆文档 (Soul Context)** 的维护。
    - **性能优化：** 使用 `asyncio` 与 `httpx` 处理高频 AI 请求与数据同步。
- **Swift / SwiftUI (macOS Native & UI):** 
    - 构建高性能 Menu Bar 应用及 Floating Panel。
    - 负责接收 Python 核心发出的“原子任务”指令并展示交互式通知。
- **IPC Link:** Python 逻辑层通过 **JSON-RPC** 与 Swift UI 层通信，实现极低延迟的本地交互。

## 2. AI 推理与 Agent 编排 (AI & Agent Orchestration)
- **Gemini 3.1 Flash-Lite:** 
    - 核心推理大脑。利用 **1M Context Window** 吞噬完整的 `user_soul.md` 记忆文档和任务历史。
- **Context-First Prompting:** 
    - 使用 **思维链 (CoT)** 与 **Few-Shot** 提示词实现“智慧拆解”与“穿插排程”，取代本地复杂算法。
- **LangGraph / PydanticAI:** 
    - 实现 **Clarification Loop** 与 **Task Decomposing** 的状态机控制。
- **Langfuse:** 
    - 记录 AI 推理路径、Prompt 耗时，确保长上下文推理的稳定性。

## 3. 存储与记忆系统 (Persistence & Memory)
- **Soul Context (Primary Memory):** 
    - 基于 **Markdown/JSON** 的本地记忆文档 (`user_soul.md`)。存储交互日志、习惯偏好、效率波动。
- **Local SQLite (Structured Storage):** 
    - 存储原子化的任务树 (ADaPT Tree) 和元数据映射。
- **Notion Mirror:** 
    - 通过 Notion SDK 实现本地数据与云端数据库的异步镜像映射。

## 4. 移动端与系统集成 (Ecosystem Integration)
- **Mobile Push Gateway:**
    - 使用 **Pushover / Bark API** (MVP 阶段) 实现极简的 iPhone 推送。
    - 未来规划：自建 Firebase/Supabase 原生网关。
- **System Integration:**
    - **App Intents:** (未来规划) 接入系统快捷指令。
    - **Accessibility API:** (插件化) 感知用户工作场景。

## 5. 开发规范与性能工程 (Engineering Standards)
- **Prompt-First Design:** 优先通过优化提示词和上下文来解决问题，而非增加本地代码复杂度。
- **Decoupled Plugins:** 所有的计算逻辑（如精准 CLT 数值计算）均设计为可插拔模块，不干扰核心 AI 推理流。
- **Local-First Privacy:** 用户的原始交互细节仅保留在本地 `user_soul.md` 中。
