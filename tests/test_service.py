from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest


def test_full_capture_plan_commit_feedback_loop(service):
    start = datetime(2026, 8, 17, 9, tzinfo=timezone.utc)
    created = service.handle_task(
        {
            "action": "create",
            "title": "Write rebuttal",
            "estimate_minutes": 120,
            "priority": 5,
            "deadline": (start + timedelta(days=1)).isoformat(),
            "energy": "high",
            "context": "writing",
        }
    )
    task_id = created["data"]["id"]

    draft = service.handle_plan(
        {
            "action": "generate",
            "window_start": start.isoformat(),
            "window_end": (start + timedelta(hours=8)).isoformat(),
            "availability": [{"start": start.isoformat(), "end": (start + timedelta(hours=8)).isoformat()}],
            "busy_blocks": [
                {
                    "start": (start + timedelta(hours=2)).isoformat(),
                    "end": (start + timedelta(hours=3)).isoformat(),
                    "label": "meeting",
                }
            ],
        }
    )
    assert draft["ok"] is True
    assert draft["requires_confirmation"] is True
    assert draft["calendar_actions"]
    plan_id = draft["data"]["id"]

    committed = service.handle_plan({"action": "commit", "plan_id": plan_id})
    block = committed["data"]["blocks"][0]
    service.handle_plan(
        {"action": "link_calendar", "block_id": block["id"], "calendar_event_id": "evt-1"}
    )
    feedback = service.handle_feedback(
        {
            "action": "record",
            "block_id": block["id"],
            "outcome": "completed",
            "actual_minutes": block["duration_minutes"],
        }
    )
    assert feedback["ok"] is True
    assert feedback["data"]["task"]["remaining_minutes"] < 120
    assert service.handle_task({"action": "get", "task_id": task_id})["ok"] is True


def test_preferences_and_brief_nudge(service):
    service.handle_preferences({"action": "set", "key": "nudge_grace_minutes", "value": 5})
    start = datetime(2026, 8, 17, 9, tzinfo=timezone.utc)
    service.handle_task(
        {"action": "create", "title": "Review", "estimate_minutes": 30, "priority": 4}
    )
    plan = service.handle_plan(
        {
            "action": "generate",
            "window_start": start.isoformat(),
            "window_end": (start + timedelta(hours=2)).isoformat(),
            "availability": [{"start": start.isoformat(), "end": (start + timedelta(hours=2)).isoformat()}],
        }
    )["data"]
    service.handle_plan({"action": "commit", "plan_id": plan["id"]})
    brief = service.handle_brief(
        {"range": "today", "now": (start + timedelta(minutes=10)).isoformat()}
    )
    assert brief["data"]["nudge"]["should_nudge"] is True


def test_replan_preserves_locked_block(service):
    start = datetime(2026, 8, 17, 9, tzinfo=timezone.utc)
    service.handle_task({"action": "create", "title": "A", "estimate_minutes": 60})
    service.handle_task({"action": "create", "title": "B", "estimate_minutes": 60})
    first = service.handle_plan(
        {
            "action": "generate",
            "window_start": start.isoformat(),
            "window_end": (start + timedelta(hours=4)).isoformat(),
            "availability": [{"start": start.isoformat(), "end": (start + timedelta(hours=4)).isoformat()}],
        }
    )["data"]
    committed = service.handle_plan({"action": "commit", "plan_id": first["id"]})["data"]
    locked = committed["blocks"][0]
    service.handle_plan(
        {
            "action": "link_calendar",
            "block_id": locked["id"],
            "calendar_event_id": "existing-event",
        }
    )
    service.handle_plan({"action": "lock_block", "block_id": locked["id"], "locked": True})

    response = service.handle_plan(
        {
            "action": "replan",
            "plan_id": first["id"],
            "window_start": start.isoformat(),
            "window_end": (start + timedelta(hours=4)).isoformat(),
            "availability": [{"start": start.isoformat(), "end": (start + timedelta(hours=4)).isoformat()}],
        }
    )
    replanned = response["data"]
    preserved = replanned["details"]["preserved_blocks"]
    assert any(block["id"] == locked["id"] for block in preserved)
    copied = next(block for block in replanned["blocks"] if block["source_block_id"] == locked["id"])
    assert copied["calendar_event_id"] == "existing-event"
    assert copied["locked"] is True
    assert all(
        action["link_after_create"]["block_id"] != copied["id"]
        for action in response["calendar_actions"]
    )


