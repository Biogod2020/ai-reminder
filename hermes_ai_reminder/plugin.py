"""Hermes plugin registration entry point."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from . import schemas
from .service import AiReminderService, ServiceSettings, json_handler

SECRETARY_KEYWORDS = {
    "agenda",
    "calendar",
    "deadline",
    "meeting",
    "plan",
    "replan",
    "remind",
    "reminder",
    "schedule",
    "task",
    "today",
    "tomorrow",
    "week",
    "安排",
    "日程",
    "任务",
    "计划",
    "提醒",
    "今天",
    "明天",
    "本周",
    "会议",
    "截止",
    "延期",
    "重排",
}


def _config_int(ctx: Any, key: str, default: int) -> int:
    return int(ctx.get_config(key, default=default))


def _service_from_context(ctx: Any) -> AiReminderService:
    raw_dir = str(
        ctx.get_config(
            "data_dir",
            default=os.getenv("AI_REMINDER_DATA_DIR", "~/.hermes/data/ai-reminder"),
        )
    )
    data_dir = Path(os.path.expandvars(raw_dir)).expanduser()
    settings = ServiceSettings(
        timezone=str(ctx.get_config("timezone", default=os.getenv("TZ", "UTC"))),
        slot_minutes=_config_int(ctx, "slot_minutes", 15),
        planning_horizon_days=_config_int(ctx, "planning_horizon_days", 7),
        transition_buffer_minutes=_config_int(ctx, "transition_buffer_minutes", 0),
        nudge_grace_minutes=_config_int(ctx, "nudge_grace_minutes", 10),
        autonomy_mode=str(ctx.get_config("autonomy_mode", default="propose")),
    )
    return AiReminderService(data_dir / "secretary.db", settings=settings)


def _looks_like_secretary_request(message: str) -> bool:
    lowered = (message or "").lower()
    return any(keyword in lowered for keyword in SECRETARY_KEYWORDS)


def _parse_setup_args(raw: str) -> dict[str, str]:
    values = {
        "morning": "08:00",
        "evening": "21:30",
        "weekly": "18:00",
        "deliver": "origin",
    }
    for token in (raw or "").split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        if key in values and value:
            values[key] = value
    for key in ("morning", "evening", "weekly"):
        if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", values[key]):
            raise ValueError(f"{key} must use HH:MM")
    return values


def _cron_expression(clock: str, weekday: int | None = None) -> str:
    hour, minute = (int(part) for part in clock.split(":", 1))
    return f"{minute} {hour} * * {weekday if weekday is not None else '*'}"


def _extract_job_names(value: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(value, str):
        try:
            return _extract_job_names(json.loads(value))
        except Exception:
            return names
    if isinstance(value, dict):
        if isinstance(value.get("name"), str):
            names.add(value["name"])
        for item in value.values():
            names.update(_extract_job_names(item))
    elif isinstance(value, list):
        for item in value:
            names.update(_extract_job_names(item))
    return names


def register(ctx: Any) -> None:
    service = _service_from_context(ctx)
    toolset = "secretary"

    ctx.register_tool(
        name="secretary_task",
        toolset=toolset,
        schema=schemas.SECRETARY_TASK,
        handler=json_handler(service.handle_task),
    )
    ctx.register_tool(
        name="secretary_plan",
        toolset=toolset,
        schema=schemas.SECRETARY_PLAN,
        handler=json_handler(service.handle_plan),
    )
    ctx.register_tool(
        name="secretary_feedback",
        toolset=toolset,
        schema=schemas.SECRETARY_FEEDBACK,
        handler=json_handler(service.handle_feedback),
    )
    ctx.register_tool(
        name="secretary_preferences",
        toolset=toolset,
        schema=schemas.SECRETARY_PREFERENCES,
        handler=json_handler(service.handle_preferences),
    )
    ctx.register_tool(
        name="secretary_brief",
        toolset=toolset,
        schema=schemas.SECRETARY_BRIEF,
        handler=json_handler(service.handle_brief),
    )
    ctx.register_tool(
        name="secretary_health",
        toolset=toolset,
        schema=schemas.SECRETARY_HEALTH,
        handler=json_handler(service.handle_health),
    )

    skills_dir = Path(__file__).parent / "skills"
    for child in sorted(skills_dir.iterdir()):
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            ctx.register_skill(child.name, skill_md)

    inject_context = bool(ctx.get_config("inject_context", default=True))

    def _inject_secretary_context(
        session_id: str | None = None,
        user_message: str = "",
        is_first_turn: bool = False,
        **kwargs: Any,
    ) -> dict[str, str] | None:
        if not inject_context or not _looks_like_secretary_request(user_message):
            return None
        return {
            "context": (
                "[Hermes AI Reminder]\n"
                "Use the secretary tools as the durable source of truth. Use secretary_plan for "
                "all time arithmetic; do not invent a schedule in prose. Calendar mutations remain "
                "separate and require explicit user confirmation.\n\n"
                + service.compact_context()
            )
        }

    ctx.register_hook("pre_llm_call", _inject_secretary_context)

    def _agenda_command(raw_args: str) -> str:
        mode = (raw_args or "today").strip().lower()
        if mode not in {"today", "tomorrow", "week"}:
            mode = "today"
        return json.dumps(service.handle_brief({"range": mode}), ensure_ascii=False)

    def _tasks_command(raw_args: str) -> str:
        status = (raw_args or "active").strip().lower()
        if status not in {"active", "completed", "archived", "all"}:
            status = "active"
        return json.dumps(
            service.handle_task({"action": "list", "status": status, "limit": 100}),
            ensure_ascii=False,
        )

    def _setup_command(raw_args: str) -> str:
        try:
            options = _parse_setup_args(raw_args)
            existing_raw = ctx.dispatch_tool("cronjob", {"action": "list"})
            existing = _extract_job_names(existing_raw)
            timezone_name = service.timezone_name()
            jobs = [
                {
                    "name": "AI Reminder Morning Brief",
                    "schedule": _cron_expression(options["morning"]),
                    "skills": ["ai-reminder:daily-brief", "google-workspace"],
                    "deliver": options["deliver"],
                    "attach_to_session": True,
                    "enabled_toolsets": ["secretary", "skills", "terminal"],
                    "prompt": (
                        f"Prepare the user's morning brief in timezone {timezone_name}. "
                        "Use the Google Workspace skill to list today's calendar events. Convert them "
                        "to busy_blocks, call secretary_brief(range='today'), and generate a draft plan "
                        "only if today lacks a usable committed plan. Never create or move calendar "
                        "events in this run. Deliver a concise brief and ask for confirmation if a draft "
                        "plan was generated."
                    ),
                },
                {
                    "name": "AI Reminder Evening Review",
                    "schedule": _cron_expression(options["evening"]),
                    "skills": ["ai-reminder:weekly-review"],
                    "deliver": options["deliver"],
                    "attach_to_session": True,
                    "enabled_toolsets": ["secretary", "skills"],
                    "prompt": (
                        f"Run an end-of-day review in timezone {timezone_name}. Call secretary_brief "
                        "for today and secretary_feedback(action='stats', days=14). Ask for only the "
                        "missing execution feedback needed to improve estimates. Do not change user "
                        "preferences without confirmation."
                    ),
                },
                {
                    "name": "AI Reminder Weekly Review",
                    "schedule": _cron_expression(options["weekly"], weekday=0),
                    "skills": ["ai-reminder:weekly-review"],
                    "deliver": options["deliver"],
                    "attach_to_session": True,
                    "enabled_toolsets": ["secretary", "skills"],
                    "prompt": (
                        f"Run the weekly scheduling review in timezone {timezone_name}. Inspect active "
                        "tasks, the next-week brief, and 30-day feedback statistics. Identify deadline "
                        "risk and estimate bias. Propose at most three preference changes, but do not "
                        "apply them until the user confirms."
                    ),
                },
            ]
            results = []
            for job in jobs:
                if job["name"] in existing:
                    results.append({"name": job["name"], "status": "already_exists"})
                    continue
                result = ctx.dispatch_tool("cronjob", {"action": "create", **job})
                results.append({"name": job["name"], "status": "created", "result": result})
            ctx.state.set("cron_bootstrap", {"options": options, "jobs": results})
            return json.dumps({"ok": True, "jobs": results}, ensure_ascii=False, default=str)
        except Exception as exc:
            return json.dumps(
                {"ok": False, "error": {"type": type(exc).__name__, "message": str(exc)}},
                ensure_ascii=False,
            )

    ctx.register_command(
        "agenda",
        handler=_agenda_command,
        description="Show today's, tomorrow's, or this week's deterministic agenda",
        args_hint="[today|tomorrow|week]",
    )
    ctx.register_command(
        "tasks",
        handler=_tasks_command,
        description="List durable secretary tasks",
        args_hint="[active|completed|archived|all]",
    )
    ctx.register_command(
        "secretary-setup",
        handler=_setup_command,
        description="Create morning, evening, and weekly secretary cron jobs",
        args_hint="[morning=08:00] [evening=21:30] [weekly=18:00] [deliver=origin]",
    )

    ctx.state.set("registered_version", "1.0.0")
