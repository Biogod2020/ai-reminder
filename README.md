# AI Reminder for Hermes

A privacy-first personal scheduling secretary built as a native [Hermes Agent](https://github.com/NousResearch/hermes-agent) plugin.

The LLM understands goals and communicates decisions. The plugin owns durable task state, constraint solving, plan versioning, execution feedback, and bounded preference learning. Google Calendar remains the source of fixed events and the actuation layer.

## What it does

- Captures durable tasks with estimates, deadlines, dependencies, energy needs, and split-block limits.
- Generates feasible plans against Calendar busy intervals and user availability.
- Uses OR-Tools CP-SAT when installed; otherwise uses a deterministic dependency-free solver.
- Replans only the future while preserving past, started, completed, and locked blocks.
- Emits idempotent Calendar create/update/delete deltas instead of recreating every event.
- Learns estimate bias and productive-hour priors only from explicit user feedback.
- Produces daily/weekly briefs and installs Hermes cron workflows.
- Keeps planning and Calendar mutation separate; Calendar writes require confirmation.

## Architecture

```text
Conversation / Telegram / Feishu / Desktop
                    │
                 Hermes
        intent, memory, cron, messaging
                    │
        ┌───────────┴───────────┐
        │ AI Reminder plugin    │
        │ tasks · plans · stats │
        │ deterministic solver  │
        └───────────┬───────────┘
                    │ proposed events
          Google Workspace skill
                    │
              Google Calendar
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the design contract.
The offline quality gate is documented in [docs/EVALUATION.md](docs/EVALUATION.md).

## Install

Install Hermes first, then install and enable the plugin:

```bash
hermes plugins install Biogod2020/ai-reminder --no-enable
hermes plugins enable ai-reminder
hermes plugins doctor ai-reminder --ci
```

The core plugin has no third-party Python dependencies. For the global CP-SAT optimizer, install the optional solver extra into the same Python environment as Hermes:

```bash
pip install "hermes-ai-reminder[solver]"
```

Without OR-Tools, the deterministic fallback remains fully functional.

## Configure

Set the timezone before serious use:

```yaml
# ~/.hermes/config.yaml
plugins:
  entries:
    ai-reminder:
      enabled: true
      settings:
        timezone: America/Los_Angeles
        data_dir: ~/.hermes/data/ai-reminder
        slot_minutes: 15
        planning_horizon_days: 7
        transition_buffer_minutes: 0
        autonomy_mode: propose
```

Then ask Hermes to set up the bundled `google-workspace` skill for Calendar access.

## Bootstrap the secretary

Inside any Hermes conversation:

```text
/secretary-setup morning=08:00 evening=21:30 weekly=18:00 deliver=origin
```

This creates idempotent morning, evening, and Sunday weekly-review cron jobs. Cron times use the gateway machine's timezone; align the host timezone with the plugin preference.

Useful commands:

```text
/agenda today
/agenda week
/tasks active
```

Natural conversation also works:

```text
I need to finish the rebuttal by Thursday. It needs about five hours of high-focus work.
```

Hermes should capture the task, read Calendar availability, call the deterministic planner, show the draft, and wait for confirmation before creating focus events.

## Tool surface

- `secretary_task` — durable task CRUD.
- `secretary_plan` — generate, replan, commit, lock, link, and unlink Calendar events.
- `secretary_feedback` — record execution outcomes and inspect learned statistics.
- `secretary_preferences` — user-approved scheduling preferences.
- `secretary_brief` — current/next block, deadline risk, and nudge decision.
- `secretary_health` — database and solver diagnostics.

## Data and privacy

Data is stored in a profile-local SQLite database under `~/.hermes/data/ai-reminder/` by default. The project does not capture screenshots, inspect browser history, or read macOS private databases. Learning is based on explicit feedback such as completed, overrun, snoozed, and skipped.

The previous experimental implementation committed personal databases, memory files, and an `.env` file. Deleting them from the current tree does not remove them from Git history. Rotate any credential that ever appeared there and purge history separately before treating the repository as clean. See [SECURITY.md](SECURITY.md).

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

Run the standalone demonstration:

```bash
python scripts/demo.py
python scripts/benchmark.py
```