def test_include_task_ids_expands_dependency_closure(service):
    start = datetime(2026, 8, 17, 9, tzinfo=timezone.utc)
    first = service.handle_task(
        {"action": "create", "title": "Experiment", "estimate_minutes": 30}
    )["data"]
    second = service.handle_task(
        {
            "action": "create",
            "title": "Write result",
            "estimate_minutes": 30,
            "dependencies": [first["id"]],
        }
    )["data"]
    plan = service.handle_plan(
        {
            "action": "generate",
            "include_task_ids": [second["id"]],
            "window_start": start.isoformat(),
            "window_end": (start + timedelta(hours=2)).isoformat(),
            "availability": [
                {"start": start.isoformat(), "end": (start + timedelta(hours=2)).isoformat()}
            ],
        }
    )["data"]
    assert {block["task_id"] for block in plan["blocks"]} == {first["id"], second["id"]}


def test_brief_prefers_committed_plan_over_newer_draft(service):
    start = datetime(2026, 8, 17, 9, tzinfo=timezone.utc)
    service.handle_task({"action": "create", "title": "Focus", "estimate_minutes": 30})
    committed = service.handle_plan(
        {
            "action": "generate",
            "window_start": start.isoformat(),
            "window_end": (start + timedelta(hours=2)).isoformat(),
            "availability": [
                {"start": start.isoformat(), "end": (start + timedelta(hours=2)).isoformat()}
            ],
        }
    )["data"]
    service.handle_plan(
        {
            "action": "generate",
            "window_start": start.isoformat(),
            "window_end": (start + timedelta(hours=2)).isoformat(),
            "availability": [
                {"start": start.isoformat(), "end": (start + timedelta(hours=2)).isoformat()}
            ],
        }
    )
    service.handle_plan({"action": "commit", "plan_id": committed["id"]})
    brief = service.handle_brief({"range": "today", "now": start.isoformat()})["data"]
    assert brief["plan"] == {"id": committed["id"], "state": "committed"}
    assert len(brief["blocks"]) == len(committed["blocks"])


def test_preference_validation_and_overrun_does_not_invent_remaining_work(service):
    with pytest.raises(ValueError, match="slot_minutes"):
        service.handle_preferences({"action": "set", "key": "slot_minutes", "value": 17})
    overnight = service.handle_preferences(
        {
            "action": "set",
            "key": "work_windows",
            "value": {"0": [["22:00", "02:00"]]},
        }
    )
    assert overnight["data"]["work_windows"]["0"] == [["22:00", "02:00"]]
    task = service.handle_task(
        {"action": "create", "title": "Estimate", "estimate_minutes": 60}
    )["data"]
    service.handle_feedback(
        {
            "action": "record",
            "task_id": task["id"],
            "outcome": "overrun",
            "actual_minutes": 90,
        }
    )
    current = service.handle_task({"action": "get", "task_id": task["id"]})["data"]
    assert current["remaining_minutes"] == 60


