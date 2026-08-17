"""Hermes tool schemas — the model-facing API of the secretary."""

from __future__ import annotations

SECRETARY_TASK = {
    "name": "secretary_task",
    "description": (
        "Create, inspect, update, complete, archive, or list durable personal tasks. "
        "Use this as the source of truth for work the user intends to schedule. "
        "Do not encode calendar meetings as tasks unless the user explicitly wants preparation work."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create", "update", "get", "list", "complete", "archive"],
            },
            "task_id": {"type": "string", "description": "Task UUID for non-create actions."},
            "title": {"type": "string"},
            "notes": {"type": "string"},
            "priority": {"type": "integer", "minimum": 1, "maximum": 5},
            "estimate_minutes": {"type": "integer", "minimum": 1},
            "remaining_minutes": {"type": "integer", "minimum": 0},
            "deadline": {
                "type": ["string", "null"],
                "description": "ISO-8601 datetime. Include timezone offset whenever possible.",
            },
            "earliest_start": {
                "type": ["string", "null"],
                "description": "ISO-8601 datetime before which the task must not be scheduled.",
            },
            "energy": {"type": "string", "enum": ["low", "medium", "high"]},
            "cognitive_load": {"type": "number", "minimum": 0, "maximum": 1},
            "splittable": {"type": "boolean"},
            "min_block_minutes": {"type": "integer", "minimum": 5},
            "max_block_minutes": {"type": "integer", "minimum": 5},
            "context": {
                "type": "string",
                "description": "Stable work context such as writing, coding, admin, reading, or calls.",
            },
            "source": {"type": "string"},
            "external_id": {
                "type": ["string", "null"],
                "description": "Optional idempotency key from another task system.",
            },
            "dependencies": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Task UUIDs that must finish first.",
            },
            "changes": {
                "type": "object",
                "description": "Fields to patch for update. Top-level fields are also accepted.",
            },
            "status": {
                "description": "Filter for list: active, completed, archived, all, or an array.",
            },
            "limit": {"type": "integer", "minimum": 1, "maximum": 1000},
        },
        "required": ["action"],
    },
}

SECRETARY_PLAN = {
    "name": "secretary_plan",
    "description": (
        "Generate and manage mathematically feasible personal schedules. The tool enforces availability, "
        "busy calendar intervals, task durations, deadlines, earliest starts, dependencies, energy fit, "
        "and split-block constraints. Generate/replan returns a draft plus proposed Calendar actions. "
        "Never execute those Calendar actions without user confirmation."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "generate",
                    "replan",
                    "get",
                    "list",
                    "commit",
                    "cancel",
                    "link_calendar",
                    "unlink_calendar",
                    "lock_block",
                    "calendar_payload",
                ],
            },
            "plan_id": {"type": "string"},
            "block_id": {"type": "string"},
            "calendar_event_id": {"type": "string"},
            "state": {"type": "string", "enum": ["draft", "committed", "superseded", "cancelled"]},
            "window_start": {"type": "string", "description": "ISO-8601 planning horizon start."},
            "window_end": {"type": "string", "description": "ISO-8601 planning horizon end."},
            "planning_horizon_days": {"type": "integer", "minimum": 1, "maximum": 21},
            "busy_blocks": {
                "type": "array",
                "description": "Fixed Calendar events or other unavailable intervals.",
                "items": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "string"},
                        "end": {"type": "string"},
                        "label": {"type": "string"},
                        "id": {"type": "string"},
                    },
                    "required": ["start", "end"],
                },
            },
            "availability": {
                "type": "array",
                "description": "Explicit work intervals. Omit to use learned/default weekly work windows.",
                "items": {
                    "type": "object",
                    "properties": {"start": {"type": "string"}, "end": {"type": "string"}, "label": {"type": "string"}},
                    "required": ["start", "end"],
                },
            },
            "include_task_ids": {"type": "array", "items": {"type": "string"}},
            "energy_profile": {
                "type": "object",
                "description": "Optional hour-to-score overrides, e.g. {'9':0.9,'15':0.8}.",
            },
            "slot_minutes": {"type": "integer", "enum": [5, 10, 15, 20, 30, 60]},
            "transition_buffer_minutes": {"type": "integer", "minimum": 0, "maximum": 60},
            "solver_seconds": {"type": "number", "minimum": 0.1, "maximum": 30},
            "locked": {"type": "boolean"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 100},
        },
        "required": ["action"],
    },
}

SECRETARY_FEEDBACK = {
    "name": "secretary_feedback",
    "description": (
        "Record explicit execution feedback and learn bounded estimate/hour preferences. "
        "Use after the user accepts, starts, completes, overruns, snoozes, or skips a block. "
        "The tool never infers private behavior from screenshots or background surveillance."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["record", "stats"]},
            "task_id": {"type": "string"},
            "block_id": {"type": "string"},
            "outcome": {
                "type": "string",
                "enum": ["accepted", "started", "completed", "overrun", "snoozed", "skipped"],
            },
            "actual_minutes": {"type": "integer", "minimum": 1},
            "completed_minutes": {
                "type": "integer",
                "minimum": 1,
                "description": (
                    "Amount of task work completed. Defaults to the scheduled block duration; "
                    "keep separate from actual elapsed time when a block overran."
                ),
            },
            "remaining_minutes": {
                "type": "integer",
                "minimum": 0,
                "description": "Explicit remaining-work correction when the user provides it.",
            },
            "note": {"type": "string"},
            "metadata": {"type": "object"},
            "days": {"type": "integer", "minimum": 1, "maximum": 365},
        },
        "required": ["action"],
    },
}

SECRETARY_PREFERENCES = {
    "name": "secretary_preferences",
    "description": (
        "Read or set user-approved scheduling preferences: timezone, weekly work windows, hourly energy prior, "
        "autonomy mode, horizon, slot size, transition buffer, and nudge grace. Never change preferences merely "
        "because a pattern is suspected; present the evidence and obtain confirmation first."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["get", "set", "reset"]},
            "key": {
                "type": "string",
                "enum": [
                    "timezone",
                    "work_windows",
                    "energy_profile",
                    "autonomy_mode",
                    "planning_horizon_days",
                    "slot_minutes",
                    "transition_buffer_minutes",
                    "nudge_grace_minutes",
                ],
            },
            "value": {},
        },
        "required": ["action"],
    },
}

SECRETARY_BRIEF = {
    "name": "secretary_brief",
    "description": (
        "Return a deterministic today/tomorrow/week briefing: current and next block, planned blocks, overdue and "
        "at-risk tasks, and whether a start-check nudge is warranted. Use this for cron-delivered daily briefs and "
        "lightweight drift checks."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "range": {"type": "string", "enum": ["today", "tomorrow", "week"]},
            "now": {"type": "string", "description": "Optional ISO-8601 reference time for tests or replay."},
        },
    },
}

SECRETARY_HEALTH = {
    "name": "secretary_health",
    "description": "Check plugin database, solver backend, timezone, autonomy mode, and object counts.",
    "parameters": {"type": "object", "properties": {}},
}
