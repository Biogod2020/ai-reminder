# Notion-Soul-Agent (SOTA) 项目指令上下文

## 1. 项目概览 (Project Overview)
**Notion-Soul-Agent** 是一个基于 **Gemini 3.1 Flash-Lite** 的主动型、多模态任务调度助手。
- **核心目标：** 深度集成 Notion `Tasks [UT]` 数据库，利用 AI 进行认知负荷感知的任务排程，并通过 macOS 原生通知进行主动推送。
- **主要技术栈：**
  - **AI:** Gemini 3.1 Flash-Lite (支持 1M 上下文与多模态输入)。
  - **后端:** Python 3.11+ (异步架构)。
  - **集成:** Notion API, AppleScript/Swift (macOS 系统交互)。
  - **算法:** 认知负荷理论 (CLT)、昼夜节律排单、强化学习偏好建模 (P-DPO/Contextual Bandits)。

## 2. 构建与运行 (Building and Running)
目前项目处于初始化阶段，以下为预期的开发命令：
- **安装依赖:** `pip install -r requirements.txt`
- **运行主 Agent:** `python main.py`
- **同步 Notion:** `python scripts/sync_notion.py`
- **测试多模态输入:** `python tests/test_multimodal.py`
- **TODO:** 需配置 `.env` 文件（包含 `NOTION_TOKEN`, `GEMINI_API_KEY`, `NOTION_DATABASE_ID`）。

## 3. 开发规范 (Development Conventions)
- **多模态澄清闭环:** 当输入模糊时，必须触发 **MCQ (Minimal Clarification Question)**，严禁盲目猜测。
- **主动性逻辑:** 
  - 检查频率：每 30 分钟。
  - 推送标准：基于用户当前的“能量窗口”和“认知负载”。
- **习惯学习:** 必须记录用户对推送的反馈（接受/拒绝/忽略），并定期更新本地 `User Soul` (用户灵魂模型)。
- **安全性:** 严禁硬编码 API 密钥；本地多模态临时缓存需在处理后立即销毁。
- **代码风格:** 遵循 PEP 8，使用异步编程 (asyncio) 以确保 macOS UI 不阻塞。

## 4. 关键文件规划
- `GEMINI.md`: 本项目宪法与指令上下文。
- `main.py`: Agent 核心循环。
- `core/adapter.py`: 支持多模态与自定义 BaseURL 的 Gemini 请求适配器。
- `core/scheduler.py`: 认知负荷与昼夜节律排程引擎。
- `ui/notifier.py`: macOS 交互式通知调度。
