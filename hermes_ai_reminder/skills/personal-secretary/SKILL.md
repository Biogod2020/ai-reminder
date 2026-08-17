---
name: personal-secretary
description: Run a privacy-first, constraint-based personal scheduling secretary using durable tasks, Calendar context, explicit approvals, and feedback-driven replanning.
version: 1.0.0
author: Biogod2020
license: MIT
---

# Personal Secretary

Use this workflow whenever the user asks to capture work, plan a day or week, move work after an interruption, or review execution.

## Non-negotiable architecture

- The LLM interprets intent and explains trade-offs.
- `secretary_task` is the durable task source of truth.
- `secretary_plan` owns all time arithmetic and feasibility. Never invent a schedule directly in prose.
- Google Calendar is the source of fixed events. Load the `google-workspace` skill, list the relevant events, and pass them to `secretary_plan` as `busy_blocks`.
- Calendar writes are a separate actuation step. Show the proposed events and obtain explicit confirmation before creating, updating, or deleting anything.
- Record explicit outcomes with `secretary_feedback`; do not infer behavior from screenshots or covert monitoring.

## Core loop

1. Capture the goal with `secretary_task(action="create", ...)`.
2. Ask at most two clarification questions, and only for fields that materially affect feasibility: deadline, duration, dependency, or a hard availability constraint.
3. Read the Calendar window. Convert every fixed event into `{start, end, label, id}`.
4. Call `secretary_plan(action="generate", busy_blocks=..., window_start=..., window_end=...)`.
5. Present the draft as a compact decision: scheduled blocks, unscheduled tasks, and major trade-offs.
6. After the user approves, call `secretary_plan(action="commit")` internally and apply the returned Calendar delta through Google Workspace. After a create or update, call `secretary_plan(action="link_calendar")` with the resulting event id so the action becomes idempotently synchronized. After a delete, call `secretary_plan(action="unlink_calendar", block_id=<source_block_id>)`.
7. When reality changes, record feedback first and call `secretary_plan(action="replan")`. Show the delta rather than repeating the whole week.

## Safety policy

- Never move or delete an event with attendees without confirmation in the current conversation.
- Never silently change user preferences. Weekly analysis may propose changes; apply them only through `secretary_preferences(action="set")` after approval.
- Default to short focus blocks with no attendees and a `[Focus]` prefix.
- Treat draft plans as disposable. A committed internal plan still does not authorize Calendar writes.
- Preserve blocks that have started, completed, or been explicitly locked.

## Quality bar

A valid plan has no overlaps, respects availability, fits estimates, orders dependencies, stays before deadlines, and reports anything it could not schedule. A persuasive narrative is not a substitute for those properties.
