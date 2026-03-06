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
Notion-Soul-Agent (NSA) 是一个**本地优先 (Local-First)**、具备“生物自适应”能力的任务 Agent。它不仅仅是一个 Notion 插件，而是一个独立的“数字灵魂”。通过将核心推理逻辑与云端 API 剥离，NSA 能够实现**零延迟的本地决策**，同时利用 **Gemini 3.1 Flash-Lite** 的多模态能力感知用户状态，为研究者、科研人员及繁忙的专业人士提供全方位的任务策划方案。

## 2. 核心架构：Decoupled Soul (解耦之魂)
为了实现极端灵活性与性能，本项目采用 **“AI-Native 推理中枢”** 架构：
- **本地大脑 (The Private Brain):** 
    - **Soul Context (动态记忆文档):** 核心推理引擎。本地维护 `user_soul.md`，记录用户交互、效率波动、喜好与反馈。Gemini 3.1 利用 1M 超长上下文阅读此文档，进行高度情境化的“灵魂推理”。
    - **逻辑剥离：** 放弃在本地运行复杂的 Reinforcement Learning 算法，转而通过 **提示词工程 (Prompt Engineering)** 和 **思维链 (CoT)** 让 AI 模拟专家决策。
    - **性能优势：** 实现毫秒级任务重排与即时叙事生成。
- **Notion 镜像 (The Mirror Dashboard):** 维持与原 `Tasks [UT]` 架构兼容，作为数据可视化与长期存档窗口。
- **移动端网关 (Mobile Push Gateway):** 接入原生推送，实现即时提醒与反馈。

## 3. 核心功能与 SOTA 机制 (Key Features - MVP)
- **智慧任务原子化 (Strategic Task Atomization):**
    - **专家视角拆解：** 当用户输入复杂任务时，Gemini 依据 SOTA 标准（如 **ADaPT** 协议）从专业人士视角将其拆解为低阻力的“原子任务”。
    - **诱导式完成：** 每次仅推送一个原子任务，并附带专业提示（例如：“现在的目标仅是写出 200 字的大纲”），降低启动门槛。
- **穿插式智能排程 (Strategic Interleaving):**
    - **多任务穿插：** 放弃传统的单一任务阻塞模式。Gemini 会在重度科研与轻度行政任务间进行科学穿插，利用“交替练习效应”防止认知疲劳。
    - **LLM 动态排程：** AI 综合用户的“记忆文档”与当前任务状态，推理出最优的任务穿插顺序。
- **多模态澄清闭环 (Clarification Loop):** 
    - 引入 **InfantAgent-Next (2025)** 的模块化设计。支持粘贴乱序文本或截图。
    - **置信度检测：** 当意图置信度 < 0.8 时，触发 **MCQ (Minimal Clarification Question)** 询问。
- **叙事化微奖励 (Narrative Micro-Rewards):**
    - **叙事重构：** Gemini 自动将枯燥任务重构为带有趣味性或成就感的短语。
    - **即时反馈：** 在通知中即时反馈“连击 (Streak)”与“经验 (XP)”。

## 4. 未来规划 (Future Roadmap - Plugins & Modules)
核心功能验证成功后，将作为“计算增强插件”逐步加入：
- **本地计算增强 (Local Algo Plugins):**
    - **CLT 自动评估插件：** 自动捕捉系统指标（AXUIElement）转化为认知负荷数值。
    - **UMP 生物钟算法插件：** 基于 **Borbély 二过程模型** 精准计算波峰，辅助 AI 决策。
- **多模态深度感知 (Visual Strategist):**
    - **白板/草稿原位解析：** 直接解析手写草稿生成 ADaPT 拆解树。
    - **桌面感知模块：** 根据当前屏幕内容动态调整穿插优先级。
- **系统级融合 (Full System):**
    - **App Intents:** 允许 Siri 驱动 Agent。
    - **Liquid Glass UI:** 高度定制化的 SwiftUI 原生悬浮面板。

## 5. 核心价值：智慧自动化 (Intelligent Automation)
NSA 不只是一个提醒器，而是一个“数字 CEO”。它在后台默默处理任务拆解、排程优化与多端同步，让用户拥有一个响应极速、具备专业智慧的本地智能核心。
