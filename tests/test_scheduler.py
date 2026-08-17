from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from hermes_ai_reminder.models import Interval, TaskRecord
from hermes_ai_reminder.scheduler import ConstraintScheduler, SchedulerInput


def task(
    task_id: str,
    title: str,
    minutes: int,
    *,
    priority: int = 3,
    deadline=None,
    dependencies=None,
    splittable=True,
    min_block=30,
    max_block=90,
    energy="medium",
    context="general",
):
    now = datetime(2026, 8, 1, tzinfo=timezone.utc)
    return TaskRecord(
        id=task_id,
        title=title,
        notes="",
        status="active",
        priority=priority,
        estimate_minutes=minutes,
        remaining_minutes=minutes,
        deadline=deadline,
        earliest_start=None,
        energy=energy,
        cognitive_load=0.5,
        splittable=splittable,
        min_block_minutes=min_block,
        max_block_minutes=max_block,
        context=context,
        source="test",
        external_id=None,
        created_at=now,
        updated_at=now,
        dependencies=dependencies or [],
    )


def base_request(tasks):
    start = datetime(2026, 8, 17, 9, tzinfo=timezone.utc)
    end = start + timedelta(hours=8)
    return SchedulerInput(
        tasks=tasks,
        window_start=start,
        window_end=end,
        availability=[Interval(start, end)],
        busy=[Interval(start + timedelta(hours=2), start + timedelta(hours=3), "meeting")],
        energy_profile={str(hour): 0.8 for hour in range(24)},
        slot_minutes=15,
    )


def assert_no_overlap(blocks):
    ordered = sorted(blocks, key=lambda block: block.start)
    for left, right in zip(ordered, ordered[1:], strict=False):
        assert left.end <= right.start


def test_greedy_enforces_busy_deadline_and_dependencies():
    start = datetime(2026, 8, 17, 9, tzinfo=timezone.utc)
    first = task("a", "Experiment", 60, priority=5, deadline=start + timedelta(hours=5))
    second = task("b", "Write", 60, dependencies=["a"], priority=4)
    result = ConstraintScheduler(prefer_ortools=False).schedule(base_request([first, second]))

    assert not result.unscheduled
    assert_no_overlap(result.blocks)
    for block in result.blocks:
        assert not (
            block.start < start + timedelta(hours=3)
            and block.end > start + timedelta(hours=2)
        )
    first_end = max(block.end for block in result.blocks if block.task_id == "a")
    second_start = min(block.start for block in result.blocks if block.task_id == "b")
    assert second_start >= first_end
    assert first_end <= first.deadline


def test_split_task_is_complete_and_ordered():
    work = task("split", "Long writing", 180, max_block=90, min_block=45, context="writing")
    result = ConstraintScheduler(prefer_ortools=False).schedule(base_request([work]))
    blocks = [block for block in result.blocks if block.task_id == "split"]
    assert len(blocks) == 2
    assert sum(block.duration_minutes for block in blocks) == 180
    assert blocks[0].end <= blocks[1].start


def test_insufficient_capacity_is_explicit():
    start = datetime(2026, 8, 17, 9, tzinfo=timezone.utc)
    request = SchedulerInput(
        tasks=[task("x", "Impossible", 240, splittable=False, max_block=240)],
        window_start=start,
        window_end=start + timedelta(hours=2),
        availability=[Interval(start, start + timedelta(hours=2))],
        busy=[],
        energy_profile={str(hour): 0.5 for hour in range(24)},
        slot_minutes=15,
    )
    result = ConstraintScheduler(prefer_ortools=False).schedule(request)
    assert result.blocks == []
    assert result.unscheduled[0]["reason"] in {"no_candidate_window", "greedy_capacity"}


def test_impossible_split_envelope_is_rejected():
    # 100 minutes cannot be represented using 60-70 minute blocks.
    work = task("split", "Impossible split", 100, min_block=60, max_block=70)
    result = ConstraintScheduler(prefer_ortools=False).schedule(base_request([work]))
    assert result.blocks == []
    assert result.unscheduled[0]["reason"] == "invalid_duration"


def test_greedy_rolls_back_partial_multiblock_allocation():
    start = datetime(2026, 8, 17, 9, tzinfo=timezone.utc)
    large = task("large", "Large", 120, priority=5, min_block=60, max_block=60)
    small = task("small", "Small", 60, priority=1, splittable=False, max_block=60)
    request = SchedulerInput(
        tasks=[large, small],
        window_start=start,
        window_end=start + timedelta(hours=1),
        availability=[Interval(start, start + timedelta(hours=1))],
        busy=[],
        energy_profile={str(hour): 0.5 for hour in range(24)},
        slot_minutes=15,
    )
    result = ConstraintScheduler(prefer_ortools=False).schedule(request)
    assert [block.task_id for block in result.blocks] == ["small"]
    assert any(item["task_id"] == "large" for item in result.unscheduled)


@pytest.mark.solver
def test_cp_sat_backend_when_installed():
    if not ConstraintScheduler.ortools_available():
        pytest.skip("OR-Tools not installed")
    result = ConstraintScheduler(prefer_ortools=True).schedule(
        base_request([task("a", "A", 60), task("b", "B", 60)])
    )
    assert result.backend == "cp-sat"
    assert_no_overlap(result.blocks)
