# Architecture

## Product boundary

AI Reminder is not a second agent framework. Hermes owns the agent loop, model routing, memory, messaging, cron, approvals, and Google Workspace workflow. This repository owns only the scheduling domain.

## Separation of responsibilities

| Layer | Responsibility |
|---|---|
| Hermes | Conversation, memory, skills, cron, channels, approvals, tool execution |
| Google Workspace skill | Read fixed Calendar events and apply confirmed event mutations |
| AI Reminder plugin | Tasks, constraints, plans, feedback, local learning, schedule arithmetic |
| LLM | Intent extraction, minimal clarification, explanations, trade-off communication |
| Solver | Feasibility, non-overlap, dependencies, deadlines, energy alignment |

## Durable state

SQLite tables:

- `tasks` and `task_dependencies`
- `plans` and `plan_blocks`
- `feedback`
- `preferences`
- `audit_log`

A plan is versioned. Replanning creates a new draft with `supersedes_plan_id`; the prior plan is superseded only when the new plan is internally committed.

Calendar identity is also versioned. Replanning matches same-task blocks across plan versions, carries the existing event id, and emits an update when time/title changed. Unmatched linked blocks become explicit delete operations. Hermes acknowledges successful creates/updates with `link_calendar` and deletes with `unlink_calendar`, preventing retry-driven duplication.

## Scheduling model

The horizon is discretized into 5–60 minute slots. Candidate blocks are generated only when they:

- fit entirely inside availability;
- do not overlap fixed busy intervals;
- satisfy earliest-start and deadline boundaries;
- obey min/max block sizes;
- can be ordered after dependencies.

When OR-Tools is present, CP-SAT chooses globally among candidate intervals. The objective strongly rewards scheduling high-priority and urgent tasks, then optimizes energy alignment and early placement. Without OR-Tools, a deterministic topological greedy solver uses the same candidates and constraints.

No solver may silently violate a hard constraint. Work that does not fit is returned in `unscheduled` with a reason.

## Actuation boundary

`secretary_plan` returns `calendar_actions`; it does not call Google Calendar. Hermes shows those actions to the user. After confirmation, the Google Workspace skill creates events and the plugin records each returned event id through `link_calendar`.

Generating a fresh plan is rejected when it overlaps an existing committed plan. The caller must use `replan`, so Calendar deltas and preservation rules cannot be bypassed accidentally.

This boundary makes planning replayable and prevents an LLM wording error from becoming an external side effect.

## Learning

The plugin updates two bounded priors from explicit feedback:

- estimate multiplier by stable work context;
- success score by local hour.

Both use conservative online updates and bounded ranges. The plugin does not infer habits from passive surveillance. Suspected changes to work windows, timezone, or autonomy remain proposals until confirmed.

## Failure behavior

- Tool handlers always return JSON and never propagate an exception into the Hermes loop.
- Each database operation uses a short-lived connection.
- SQLite uses WAL, foreign keys, a write lock, and atomic transactions.
- CP-SAT failure degrades to the deterministic solver.
- Missing capacity produces an explicit unscheduled result rather than compressed or overlapping work.
