"""Application service exposed through Hermes tools."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence

from .learning import apply_feedback_learning, effective_estimate_multiplier, learned_energy_profile
from .models import Interval, PlanBlock, TaskRecord
from .scheduler import ConstraintScheduler, SchedulerInput
from .store import SqliteStore, calendar_signature
from .time_utils import (
    build_availability,
    day_range,
    default_energy_profile,
    default_work_windows,
    get_timezone,
    parse_datetime,
    parse_intervals,
    utc_now,
    validate_energy_profile,
    validate_work_windows,
)


@dataclass(slots=True)
class ServiceSettings:
    timezone: str = "UTC"
    slot_minutes: int = 15
    planning_horizon_days: int = 7
    transition_buffer_minutes: int = 0
    nudge_grace_minutes: int = 10
    autonomy_mode: str = "propose"


class AiReminderService:
    def __init__(self, db_path: str | Path, settings: ServiceSettings | None = None):
        self.settings = settings or ServiceSettings()
        self.store = SqliteStore(db_path)
        self.scheduler = ConstraintScheduler(prefer_ortools=True)
        self._seed_defaults()

    def _seed_defaults(self) -> None:
        defaults = {
            "timezone": self.settings.timezone,
            "slot_minutes": self.settings.slot_minutes,
            "planning_horizon_days": self.settings.planning_horizon_days,
            "transition_buffer_minutes": self.settings.transition_buffer_minutes,
            "nudge_grace_minutes": self.settings.nudge_grace_minutes,
            "autonomy_mode": self.settings.autonomy_mode,
            "work_windows": default_work_windows(),
            "energy_profile": default_energy_profile(),
        }
        for key, value in defaults.items():
            if self.store.get_preference(key, None) is None:
                self.store.set_preference(key, value)

    def timezone_name(self) -> str:
        return str(self.store.get_preference("timezone", self.settings.timezone))

    def _tz(self):
        return get_timezone(self.timezone_name())

    @staticmethod
    def _ok(data: Any, **extra: Any) -> dict[str, Any]:
        return {"ok": True, "data": data, **extra}

    @staticmethod
    def _normalise_action(args: dict[str, Any], default: str) -> str:
        return str(args.get("action") or default).strip().lower().replace("-", "_")

    @staticmethod
    def _require(args: dict[str, Any], key: str) -> Any:
        value = args.get(key)
        if value is None or value == "":
            raise ValueError(f"Missing required field: {key}")
        return value

    def handle_task(self, args: dict[str, Any]) -> dict[str, Any]:
        action = self._normalise_action(args, "list")
        if action == "create":
            title = str(self._require(args, "title")).strip()
            if not title:
                raise ValueError("title cannot be blank")
            estimate = (
                int(args["estimate_minutes"])
                if args.get("estimate_minutes") is not None
                else 30
            )
            if estimate <= 0:
                raise ValueError("estimate_minutes must be positive")
            tz = self._tz()
            deadline = parse_datetime(args.get("deadline"), tz)
            earliest = parse_datetime(args.get("earliest_start"), tz)
            warnings: list[str] = []
            if args.get("estimate_minutes") is None:
                warnings.append("estimate_minutes defaulted to 30; clarify when accuracy matters")
            if deadline is None:
                warnings.append("no deadline supplied")

            external_id = args.get("external_id")
            if external_id:
                existing = self.store.get_task_by_external_id(str(external_id))
                if existing:
                    return self._ok(existing.to_dict(), created=False, warnings=warnings)

            task = self.store.create_task(
                {
                    "title": title,
                    "notes": str(args.get("notes") or ""),
                    "priority": int(args.get("priority", 3)),
                    "estimate_minutes": estimate,
                    "remaining_minutes": int(args.get("remaining_minutes", estimate)),
                    "deadline": deadline.astimezone(timezone.utc).isoformat() if deadline else None,
                    "earliest_start": earliest.astimezone(timezone.utc).isoformat() if earliest else None,
                    "energy": str(args.get("energy") or "medium").lower(),
                    "cognitive_load": float(args.get("cognitive_load", 0.5)),
                    "splittable": bool(args.get("splittable", True)),
                    "min_block_minutes": int(args.get("min_block_minutes", 25)),
                    "max_block_minutes": int(args.get("max_block_minutes", 90)),
                    "context": str(args.get("context") or "general"),
                    "source": str(args.get("source") or "conversation"),
                    "external_id": str(external_id) if external_id else None,
                },
                dependencies=args.get("dependencies") or [],
            )
            return self._ok(task.to_dict(), created=True, warnings=warnings)

        if action == "update":
            task_id = str(self._require(args, "task_id"))
            changes = dict(args.get("changes") or {})
            for key in (
                "title",
                "notes",
                "status",
                "priority",
                "estimate_minutes",
                "remaining_minutes",
                "energy",
                "cognitive_load",
                "splittable",
                "min_block_minutes",
                "max_block_minutes",
                "context",
                "source",
                "external_id",
            ):
                if key in args:
                    changes[key] = args[key]
            tz = self._tz()
            for key in ("deadline", "earliest_start"):
                if key in args or key in changes:
                    raw = args[key] if key in args else changes[key]
                    parsed = parse_datetime(raw, tz)
                    changes[key] = parsed.astimezone(timezone.utc).isoformat() if parsed else None
            dependencies = args.get("dependencies")
            task = self.store.update_task(task_id, changes, dependencies=dependencies)
            return self._ok(task.to_dict())

        if action == "get":
            return self._ok(self.store.get_task(str(self._require(args, "task_id"))).to_dict())

        if action == "complete":
            task_id = str(self._require(args, "task_id"))
            task = self.store.update_task(
                task_id, {"status": "completed", "remaining_minutes": 0}
            )
            return self._ok(task.to_dict())

        if action == "archive":
            task = self.store.update_task(
                str(self._require(args, "task_id")), {"status": "archived"}
            )
            return self._ok(task.to_dict())

        if action == "list":
            status = args.get("status")
            statuses: Sequence[str] | None
            if status in {None, "all"}:
                statuses = None
            elif isinstance(status, list):
                statuses = [str(item) for item in status]
            else:
                statuses = [str(status)]
            tasks = self.store.list_tasks(statuses=statuses, limit=int(args.get("limit", 100)))
            return self._ok([task.to_dict() for task in tasks], count=len(tasks))

        raise ValueError(f"Unsupported task action: {action}")

    def _prepare_scheduler_tasks(
        self,
        include_task_ids: Sequence[str] | None = None,
        reserved_minutes_by_task: dict[str, int] | None = None,
        reserved_completion_by_task: dict[str, datetime] | None = None,
    ) -> list[TaskRecord]:
        all_tasks = self.store.list_tasks(statuses=["active", "completed", "archived"], limit=1000)
        task_by_id = {task.id: task for task in all_tasks}
        include = {str(item) for item in include_task_ids or []}
        if include:
            unknown = sorted(include - task_by_id.keys())
            if unknown:
                raise ValueError(f"Unknown include_task_ids: {unknown}")
            stack = list(include)
            while stack:
                task = task_by_id[stack.pop()]
                for dependency in task.dependencies:
                    if dependency not in include:
                        include.add(dependency)
                        stack.append(dependency)
        reserved = reserved_minutes_by_task or {}
        reserved_completion = reserved_completion_by_task or {}
        result: list[TaskRecord] = []
        for task in all_tasks:
            if include and task.status == "active" and task.id not in include:
                continue
            if task.status == "active":
                original_remaining = task.remaining_minutes
                base_remaining = max(0, original_remaining - int(reserved.get(task.id, 0)))
                multiplier = effective_estimate_multiplier(self.store, task.context)
                task.remaining_minutes = (
                    max(1, int(math.ceil(base_remaining * multiplier)))
                    if base_remaining > 0
                    else 0
                )
                if base_remaining == 0 and original_remaining > 0:
                    # For this planning run only, preserved blocks satisfy the task's
                    # remaining work. Durable task state is unchanged until feedback.
                    task.status = "completed"
                dependency_floor = max(
                    (
                        reserved_completion[dependency]
                        for dependency in task.dependencies
                        if dependency in reserved_completion
                    ),
                    default=None,
                )
                if dependency_floor is not None:
                    task.earliest_start = max(
                        filter(None, (task.earliest_start, dependency_floor))
                    )
            result.append(task)
        return result

    def _parse_window(self, args: dict[str, Any]) -> tuple[datetime, datetime]:
        tz = self._tz()
        now = datetime.now(tz)
        start = parse_datetime(args.get("window_start"), tz) or now
        horizon = int(
            args["planning_horizon_days"]
            if args.get("planning_horizon_days") is not None
            else self.store.get_preference(
                "planning_horizon_days", self.settings.planning_horizon_days
            )
        )
        if not 1 <= horizon <= 21:
            raise ValueError("planning_horizon_days must be between 1 and 21")
        end = parse_datetime(args.get("window_end"), tz) or (start + timedelta(days=horizon))
        if end <= start:
            raise ValueError("window_end must be after window_start")
        if end - start > timedelta(days=21):
            raise ValueError("Planning window cannot exceed 21 days")
        return start, end

    def _availability(
        self, args: dict[str, Any], start: datetime, end: datetime
    ) -> list[Interval]:
        explicit = args.get("availability")
        if explicit is not None:
            return parse_intervals(explicit, self._tz())
        work_windows = self.store.get_preference("work_windows", default_work_windows())
        return build_availability(start, end, self.timezone_name(), work_windows)

    @staticmethod
    def _preserved_plan_block(block: dict[str, Any]) -> PlanBlock:
        start = parse_datetime(block["start"], timezone.utc)
        end = parse_datetime(block["end"], timezone.utc)
        if start is None or end is None:
            raise ValueError("Stored plan block has invalid timestamps")
        rationale = list(block.get("rationale") or [])
        rationale.append(f"preserved from block {block['id']}")
        return PlanBlock(
            task_id=block["task_id"],
            task_title=block["task_title"],
            start=start,
            end=end,
            piece_index=int(block["piece_index"]),
            piece_count=int(block["piece_count"]),
            context=block["context"],
            energy=block["energy"],
            score=float(block.get("score") or 0.0),
            rationale=rationale,
            locked=bool(block.get("locked")),
            state=str(block.get("state") or "planned"),
            calendar_event_id=block.get("calendar_event_id"),
            calendar_signature=block.get("calendar_signature"),
            source_block_id=block["id"],
        )

    @staticmethod
    def _match_replanned_blocks(
        previous_blocks: list[dict[str, Any]], new_blocks: list[PlanBlock]
    ) -> list[dict[str, Any]]:
        """Carry external event identity across a replan and return removals.

        Exact same-task/time matches are paired first. Remaining blocks are
        paired chronologically within each task, which turns a moved focus block
        into an update instead of a duplicate create plus orphaned old event.
        """

        available_old = {block["id"]: block for block in previous_blocks}
        matched_new: set[int] = set()

        def attach(new: PlanBlock, old: dict[str, Any]) -> None:
            new.source_block_id = old["id"]
            new.calendar_event_id = old.get("calendar_event_id")
            new.calendar_signature = old.get("calendar_signature")
            available_old.pop(old["id"], None)

        for index, new in enumerate(new_blocks):
            exact = next(
                (
                    old
                    for old in available_old.values()
                    if old["task_id"] == new.task_id
                    and old["start"] == new.start.astimezone(timezone.utc).isoformat()
                    and old["end"] == new.end.astimezone(timezone.utc).isoformat()
                ),
                None,
            )
            if exact:
                attach(new, exact)
                matched_new.add(index)

        task_ids = sorted(
            {new.task_id for index, new in enumerate(new_blocks) if index not in matched_new}
        )
        for task_id in task_ids:
            old_for_task = sorted(
                (old for old in available_old.values() if old["task_id"] == task_id),
                key=lambda item: item["start"],
            )
            new_for_task = sorted(
                (
                    (index, new)
                    for index, new in enumerate(new_blocks)
                    if index not in matched_new and new.task_id == task_id
                ),
                key=lambda item: item[1].start,
            )
            for old, (index, new) in zip(old_for_task, new_for_task, strict=False):
                attach(new, old)
                matched_new.add(index)

        return sorted(available_old.values(), key=lambda item: item["start"])

    def _calendar_actions(self, plan: dict[str, Any]) -> list[dict[str, Any]]:
        actions: list[dict[str, Any]] = []
        for block in plan.get("blocks", []):
            if block.get("state") in {"completed", "cancelled", "skipped"}:
                continue
            if block.get("calendar_event_id"):
                current_signature = calendar_signature(
                    block["task_title"], block["start"], block["end"]
                )
                if block.get("calendar_signature") != current_signature:
                    actions.append(
                        {
                            "action": "update",
                            "event_id": block["calendar_event_id"],
                            "summary": f"[Focus] {block['task_title']}",
                            "start": block["start"],
                            "end": block["end"],
                            "description": (
                                "Managed by Hermes AI Reminder.\n"
                                f"plan_id={plan['id']}\n"
                                f"block_id={block['id']}\n"
                                f"task_id={block['task_id']}"
                            ),
                            "attendees": [],
                            "requires_confirmation": True,
                            "source_block_id": block.get("source_block_id"),
                        }
                    )
                continue
            actions.append(
                {
                    "action": "create",
                    "summary": f"[Focus] {block['task_title']}",
                    "start": block["start"],
                    "end": block["end"],
                    "description": (
                        "Managed by Hermes AI Reminder.\n"
                        f"plan_id={plan['id']}\n"
                        f"block_id={block['id']}\n"
                        f"task_id={block['task_id']}"
                    ),
                    "attendees": [],
                    "requires_confirmation": True,
                    "link_after_create": {
                        "plan_action": "link_calendar",
                        "block_id": block["id"],
                    },
                }
            )
        for removed in plan.get("details", {}).get("removed_blocks", []):
            try:
                source = self.store.get_block(removed["id"])
            except KeyError:
                source = removed
            if source.get("calendar_event_id"):
                actions.append(
                    {
                        "action": "delete",
                        "event_id": source["calendar_event_id"],
                        "summary": f"[Focus] {removed['task_title']}",
                        "source_block_id": removed["id"],
                        "requires_confirmation": True,
                    }
                )
        return actions

    def handle_plan(self, args: dict[str, Any]) -> dict[str, Any]:
        action = self._normalise_action(args, "get")
        if action in {"generate", "replan"}:
            start, end = self._parse_window(args)
            busy = parse_intervals(args.get("busy_blocks") or [], self._tz())
            supersedes: str | None = None
            preserved: list[dict[str, Any]] = []
            preserved_blocks: list[PlanBlock] = []
            mutable_previous: list[dict[str, Any]] = []
            source_blocks: list[dict[str, Any]] = []
            removed_blocks: list[dict[str, Any]] = []
            reserved_minutes: dict[str, int] = {}
            reserved_completion: dict[str, datetime] = {}
            if action == "generate":
                try:
                    committed = self.store.get_plan(state="committed")
                except KeyError:
                    committed = None
                if committed:
                    committed_start = parse_datetime(
                        committed["window_start"], timezone.utc
                    )
                    committed_end = parse_datetime(committed["window_end"], timezone.utc)
                    if (
                        committed_start is not None
                        and committed_end is not None
                        and committed_start < end.astimezone(timezone.utc)
                        and committed_end > start.astimezone(timezone.utc)
                    ):
                        raise ValueError(
                            "An overlapping committed plan already exists; use "
                            f"action='replan' with plan_id='{committed['id']}'"
                        )
            if action == "replan":
                plan_id = args.get("plan_id")
                try:
                    previous = self.store.get_plan(str(plan_id) if plan_id else None, state=None if plan_id else "committed")
                except KeyError:
                    previous = None
                if previous is None:
                    raise KeyError("No committed plan is available to replan")
                supersedes = previous["id"]
                now_utc = utc_now()
                for block in previous["blocks"]:
                    block_start = parse_datetime(block["start"], timezone.utc)
                    block_end = parse_datetime(block["end"], timezone.utc)
                    if block_start is None or block_end is None:
                        continue
                    if block_end <= start or block_start >= end:
                        continue
                    if block["state"] == "cancelled":
                        continue
                    source_blocks.append(block)
                    should_preserve = bool(block["locked"]) or block["state"] in {
                        "in_progress",
                        "completed",
                    }
                    if should_preserve or block_start <= now_utc:
                        busy.append(
                            Interval(
                                start=block_start,
                                end=block_end,
                                label=f"preserved:{block['task_title']}",
                                external_id=block["id"],
                            )
                        )
                        preserved.append(block)
                        preserved_blocks.append(self._preserved_plan_block(block))
                        if block["state"] != "completed":
                            reserved_minutes[block["task_id"]] = reserved_minutes.get(
                                block["task_id"], 0
                            ) + int(block["duration_minutes"])
                            reserved_completion[block["task_id"]] = max(
                                reserved_completion.get(block["task_id"], block_end),
                                block_end,
                            )
                    else:
                        mutable_previous.append(block)

            availability = self._availability(args, start, end)
            tasks = self._prepare_scheduler_tasks(
                args.get("include_task_ids"),
                reserved_minutes_by_task=reserved_minutes,
                reserved_completion_by_task=reserved_completion,
            )
            energy_profile = learned_energy_profile(self.store)
            if args.get("energy_profile") is not None:
                energy_profile.update(validate_energy_profile(args["energy_profile"]))
            slot_minutes = int(
                args["slot_minutes"]
                if args.get("slot_minutes") is not None
                else self.store.get_preference("slot_minutes", self.settings.slot_minutes)
            )
            if slot_minutes not in {5, 10, 15, 20, 30, 60}:
                raise ValueError("slot_minutes must be one of 5, 10, 15, 20, 30, 60")
            transition = int(
                args.get("transition_buffer_minutes")
                if args.get("transition_buffer_minutes") is not None
                else self.store.get_preference(
                    "transition_buffer_minutes", self.settings.transition_buffer_minutes
                )
            )
            if not 0 <= transition <= 60:
                raise ValueError("transition_buffer_minutes must be between 0 and 60")
            solver_seconds = float(args.get("solver_seconds", 3.0))
            if not 0.1 <= solver_seconds <= 30:
                raise ValueError("solver_seconds must be between 0.1 and 30")
            result = self.scheduler.schedule(
                SchedulerInput(
                    tasks=tasks,
                    window_start=start,
                    window_end=end,
                    availability=availability,
                    busy=busy,
                    energy_profile=energy_profile,
                    slot_minutes=slot_minutes,
                    transition_buffer_minutes=transition,
                    solver_seconds=solver_seconds,
                )
            )
            if mutable_previous:
                removed_blocks = self._match_replanned_blocks(
                    mutable_previous, result.blocks
                )
            blocks = preserved_blocks + result.blocks
            blocks.sort(key=lambda block: (block.start, block.end, block.task_id))
            diagnostics = dict(result.diagnostics)
            diagnostics.update(
                {
                    "preserved_blocks": len(preserved_blocks),
                    "preserved_minutes": sum(
                        block.duration_minutes for block in preserved_blocks
                    ),
                    "new_blocks": len(result.blocks),
                    "removed_blocks": len(removed_blocks),
                }
            )
            plan = self.store.create_plan(
                window_start=start.astimezone(timezone.utc).isoformat(),
                window_end=end.astimezone(timezone.utc).isoformat(),
                timezone_name=self.timezone_name(),
                backend=result.backend,
                objective_score=result.objective_score
                + sum(block.score for block in preserved_blocks),
                blocks=blocks,
                details={
                    "unscheduled": result.unscheduled,
                    "diagnostics": diagnostics,
                    "busy_blocks": [item.to_dict() for item in busy],
                    "availability": [item.to_dict() for item in availability],
                    "preserved_blocks": preserved,
                    "source_blocks": source_blocks,
                    "removed_blocks": removed_blocks,
                },
                supersedes_plan_id=supersedes,
            )
            calendar_actions = self._calendar_actions(plan)
            plan_delta = {
                "preserved": len(preserved_blocks),
                "created": sum(
                    action["action"] == "create" for action in calendar_actions
                ),
                "updated": sum(
                    action["action"] == "update" for action in calendar_actions
                ),
                "deleted": sum(
                    action["action"] == "delete" for action in calendar_actions
                ),
                "unscheduled": len(result.unscheduled),
            }
            return self._ok(
                plan,
                calendar_actions=calendar_actions,
                plan_delta=plan_delta,
                requires_confirmation=True,
                note=(
                    "This is a draft. Confirm before creating or moving calendar events."
                ),
            )

        if action == "get":
            plan_id = args.get("plan_id")
            state = args.get("state")
            plan = self.store.get_plan(str(plan_id) if plan_id else None, state=str(state) if state else None)
            return self._ok(plan, calendar_actions=self._calendar_actions(plan))

        if action == "list":
            return self._ok(self.store.list_plans(limit=int(args.get("limit", 20))))

        if action == "commit":
            plan = self.store.set_plan_state(str(self._require(args, "plan_id")), "committed")
            return self._ok(
                plan,
                calendar_actions=self._calendar_actions(plan),
                note="Internal plan committed. Calendar actions still require user confirmation.",
            )

        if action == "cancel":
            return self._ok(
                self.store.set_plan_state(str(self._require(args, "plan_id")), "cancelled")
            )

        if action == "link_calendar":
            block = self.store.link_calendar_event(
                str(self._require(args, "block_id")),
                str(self._require(args, "calendar_event_id")),
            )
            return self._ok(block)

        if action == "unlink_calendar":
            block = self.store.unlink_calendar_event(
                str(self._require(args, "block_id"))
            )
            return self._ok(block)

        if action == "lock_block":
            block_id = str(self._require(args, "block_id"))
            block = self.store.get_block(block_id)
            updated = self.store.set_block_state(
                block_id,
                block["state"],
                locked=bool(args.get("locked", True)),
            )
            return self._ok(updated)

        if action == "calendar_payload":
            plan = self.store.get_plan(str(self._require(args, "plan_id")))
            return self._ok(self._calendar_actions(plan), requires_confirmation=True)

        raise ValueError(f"Unsupported plan action: {action}")

    def handle_feedback(self, args: dict[str, Any]) -> dict[str, Any]:
        action = self._normalise_action(args, "record")
        if action == "stats":
            return self._ok(
                {
                    "outcomes": self.store.feedback_stats(days=int(args.get("days", 30))),
                    "estimate_bias": self.store.get_preference("estimate_bias", {}),
                    "hour_success": self.store.get_preference("hour_success", {}),
                    "effective_energy_profile": learned_energy_profile(self.store),
                }
            )
        if action != "record":
            raise ValueError(f"Unsupported feedback action: {action}")

        outcome = str(self._require(args, "outcome")).lower()
        allowed_outcomes = {"accepted", "started", "completed", "overrun", "snoozed", "skipped"}
        if outcome not in allowed_outcomes:
            raise ValueError(f"outcome must be one of {sorted(allowed_outcomes)}")
        block_id = str(args["block_id"]) if args.get("block_id") else None
        task_id = str(args["task_id"]) if args.get("task_id") else None
        block = self.store.get_block(block_id) if block_id else None
        if block and task_id is None:
            task_id = block["task_id"]
        if task_id is None:
            raise ValueError("task_id or block_id is required")
        task = self.store.get_task(task_id)
        actual_minutes = (
            int(args["actual_minutes"]) if args.get("actual_minutes") is not None else None
        )
        if actual_minutes is not None and actual_minutes <= 0:
            raise ValueError("actual_minutes must be positive")
        completed_minutes = (
            int(args["completed_minutes"])
            if args.get("completed_minutes") is not None
            else None
        )
        if completed_minutes is not None and completed_minutes <= 0:
            raise ValueError("completed_minutes must be positive")
        explicit_remaining = (
            int(args["remaining_minutes"])
            if args.get("remaining_minutes") is not None
            else None
        )
        if explicit_remaining is not None and explicit_remaining < 0:
            raise ValueError("remaining_minutes cannot be negative")

        state_map = {
            "accepted": "committed",
            "started": "in_progress",
            "completed": "completed",
            "overrun": "in_progress",
            "snoozed": "snoozed",
            "skipped": "skipped",
        }
        if block:
            self.store.set_block_state(block["id"], state_map[outcome])

        if explicit_remaining is not None:
            changes: dict[str, Any] = {"remaining_minutes": explicit_remaining}
            if explicit_remaining == 0:
                changes["status"] = "completed"
            elif task.status == "completed":
                changes["status"] = "active"
            task = self.store.update_task(task.id, changes)
        elif outcome == "completed":
            credit = completed_minutes or (
                block["duration_minutes"] if block else task.remaining_minutes
            )
            remaining = max(0, task.remaining_minutes - credit)
            changes: dict[str, Any] = {"remaining_minutes": remaining}
            if remaining == 0:
                changes["status"] = "completed"
            task = self.store.update_task(task.id, changes)

        feedback = self.store.record_feedback(
            task_id=task_id,
            block_id=block_id,
            outcome=outcome,
            actual_minutes=actual_minutes,
            note=str(args.get("note") or ""),
            metadata=dict(args.get("metadata") or {}),
        )
        scheduled_minutes = block["duration_minutes"] if block else task.estimate_minutes
        start_hour = None
        if block:
            start_dt = parse_datetime(block["start"], timezone.utc)
            if start_dt:
                start_hour = start_dt.astimezone(self._tz()).hour
        learned = apply_feedback_learning(
            self.store,
            context=task.context,
            scheduled_minutes=scheduled_minutes,
            actual_minutes=actual_minutes,
            start_hour=start_hour,
            outcome=outcome,
        )
        return self._ok(
            {
                "feedback": feedback,
                "task": self.store.get_task(task_id).to_dict(),
                "learning_updates": learned,
                "replan_recommended": outcome in {"overrun", "snoozed", "skipped"},
            }
        )

    def handle_preferences(self, args: dict[str, Any]) -> dict[str, Any]:
        action = self._normalise_action(args, "get")
        allowed = {
            "timezone",
            "work_windows",
            "energy_profile",
            "autonomy_mode",
            "planning_horizon_days",
            "slot_minutes",
            "transition_buffer_minutes",
            "nudge_grace_minutes",
        }
        if action == "get":
            key = args.get("key")
            if key:
                return self._ok({str(key): self.store.get_preference(str(key))})
            return self._ok(self.store.all_preferences())
        if action == "set":
            key = str(self._require(args, "key"))
            if key not in allowed:
                raise ValueError(f"Unsupported user preference key: {key}")
            value = self._require(args, "value")
            if key == "timezone":
                get_timezone(str(value))
                value = str(value)
            elif key == "work_windows":
                value = validate_work_windows(value)
            elif key == "energy_profile":
                value = validate_energy_profile(value)
            elif key == "autonomy_mode":
                value = str(value)
                if value not in {"observe", "propose", "focus_blocks"}:
                    raise ValueError("autonomy_mode must be observe, propose, or focus_blocks")
            elif key == "planning_horizon_days":
                value = int(value)
                if not 1 <= value <= 21:
                    raise ValueError("planning_horizon_days must be between 1 and 21")
            elif key == "slot_minutes":
                value = int(value)
                if value not in {5, 10, 15, 20, 30, 60}:
                    raise ValueError("slot_minutes must be one of 5, 10, 15, 20, 30, 60")
            elif key == "transition_buffer_minutes":
                value = int(value)
                if not 0 <= value <= 60:
                    raise ValueError("transition_buffer_minutes must be between 0 and 60")
            elif key == "nudge_grace_minutes":
                value = int(value)
                if not 0 <= value <= 240:
                    raise ValueError("nudge_grace_minutes must be between 0 and 240")
            self.store.set_preference(key, value)
            return self._ok({key: value})
        if action == "reset":
            for key in allowed:
                self.store.delete_preference(key)
            self._seed_defaults()
            return self._ok(self.store.all_preferences())
        raise ValueError(f"Unsupported preferences action: {action}")

    def handle_brief(self, args: dict[str, Any]) -> dict[str, Any]:
        mode = str(args.get("range") or "today").lower()
        now = parse_datetime(args.get("now"), self._tz()) or datetime.now(self._tz())
        start, end = day_range(now, mode, self.timezone_name())
        effective_plan: dict[str, Any] | None = None
        try:
            effective_plan = self.store.get_plan(state="committed")
        except KeyError:
            try:
                effective_plan = self.store.get_plan(state="draft")
            except KeyError:
                effective_plan = None
        start_utc = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)
        blocks: list[dict[str, Any]] = []
        if effective_plan:
            for block in effective_plan["blocks"]:
                block_start = parse_datetime(block["start"], timezone.utc)
                block_end = parse_datetime(block["end"], timezone.utc)
                if block_start is None or block_end is None:
                    continue
                if block["state"] in {"cancelled", "skipped"}:
                    continue
                if block_start < end_utc and block_end > start_utc:
                    blocks.append(block)
            blocks.sort(key=lambda item: item["start"])
        active_tasks = self.store.list_tasks(statuses=["active"], limit=500)
        overdue = [
            task.to_dict()
            for task in active_tasks
            if task.deadline and task.deadline < now.astimezone(timezone.utc)
        ]
        scheduled_by_task: dict[str, int] = {}
        for block in blocks:
            if block["state"] not in {"cancelled", "skipped"}:
                scheduled_by_task[block["task_id"]] = scheduled_by_task.get(block["task_id"], 0) + int(
                    block["duration_minutes"]
                )
        at_risk: list[dict[str, Any]] = []
        for task in active_tasks:
            if task.deadline is None:
                continue
            hours = (task.deadline - now.astimezone(timezone.utc)).total_seconds() / 3600
            scheduled = scheduled_by_task.get(task.id, 0)
            if hours <= 72 and scheduled < task.remaining_minutes:
                at_risk.append(
                    {
                        "task_id": task.id,
                        "title": task.title,
                        "deadline": task.deadline.isoformat(),
                        "remaining_minutes": task.remaining_minutes,
                        "scheduled_minutes_in_range": scheduled,
                        "gap_minutes": task.remaining_minutes - scheduled,
                    }
                )

        current = None
        next_block = None
        now_utc = now.astimezone(timezone.utc)
        for block in blocks:
            block_start = parse_datetime(block["start"], timezone.utc)
            block_end = parse_datetime(block["end"], timezone.utc)
            if block_start is None or block_end is None:
                continue
            if block_start <= now_utc < block_end:
                current = block
            elif block_start > now_utc and next_block is None:
                next_block = block

        nudge = {"should_nudge": False}
        if current and current["state"] not in {"in_progress", "completed"}:
            start_dt = parse_datetime(current["start"], timezone.utc)
            grace = int(
                self.store.get_preference("nudge_grace_minutes", self.settings.nudge_grace_minutes)
            )
            latest = self.store.latest_feedback_for_block(current["id"])
            if start_dt and now_utc >= start_dt + timedelta(minutes=grace) and latest is None:
                nudge = {
                    "should_nudge": True,
                    "type": "start_check",
                    "block_id": current["id"],
                    "task_id": current["task_id"],
                    "message": f"The block '{current['task_title']}' started {grace}+ minutes ago. Ask whether it was started, snoozed, or should be replanned.",
                }

        return self._ok(
            {
                "range": mode,
                "timezone": self.timezone_name(),
                "start": start.isoformat(),
                "end": end.isoformat(),
                "plan": (
                    {"id": effective_plan["id"], "state": effective_plan["state"]}
                    if effective_plan
                    else None
                ),
                "current_block": current,
                "next_block": next_block,
                "blocks": blocks,
                "overdue_tasks": overdue,
                "at_risk_tasks": at_risk,
                "nudge": nudge,
                "counts": self.store.counts(),
            }
        )

    def handle_health(self, args: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._ok(
            {
                "status": "healthy",
                "database": str(self.store.path),
                "timezone": self.timezone_name(),
                "solver": "cp-sat" if self.scheduler.ortools_available() else "deterministic-greedy",
                "counts": self.store.counts(),
                "autonomy_mode": self.store.get_preference("autonomy_mode", "propose"),
            }
        )

    def compact_context(self, max_tasks: int = 8) -> str:
        tasks = self.store.list_tasks(statuses=["active"], limit=max_tasks)
        try:
            plan = self.store.get_plan(state="committed")
            now = utc_now()
            next_blocks = [
                block
                for block in plan["blocks"]
                if block["state"] not in {"completed", "cancelled", "skipped"}
                and (parse_datetime(block["end"], timezone.utc) or now) > now
            ][:5]
        except KeyError:
            plan = None
            next_blocks = []
        lines = [
            f"Timezone: {self.timezone_name()}",
            f"Autonomy: {self.store.get_preference('autonomy_mode', 'propose')}",
            "Active tasks:",
        ]
        if tasks:
            for task in tasks:
                deadline = task.deadline.isoformat() if task.deadline else "none"
                lines.append(
                    f"- {task.id}: {task.title} | remaining={task.remaining_minutes}m | priority={task.priority} | deadline={deadline}"
                )
        else:
            lines.append("- none")
        lines.append("Upcoming committed blocks:")
        if next_blocks:
            for block in next_blocks:
                lines.append(
                    f"- {block['start']}–{block['end']} {block['task_title']} (block {block['id']})"
                )
        else:
            lines.append("- none")
        return "\n".join(lines)


def json_handler(method):
    """Convert a service method into the Hermes handler contract."""

    def wrapped(args: dict[str, Any], **kwargs: Any) -> str:
        try:
            result = method(args or {})
            return json.dumps(result, ensure_ascii=False, separators=(",", ":"))
        except (ValueError, KeyError) as exc:
            return json.dumps(
                {"ok": False, "error": {"type": type(exc).__name__, "message": str(exc)}},
                ensure_ascii=False,
                separators=(",", ":"),
            )
        except Exception as exc:  # Plugin tools must never break Hermes' loop.
            return json.dumps(
                {
                    "ok": False,
                    "error": {
                        "type": type(exc).__name__,
                        "message": str(exc),
                        "recoverable": True,
                    },
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )

    return wrapped
