from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from hermes_ai_reminder.models import PlanBlock
from hermes_ai_reminder.store import SqliteStore


def test_task_crud_and_dependencies(tmp_path):
    store = SqliteStore(tmp_path / "state.db")
    parent = store.create_task(
        {
            "title": "Run experiment",
            "estimate_minutes": 60,
            "priority": 5,
            "deadline": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        }
    )
    child = store.create_task(
        {"title": "Write results", "estimate_minutes": 90, "context": "writing"},
        dependencies=[parent.id],
    )

    assert child.dependencies == [parent.id]
    updated = store.update_task(child.id, {"remaining_minutes": 45, "priority": 4})
    assert updated.remaining_minutes == 45
    assert updated.priority == 4
    assert {task.id for task in store.list_tasks(statuses=["active"])} == {parent.id, child.id}

    completed = store.update_task(parent.id, {"status": "completed", "remaining_minutes": 0})
    assert completed.status == "completed"


def test_task_validation_and_cycle_rejection(tmp_path):
    store = SqliteStore(tmp_path / "state.db")
    first = store.create_task({"title": "First", "estimate_minutes": 30})
    second = store.create_task(
        {"title": "Second", "estimate_minutes": 30}, dependencies=[first.id]
    )
    with pytest.raises(ValueError, match="cycle"):
        store.update_task(first.id, {}, dependencies=[second.id])
    with pytest.raises(ValueError, match="priority"):
        store.update_task(first.id, {"priority": 9})


def test_plan_version_and_calendar_link(tmp_path):
    store = SqliteStore(tmp_path / "state.db")
    task = store.create_task({"title": "Focus", "estimate_minutes": 30})
    start = datetime(2026, 8, 17, 9, tzinfo=timezone.utc)
    block = PlanBlock(
        task_id=task.id,
        task_title=task.title,
        start=start,
        end=start + timedelta(minutes=30),
        piece_index=0,
        piece_count=1,
        context="general",
        energy="medium",
        score=1.0,
        rationale=["test"],
    )
    plan = store.create_plan(
        window_start=start.isoformat(),
        window_end=(start + timedelta(days=1)).isoformat(),
        timezone_name="UTC",
        backend="greedy",
        objective_score=1.0,
        blocks=[block],
        details={},
    )
    committed = store.set_plan_state(plan["id"], "committed")
    assert committed["state"] == "committed"
    assert committed["blocks"][0]["state"] == "committed"

    linked = store.link_calendar_event(committed["blocks"][0]["id"], "gcal-123")
    assert linked["calendar_event_id"] == "gcal-123"
