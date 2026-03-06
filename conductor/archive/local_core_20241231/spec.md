# Specification: Build AI-Native Core & Soul Memory

## Goal
建立以 AI 为核心的决策中枢，实现任务的智慧拆解与情境化记忆系统。

## Requirements
- **Native Skill Architecture:** 在 \`core/skills/\` 建立模块化指令集（SKILL.md）。Agent 需支持“按需挂载”这些专家指令。
- **Soul Context System:** 设计 \`user_soul.md\` 动态维护机制，用于存储用户习惯、反馈与效率日志。
- **Strategic Atomization Engine:** 基于 Gemini 3.1 的多模态适配器，通过 \`task-atomizer\` 技能实现 ADaPT 协议拆解。
- **Recursive Task Storage:** 本地数据库需支持“任务-子任务”的递归树状结构。

## Deliverables
- `core/memory.py`: 记忆文档管理器 (Markdown CRUD)。
- `core/adapter.py`: 增强版适配器（包含分解、排程接口）。
- `core/models.py`: 递归任务模型 (SubTask support)。
- `tests/test_ai_core.py`: AI 拆解与记忆流自动化测试。
