# Initial Concept

本项目旨在利用 **Gemini 3.1 Flash-Lite** 的多模态能力与高推理性能，构建一个深度集成于 macOS 的 **Notion-Soul-Agent (SOTA)**。

核心目标包括：
1. **Notion 解耦集成**：核心业务逻辑与 Notion 剥离，将 Notion 定位为数据“镜像”与可视化窗口。通过异步同步引擎，实现 `Tasks [UT]` 数据库的稳健映射。
2. **多模态主动推送**：通过 macOS 及 Mobile 原生通知系统，根据用户的认知负荷 (CLT) 与昼夜节律 (Circadian Rhythm) 主动推送任务排程建议。
3. **模糊输入澄清 (Clarification Loop)**：支持粘贴不规范的文本或截图，通过本地 AI 自动澄清意图并更新本地数据库与 Notion。
4. **用户习惯学习**：通过 RLHF (P-DPO) 学习用户偏好、工作习惯与效率波峰，实现“类人”的自动化规划。
5. **系统级集成**：利用 macOS App Intents 与后台常驻服务 (`SMAppService`) 实现无感、无缝的操作体验，支持跨平台（macOS + Mobile）的主动推送交互。

# Product Guide - Notion-Soul-Agent (SOTA - Decoupled Edition)

## 1. 项目愿景 (Overview)
Notion-Soul-Agent (NSA) 是一个**本地优先 (Local-First)**、具备“生物自适应”能力的任务 Agent。它不仅仅是一个 Notion 插件，而是一个独立的“数字灵魂”。通过将核心推理逻辑与云端 API 剥离，NSA 能够实现**零延迟的本地决策**，同时利用 **Gemini 3.1 Flash-Lite** 的多模态能力感知用户状态，为研究者、科研人员及繁忙的专业人士提供全方位的任务排程方案。

## 2. 核心架构：Decoupled Soul (解耦之魂)
为了实现极端灵活性与性能，本项目采用 **“本地大脑 + 跨端镜像”** 架构：
- **本地大脑 (The Private Brain):** 
    - 存储完整的任务图谱、用户习惯模型 (User Soul) 及详细执行日志。
    - 运行核心推理引擎 (Gemini 3.1)、CLT 负荷计算及 UMP 排程算法。
    - **性能优势：** 摆脱网络延迟与 Notion API 频率限制，实现毫秒级任务重排。
- **Notion 镜像 (The Mirror Dashboard):** 
    - 维持与原 `Tasks [UT]` 架构的兼容性。
    - 作为数据的可视化展示、长期存档与非 macOS 设备查看窗口。
    - 通过异步同步器实现数据对齐，作为用户数字资产的备份。
- **移动端网关 (Mobile Push Gateway):** 
    - 接入 APNs 原生推送，实现手机端的即时提醒与 [Approve/Refuse] 反馈。

## 3. 核心功能与 SOTA 机制 (Key Features)
- **多模态澄清闭环 (Clarification Loop):** 
    - 引入 **InfantAgent-Next (2025)** 的模块化设计。支持用户直接粘贴乱序文本、会议白板截图。
    - **置信度检测：** 当 AI 意图识别置信度 < 0.8 时，触发 **MCQ (Minimal Clarification Question)** 询问，确保数据在本地及同步到 Notion 时的准确性。
- **生物节律与认知负荷排程 (Bio-Cognitive Scheduling):**
    - **理论支撑：** 结合 **Borbély 的二过程模型** (Process C & S) 与 **ChronoCal** 算法。
    - **性能监测：** 实时监控 **CLTs (Cognitive Load Traces)**，即内在负荷 (IL) 与外在负荷 (EL) 指标。
    - **排程策略：** 自动将高难度科研任务 (Intrinsic Load) 排在 UMP 预测的能量巅峰（Peak Alertness），实现“顺应天时”的产出。
- **主动性与习惯学习 (Habit Learning):**
    - **算法标准：** 采用 **P-DPO** (Personalized Direct Preference Optimization) 与 **Contextual Bandits**。
    - **进化路径：** 自动记录并学习用户对排程建议的反馈。若用户连续拒绝下午 2 点的深度任务，Agent 将自动调整该时段的“User Soul”偏好权重。

## 4. 用户界面与系统集成 (UI/UX)
- **macOS Native:** 采用 **Liquid Glass (Tahoe)** 设计风格。
    - **Menu Bar App:** 提供实时的“心跳”指示与快速任务入口。
    - **Floating Panel:** 轻量化 Webview 与 SwiftUI 混合界面，展示复杂的认知负荷曲线与排程视图。
- **Active Notification:** 交互式通知支持。用户无需打开应用，直接在通知 Banner 点击“已完成”或“推迟”即可同步更新本地与 Notion 状态。
- **System Observer:** 通过 **Accessibility API (`AXUIElement`)** 感知用户当前运行的应用及工作场景，智能抑制不合时宜的通知。

## 5. 核心价值：无感自动化 (Seamless Automation)
NSA 的最终目标是成为一个“设定即遗忘”的协调层。它在后台默默处理任务规划、信息提取与多端同步，让用户在享受 Notion 强大组织能力的同时，拥有一个响应极速、深度懂你的本地智能核心。
