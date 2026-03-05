# Technology Stack - Notion-Soul-Agent (SOTA - Decoupled Edition)

## 1. 核心语言与混合架构 (Core Languages & Architecture)
- **Python 3.11+ (Logic & AI Core):** 
    - 负责核心推理、Notion 同步引擎、CLT 负荷计算及生物排程算法。
    - **性能优化：** 使用 `asyncio` 与 `httpx` 处理高并发请求。
- **Swift / SwiftUI (macOS Native & UI):** 
    - 构建高性能 Menu Bar 应用及 Floating Panel。
    - 通过 **App Intents** 接入 macOS 系统服务。
- **Decoupled Link:** Python 逻辑层通过 **JSON-RPC** 或 Unix Domain Socket 与 Swift UI 层通信，实现极低延迟的本地交互。

## 2. AI 推理与 Agent 编排 (AI & Agent Orchestration)
- **Gemini 3.1 Flash-Lite:** 
    - 核心多模态 VLM，利用其 **1M Context Window** 处理长程任务轨迹。
- **LangGraph / PydanticAI:** 
    - 实现 **Clarification Loop** 的状态机控制，支持复杂的循环决策流。
- **Langfuse:** 
    - 生产级监控，记录 Prompt 迭代、推理时延及 Agent 决策路径。

## 3. 系统集成与感知 (System Integration & Observer)
- **macOS System Services:**
    - **`SMAppService` / `LaunchAgent`:** 确保后台常驻与自启动。
    - **`UserNotifications` Framework:** 实现带交互按钮的原生推送。
    - **Accessibility API (`AXUIElement`):** 实时感知当前活跃 App，作为认知负荷计算的环境特征。
- **Notion SDK:** 
    - 用于本地数据与 Notion `Tasks [UT]` 数据库的镜像映射。

## 4. 数据存储与跨端推送 (Persistence & Mobile Gateway)
- **本地主数据库 (Primary Source):**
    - **SQLite + SwiftData:** 本地优先存储，记录任务图谱、User Soul 模型、以及高频执行日志。
- **移动端推送网关 (Mobile Push):**
    - **Firebase (FCM) / Supabase Realtime:** 作为跨端消息中继，实现 iPhone 原生 APNs 推送。
- **配置管理:** 
    - 使用 **YAML / JSON** 存储模型参数、API 配置及用户自定义偏好。

## 5. 性能与隐私工程 (Engineering Standards)
- **Zero-Latency Logic:** 核心排程不依赖外网，仅同步至 Notion 时进行异步 I/O。
- **Local-Only Biometrics:** 用户的疲劳度原始指标、心率等隐私数据仅存本地 SQLite，不上传至 Notion 或云端。
