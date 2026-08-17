"""Run a small deterministic acceptance benchmark without external services."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from hermes_ai_reminder.evaluation import evaluate_schedule
from hermes_ai_reminder.models import Interval, TaskRecord
from hermes_ai_reminder.scheduler import ConstraintScheduler, SchedulerInput


def make_task(task_id: str, title: str, minutes: int, **overrides):
    now = datetime(2026, 8, 17, tzinfo=timezone.utc)
    values = {
        "id": task_id,
        "title": title,
        "notes": "",
        "status": "active",
        "priority": 3,
        "estimate_minutes": minutes,
        "remaining_minutes": minutes,
        "deadline": None,
        "earliest_start": None,
        "energy": "medium",
        "cognitive_load": 0.5,
        "splittable": True,
        "min_block_minutes": 30,
        "max_block_minutes": 90,
        "context": "general",
        "source": "benchmark",
        "external_id": None,
        "created_at": now,
        "updated_at": now,
        "dependencies": [],
    }
    values.update(overrides)
    return TaskRecord(**values)


def main() -> None:
    start = datetime(2026, 8, 17, 9, tzinfo=timezone.utc)
    scenarios = [
        SchedulerInput(
            tasks=[
                make_task(
                    "experiment",
                    "Run experiment",
                    90,
                    priority=5,
                    deadline=start + timedelta(hours=5),
                    energy="high",
                    context="lab",
                ),
                make_task(
                    "write",
                    "Write result",
                    120,
                    priority=4,
                    dependencies=["experiment"],
                    context="writing",
                ),
                make_task("admin", "Clear admin", 45, energy="low", context="admin"),
            ],
            window_start=start,
            window_end=start + timedelta(hours=8),
            availability=[Interval(start, start + timedelta(hours=8))],
            busy=[Interval(start + timedelta(hours=2), start + timedelta(hours=3), "meeting")],
            energy_profile={str(hour): (0.9 if 9 <= hour < 12 else 0.55) for hour in range(24)},
            slot_minutes=15,
        ),
        SchedulerInput(
            tasks=[make_task("capacity", "Over capacity", 300, priority=5)],
            window_start=start,
            window_end=start + timedelta(hours=2),
            availability=[Interval(start, start + timedelta(hours=2))],
            busy=[],
            energy_profile={str(hour): 0.5 for hour in range(24)},
            slot_minutes=15,
        ),
    ]

    scheduler = ConstraintScheduler(prefer_ortools=True)
    reports = []
    for index, scenario in enumerate(scenarios, start=1):
        result = scheduler.schedule(scenario)
        reports.append({"scenario": index, **evaluate_schedule(scenario, result)})
    payload = {
        "accepted": all(report["hard_constraint_violations"] == 0 for report in reports),
        "reports": reports,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if not payload["accepted"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
