"""Deterministic quality metrics for schedule regression testing.

The benchmark deliberately measures properties a persuasive LLM response cannot
fake: hard-constraint violations, requested-work coverage, and fragmentation.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .models import ScheduleResult
from .scheduler import SchedulerInput


def evaluate_schedule(request: SchedulerInput, result: ScheduleResult) -> dict[str, Any]:
    tasks = {task.id: task for task in request.tasks}
    blocks = sorted(result.blocks, key=lambda block: (block.start, block.end, block.task_id))
    violations: list[dict[str, Any]] = []

    for left, right in zip(blocks, blocks[1:], strict=False):
        if left.end > right.start:
            violations.append(
                {"type": "overlap", "left": left.task_id, "right": right.task_id}
            )

    for block in blocks:
        task = tasks[block.task_id]
        if not any(block.start >= item.start and block.end <= item.end for item in request.availability):
            violations.append({"type": "outside_availability", "task_id": block.task_id})
        if any(block.start < item.end and block.end > item.start for item in request.busy):
            violations.append({"type": "busy_overlap", "task_id": block.task_id})
        if task.deadline and block.end > task.deadline:
            violations.append({"type": "deadline", "task_id": block.task_id})
        if task.earliest_start and block.start < task.earliest_start:
            violations.append({"type": "earliest_start", "task_id": block.task_id})

    by_task: dict[str, list[Any]] = defaultdict(list)
    for block in blocks:
        by_task[block.task_id].append(block)
    completed_ids = {task.id for task in request.tasks if task.status == "completed"}
    for task_id, task_blocks in by_task.items():
        task = tasks[task_id]
        for dependency in task.dependencies:
            if dependency in completed_ids:
                continue
            dependency_blocks = by_task.get(dependency, [])
            if not dependency_blocks or min(block.start for block in task_blocks) < max(
                block.end for block in dependency_blocks
            ):
                violations.append(
                    {
                        "type": "dependency",
                        "task_id": task_id,
                        "dependency": dependency,
                    }
                )

    requested_minutes = sum(
        task.remaining_minutes
        for task in request.tasks
        if task.status == "active" and task.remaining_minutes > 0
    )
    scheduled_minutes = sum(block.duration_minutes for block in blocks)
    contexts = [block.context for block in blocks]
    context_switches = sum(left != right for left, right in zip(contexts, contexts[1:], strict=False))
    scheduled_task_count = len(by_task)

    return {
        "hard_constraint_violations": len(violations),
        "violations": violations,
        "requested_minutes": requested_minutes,
        "scheduled_minutes": scheduled_minutes,
        "coverage": (
            min(1.0, scheduled_minutes / requested_minutes) if requested_minutes else 1.0
        ),
        "scheduled_tasks": scheduled_task_count,
        "unscheduled_tasks": len(result.unscheduled),
        "block_count": len(blocks),
        "context_switches": context_switches,
        "fragmentation_per_scheduled_task": (
            len(blocks) / scheduled_task_count if scheduled_task_count else 0.0
        ),
        "backend": result.backend,
    }
