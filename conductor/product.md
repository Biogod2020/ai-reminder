# Initial Concept

本项目旨在利用 **Gemini 3.1 Flash-Lite** 的多模态能力与高推理性能，构建一个深度集成于 macOS 的 **Notion-Soul-Agent (SOTA)**。

核心目标包括：
1. **Notion 深度集成**：实时同步 `Tasks [UT]` 数据库，分析任务状态。
2. **多模态主动推送**：通过 macOS 原生通知系统，根据用户的认知负荷 (CLT) 与昼夜节律 (Circadian Rhythm) 主动推送任务排程建议。
3. **模糊输入澄清 (Clarification Loop)**：支持粘贴不规范的文本或截图，通过 AI 自动澄清意图并更新 Notion。
4. **用户习惯学习**：通过 RLHF (P-DPO) 学习用户偏好、工作习惯与效率波峰，实现“类人”的自动化规划。
5. **系统级集成**：利用 macOS App Intents 与后台常驻服务 (`SMAppService`) 实现无感、无缝的操作体验。

# Product Guide - Notion-Soul-Agent (SOTA)

## Overview
Notion-Soul-Agent is a proactive, AI-driven task management system that bridges the gap between your digital knowledge base (Notion) and your daily macOS workflow. It acts as an autonomous "Digital Soul" that understands your work patterns, manages your cognitive load, and handles unstructured information through multi-modal input.

## Target Audience
- **Primary:** Researcher/Student and Busy Professionals who deal with complex, high-stakes tasks (e.g., data standardization, research workflows).
- **Secondary:** General productivity enthusiasts looking for a seamless, AI-orchestrated task management experience.

## Key Features
- **Deep Notion Sync:** Real-time bidirectional synchronization with the `Tasks [UT]` database. The agent acts as a living extension of your Notion setup.
- **Proactive AI Scheduling:** Utilizing Gemini 3.1 Flash-Lite to perform time-blocking and energy-peak analysis, ensuring high-intensity tasks are scheduled during your most productive hours.
- **Multi-modal Clarification Loop:** Seamlessly processes unstructured text, messy screenshots, and whiteboard photos to automatically extract intents and update your Notion database after a brief clarification cycle.
- **Adaptive Habit Learning:** Leverages RLHF (P-DPO) and Contextual Bandits to learn your working style, preferences, and productivity rhythms, continuously optimizing your schedule.
- **Proactive User Interaction:** Regularly engages with the user to verify plans, provide reminders, and solicit feedback on the current schedule.

## User Interface & Experience
- **Multi-layered macOS Integration:**
    - **Menu Bar App:** Persistent status and quick access to the agent's current "thought" or focus.
    - **Floating Panel:** A rich, interactive interface for deep planning and viewing complex schedules.
    - **Native Notifications:** Actionable macOS alerts for proactive pushes, allowing users to "Approve," "Delay," or "Clarify" tasks directly from the banner.
- **Cross-platform Interaction:** While optimized for macOS, the agent maintains its "presence" within Notion blocks, allowing for consistent interaction across multiple platforms where Notion is available.

## Core Value Proposition: Seamless Automation
The Notion-Soul-Agent aims to provide a "set-and-forget" orchestration layer for personal productivity. By automating the tedious parts of task planning and information extraction, it frees the user to focus on their core work while ensuring that their long-term goals and short-term actions remain perfectly aligned.