def test_replan_reuses_event_id_and_acknowledges_update(service):
    start = datetime(2026, 8, 17, 9, tzinfo=timezone.utc)
    service.handle_task({"action": "create", "title": "Move me", "estimate_minutes": 60})
    initial = service.handle_plan(
        {
            "action": "generate",
            "window_start": start.isoformat(),
            "window_end": (start + timedelta(hours=4)).isoformat(),
            "availability": [
                {"start": start.isoformat(), "end": (start + timedelta(hours=4)).isoformat()}
            ],
        }
    )["data"]
    committed = service.handle_plan({"action": "commit", "plan_id": initial["id"]})["data"]
    old = committed["blocks"][0]
    service.handle_plan(
        {"action": "link_calendar", "block_id": old["id"], "calendar_event_id": "event-1"}
    )

    response = service.handle_plan(
        {
            "action": "replan",
            "plan_id": committed["id"],
            "window_start": start.isoformat(),
            "window_end": (start + timedelta(hours=4)).isoformat(),
            "availability": [
                {"start": start.isoformat(), "end": (start + timedelta(hours=4)).isoformat()}
            ],
            "busy_blocks": [{"start": old["start"], "end": old["end"], "label": "new meeting"}],
        }
    )
    updates = [action for action in response["calendar_actions"] if action["action"] == "update"]
    assert len(updates) == 1
    assert updates[0]["event_id"] == "event-1"
    moved = next(block for block in response["data"]["blocks"] if block["calendar_event_id"])
    assert moved["source_block_id"] == old["id"]
    assert (moved["start"], moved["end"]) != (old["start"], old["end"])

    service.handle_plan(
        {"action": "link_calendar", "block_id": moved["id"], "calendar_event_id": "event-1"}
    )
    refreshed = service.handle_plan({"action": "get", "plan_id": response["data"]["id"]})
    assert not [action for action in refreshed["calendar_actions"] if action["action"] == "update"]


def test_replan_delete_is_acknowledgeable(service):
    start = datetime(2026, 8, 17, 9, tzinfo=timezone.utc)
    service.handle_task({"action": "create", "title": "Remove me", "estimate_minutes": 60})
    initial = service.handle_plan(
        {
            "action": "generate",
            "window_start": start.isoformat(),
            "window_end": (start + timedelta(hours=2)).isoformat(),
            "availability": [
                {"start": start.isoformat(), "end": (start + timedelta(hours=2)).isoformat()}
            ],
        }
    )["data"]
    committed = service.handle_plan({"action": "commit", "plan_id": initial["id"]})["data"]
    old = committed["blocks"][0]
    service.handle_plan(
        {"action": "link_calendar", "block_id": old["id"], "calendar_event_id": "event-delete"}
    )
    replanned = service.handle_plan(
        {
            "action": "replan",
            "plan_id": committed["id"],
            "window_start": start.isoformat(),
            "window_end": (start + timedelta(hours=2)).isoformat(),
            "availability": [],
        }
    )
    deletes = [action for action in replanned["calendar_actions"] if action["action"] == "delete"]
    assert deletes == [
        {
            "action": "delete",
            "event_id": "event-delete",
            "summary": "[Focus] Remove me",
            "source_block_id": old["id"],
            "requires_confirmation": True,
        }
    ]
    service.handle_plan({"action": "unlink_calendar", "block_id": old["id"]})
    refreshed = service.handle_plan({"action": "get", "plan_id": replanned["data"]["id"]})
    assert not [action for action in refreshed["calendar_actions"] if action["action"] == "delete"]


def test_generate_rejects_overlapping_committed_plan(service):
    start = datetime(2026, 8, 17, 9, tzinfo=timezone.utc)
    service.handle_task({"action": "create", "title": "One plan", "estimate_minutes": 30})
    plan = service.handle_plan(
        {
            "action": "generate",
            "window_start": start.isoformat(),
            "window_end": (start + timedelta(hours=2)).isoformat(),
            "availability": [
                {"start": start.isoformat(), "end": (start + timedelta(hours=2)).isoformat()}
            ],
        }
    )["data"]
    service.handle_plan({"action": "commit", "plan_id": plan["id"]})
    with pytest.raises(ValueError, match="action='replan'"):
        service.handle_plan(
            {
                "action": "generate",
                "window_start": start.isoformat(),
                "window_end": (start + timedelta(hours=2)).isoformat(),
                "availability": [
                    {"start": start.isoformat(), "end": (start + timedelta(hours=2)).isoformat()}
                ],
            }
        )
