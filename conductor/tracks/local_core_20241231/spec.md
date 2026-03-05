# Specification: Build Local Core Foundation

## Goal
建立解耦架构的核心地基，实现本地数据持久化与高灵活性的 AI 请求能力。

## Requirements
- **Local DB Schema:** 设计基于 SQLite 的数据库，包含任务表 (Tasks)、习惯表 (Habits) 和执行日志 (Logs)。需兼容 Notion `Tasks [UT]` 字段并扩展认知负荷字段。
- **Gemini Adapter:** 实现一个 Python 类，支持自定义 `base_url`、多模态 (Text/Image) 请求，并封装针对 Flash-Lite 的优化提示词。
- **Environment:** 使用 `uv` 管理依赖，确保异步支持 (`asyncio`)。

## Deliverables
- `core/models.py`: 数据库模型定义。
- `core/adapter.py`: AI 请求适配器。
- `tests/test_core.py`: 核心组件自动化测试。
