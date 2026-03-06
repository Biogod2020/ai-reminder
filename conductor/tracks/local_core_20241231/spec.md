# Specification: Build AI-Native Core & Soul Memory

## Goal
建立以 AI 为核心的决策中枢，实现任务的智慧拆解与情境化记忆系统。

## Requirements
- **Soul Context System:** 设计 `user_soul.md` 动态维护机制，用于存储用户习惯、反馈与效率日志。
- **Strategic Atomization Engine:** 基于 Gemini 3.1 的多模态适配器，增加 `decompose_task` 接口，支持 ADaPT 协议拆解任务。
- **Recursive Task Storage:** 本地数据库需支持“任务-子任务”的递归树状结构，用于存储拆解后的原子任务。
- **Prompt Engineering:** 封装用于任务拆解、穿插排程、叙事重构的高质量提示词模板。

## Deliverables
- `core/memory.py`: 记忆文档管理器 (Markdown CRUD)。
- `core/adapter.py`: 增强版适配器（包含分解、排程接口）。
- `core/models.py`: 递归任务模型 (SubTask support)。
- `tests/test_ai_core.py`: AI 拆解与记忆流自动化测试。
