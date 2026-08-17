"""Deterministic constraint scheduler with an optional OR-Tools CP-SAT backend.

The LLM interprets intent; this module owns arithmetic and feasibility.  The
fallback solver is intentionally dependency-free and deterministic.  If
``ortools`` is installed, CP-SAT searches the same candidate space globally.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Iterable

from .models import Interval, PlanBlock, ScheduleResult, TaskRecord
from .time_utils import ceil_datetime, floor_datetime, merge_intervals


ENERGY_TARGET = {"low": 0.28, "medium": 0.58, "high": 0.88}


@dataclass(slots=True, frozen=True)
class Piece:
    task_id: str
    index: int
    count: int
    duration_slots: int

    @property
    def key(self) -> str:
        return f"{self.task_id}:{self.index}"


@dataclass(slots=True, frozen=True)
class Candidate:
    piece_key: str
    task_id: str
    piece_index: int
    start_slot: int
    end_slot: int
    cover_end_slot: int
    score: float
    rationale: tuple[str, ...]


@dataclass(slots=True)
class SchedulerInput:
    tasks: list[TaskRecord]
    window_start: datetime
    window_end: datetime
    availability: list[Interval]
    busy: list[Interval]
    energy_profile: dict[str, float]
    slot_minutes: int = 15
    transition_buffer_minutes: int = 0
    max_candidates_per_piece: int = 400
    solver_seconds: float = 3.0


class ConstraintScheduler:
    def __init__(self, *, prefer_ortools: bool = True):
        self.prefer_ortools = prefer_ortools

    @staticmethod
    def ortools_available() -> bool:
        try:
            import ortools  # noqa: F401
        except Exception:
            return False
        return True

    def schedule(self, request: SchedulerInput) -> ScheduleResult:
        prepared = self._prepare(request)
        if not prepared["tasks"]:
            return ScheduleResult(
                blocks=[],
                unscheduled=prepared["unscheduled"],
                backend="none",
                objective_score=0.0,
                diagnostics=prepared["diagnostics"],
            )

        if self.prefer_ortools and self.ortools_available():
            try:
                selected, dropped, objective = self._solve_cp_sat(request, prepared)
                backend = "cp-sat"
            except Exception as exc:  # A solver failure must not break the secretary.
                prepared["diagnostics"]["cp_sat_error"] = f"{type(exc).__name__}: {exc}"
                selected, dropped, objective = self._solve_greedy(request, prepared)
                backend = "greedy-fallback"
        else:
            selected, dropped, objective = self._solve_greedy(request, prepared)
            backend = "greedy"

        blocks = self._materialize_blocks(request, prepared, selected)
        unscheduled = prepared["unscheduled"] + dropped
        diagnostics = dict(prepared["diagnostics"])
        diagnostics.update(
            {
                "selected_blocks": len(blocks),
                "scheduled_tasks": len({block.task_id for block in blocks}),
                "backend": backend,
            }
        )
        return ScheduleResult(
            blocks=blocks,
            unscheduled=unscheduled,
            backend=backend,
            objective_score=objective,
            diagnostics=diagnostics,
        )

    def _prepare(self, request: SchedulerInput) -> dict[str, Any]:
        if request.slot_minutes not in {5, 10, 15, 20, 30, 60}:
            raise ValueError("slot_minutes must be one of 5, 10, 15, 20, 30, 60")
        window_start = ceil_datetime(request.window_start, request.slot_minutes)
        window_end = floor_datetime(request.window_end, request.slot_minutes)
        if window_end <= window_start:
            raise ValueError("Planning window is empty after slot alignment")
        horizon_minutes = int((window_end - window_start).total_seconds() // 60)
        if horizon_minutes > 21 * 24 * 60:
            raise ValueError("Planning horizon cannot exceed 21 days")
        slot_count = horizon_minutes // request.slot_minutes

        available = self._mask_intervals(
            window_start, slot_count, request.slot_minutes, merge_intervals(request.availability)
        )
        busy = self._mask_intervals(
            window_start, slot_count, request.slot_minutes, merge_intervals(request.busy), overlap=True
        )
        base_free = [a and not b for a, b in zip(available, busy, strict=True)]

        task_map = {task.id: task for task in request.tasks}
        completed = {task.id for task in request.tasks if task.status == "completed"}
        active_tasks = [task for task in request.tasks if task.status == "active" and task.remaining_minutes > 0]
        unscheduled: list[dict[str, Any]] = []
        usable_tasks: list[TaskRecord] = []
        pieces_by_task: dict[str, list[Piece]] = {}
        candidates_by_piece: dict[str, list[Candidate]] = {}

        for task in active_tasks:
            missing_dependencies = [
                dep for dep in task.dependencies if dep not in completed and dep not in task_map
            ]
            archived_dependencies = [
                dep
                for dep in task.dependencies
                if dep in task_map and task_map[dep].status == "archived"
            ]
            if missing_dependencies or archived_dependencies:
                unscheduled.append(
                    {
                        "task_id": task.id,
                        "title": task.title,
                        "reason": "dependency_unsatisfied",
                        "details": {
                            "missing": missing_dependencies,
                            "archived": archived_dependencies,
                        },
                    }
                )
                continue
            if task.deadline and task.deadline <= window_start:
                unscheduled.append(
                    {
                        "task_id": task.id,
                        "title": task.title,
                        "reason": "deadline_before_window",
                        "deadline": task.deadline.isoformat(),
                    }
                )
                continue
            pieces = self._split_task(task, request.slot_minutes)
            if not pieces:
                unscheduled.append(
                    {"task_id": task.id, "title": task.title, "reason": "invalid_duration"}
                )
                continue
            task_has_candidates = True
            for piece in pieces:
                candidates = self._candidate_intervals(
                    request=request,
                    task=task,
                    piece=piece,
                    base_free=base_free,
                    window_start=window_start,
                    window_end=window_end,
                    slot_count=slot_count,
                )
                candidates_by_piece[piece.key] = candidates
                if not candidates:
                    task_has_candidates = False
            if not task_has_candidates:
                unscheduled.append(
                    {
                        "task_id": task.id,
                        "title": task.title,
                        "reason": "no_candidate_window",
                    }
                )
                continue
            usable_tasks.append(task)
            pieces_by_task[task.id] = pieces

        return {
            "window_start": window_start,
            "window_end": window_end,
            "slot_count": slot_count,
            "base_free": base_free,
            "tasks": usable_tasks,
            "task_map": task_map,
            "completed": completed,
            "pieces_by_task": pieces_by_task,
            "candidates_by_piece": candidates_by_piece,
            "unscheduled": unscheduled,
            "diagnostics": {
                "slot_minutes": request.slot_minutes,
                "slot_count": slot_count,
                "free_minutes": sum(base_free) * request.slot_minutes,
                "candidate_count": sum(len(items) for items in candidates_by_piece.values()),
                "input_tasks": len(active_tasks),
                "eligible_tasks": len(usable_tasks),
            },
        }

    @staticmethod
    def _mask_intervals(
        window_start: datetime,
        slot_count: int,
        slot_minutes: int,
        intervals: Iterable[Interval],
        *,
        overlap: bool = False,
    ) -> list[bool]:
        mask = [False] * slot_count
        step = timedelta(minutes=slot_minutes)
        for slot in range(slot_count):
            start = window_start + slot * step
            end = start + step
            for interval in intervals:
                if overlap:
                    matches = start < interval.end and end > interval.start
                else:
                    matches = start >= interval.start and end <= interval.end
                if matches:
                    mask[slot] = True
                    break
        return mask

    @staticmethod
    def _split_task(task: TaskRecord, slot_minutes: int) -> list[Piece]:
        total_slots = max(1, math.ceil(task.remaining_minutes / slot_minutes))
        min_slots = max(1, math.ceil(task.min_block_minutes / slot_minutes))
        max_slots = max(min_slots, math.ceil(task.max_block_minutes / slot_minutes))
        if not task.splittable or total_slots <= max_slots:
            return [Piece(task.id, 0, 1, total_slots)]

        minimum_piece_count = math.ceil(total_slots / max_slots)
        maximum_piece_count = total_slots // min_slots
        if minimum_piece_count > maximum_piece_count:
            # The requested min/max block envelope cannot represent the duration.
            return []

        piece_count = minimum_piece_count
        base, remainder = divmod(total_slots, piece_count)
        sizes = [base + (1 if index < remainder else 0) for index in range(piece_count)]
        if any(size < min_slots or size > max_slots for size in sizes):
            return []
        return [Piece(task.id, index, piece_count, size) for index, size in enumerate(sizes)]

    def _candidate_intervals(
        self,
        *,
        request: SchedulerInput,
        task: TaskRecord,
        piece: Piece,
        base_free: list[bool],
        window_start: datetime,
        window_end: datetime,
        slot_count: int,
    ) -> list[Candidate]:
        step = timedelta(minutes=request.slot_minutes)
        earliest = max(window_start, task.earliest_start or window_start)
        deadline = min(window_end, task.deadline or window_end)
        buffer_slots = math.ceil(request.transition_buffer_minutes / request.slot_minutes)

        blocked_prefix = [0]
        for free in base_free:
            blocked_prefix.append(blocked_prefix[-1] + (0 if free else 1))

        candidates: list[Candidate] = []
        last_start = slot_count - piece.duration_slots
        for start_slot in range(max(0, last_start + 1)):
            end_slot = start_slot + piece.duration_slots
            cover_end = min(slot_count, end_slot + buffer_slots)
            start_at = window_start + start_slot * step
            end_at = window_start + end_slot * step
            if start_at < earliest or end_at > deadline:
                continue
            if blocked_prefix[end_slot] - blocked_prefix[start_slot] != 0:
                continue
            if buffer_slots and blocked_prefix[cover_end] - blocked_prefix[end_slot] != 0:
                continue
            score, rationale = self._candidate_score(
                task=task,
                start_at=start_at,
                end_at=end_at,
                window_start=window_start,
                window_end=window_end,
                energy_profile=request.energy_profile,
            )
            candidates.append(
                Candidate(
                    piece_key=piece.key,
                    task_id=task.id,
                    piece_index=piece.index,
                    start_slot=start_slot,
                    end_slot=end_slot,
                    cover_end_slot=cover_end,
                    score=score,
                    rationale=tuple(rationale),
                )
            )

        if len(candidates) <= request.max_candidates_per_piece:
            return candidates
        # Retain the best candidates plus a few chronological anchors so the
        # global solver still has options around dependencies and other tasks.
        ranked = sorted(candidates, key=lambda item: (-item.score, item.start_slot))
        keep = ranked[: max(1, request.max_candidates_per_piece - 20)]
        anchors = sorted(candidates, key=lambda item: item.start_slot)
        anchors = anchors[:10] + anchors[-10:]
        unique = {(item.start_slot, item.end_slot): item for item in keep + anchors}
        return sorted(unique.values(), key=lambda item: item.start_slot)

    @staticmethod
    def _candidate_score(
        *,
        task: TaskRecord,
        start_at: datetime,
        end_at: datetime,
        window_start: datetime,
        window_end: datetime,
        energy_profile: dict[str, float],
    ) -> tuple[float, list[str]]:
        midpoint = start_at + (end_at - start_at) / 2
        energy_score = float(energy_profile.get(str(midpoint.hour), 0.5))
        target = ENERGY_TARGET.get(task.energy, 0.58)
        alignment = max(0.0, 1.0 - abs(energy_score - target))
        horizon = max(1.0, (window_end - window_start).total_seconds())
        start_fraction = (start_at - window_start).total_seconds() / horizon

        if task.deadline:
            total_slack = max(1.0, (task.deadline - window_start).total_seconds())
            urgency = max(0.0, min(1.0, 1.0 - total_slack / (7 * 86400)))
        else:
            urgency = 0.15
        earliness = 1.0 - max(0.0, min(1.0, start_fraction))
        score = alignment * 110 + urgency * earliness * 90 + task.priority * 7
        score += task.cognitive_load * alignment * 20

        rationale = [f"energy alignment {alignment:.2f}", f"priority {task.priority}/5"]
        if task.deadline:
            rationale.append(f"before deadline {task.deadline.isoformat()}")
        if task.earliest_start:
            rationale.append(f"after earliest start {task.earliest_start.isoformat()}")
        return score, rationale

    @staticmethod
    def _task_reward(task: TaskRecord, window_start: datetime) -> int:
        if task.deadline:
            hours = max(0.0, (task.deadline - window_start).total_seconds() / 3600)
            urgency = max(0.0, min(1.0, 1.0 - hours / (7 * 24)))
        else:
            urgency = 0.1
        return int(task.priority * 10_000 + urgency * 8_000 + task.cognitive_load * 500)

    def _solve_cp_sat(
        self, request: SchedulerInput, prepared: dict[str, Any]
    ) -> tuple[list[Candidate], list[dict[str, Any]], float]:
        from ortools.sat.python import cp_model

        model = cp_model.CpModel()
        tasks: list[TaskRecord] = prepared["tasks"]
        pieces_by_task: dict[str, list[Piece]] = prepared["pieces_by_task"]
        candidates_by_piece: dict[str, list[Candidate]] = prepared["candidates_by_piece"]
        slot_count: int = prepared["slot_count"]

        active = {task.id: model.NewBoolVar(f"active_{task.id}") for task in tasks}
        candidate_vars: dict[tuple[str, int], Any] = {}
        start_expr: dict[str, Any] = {}
        end_expr: dict[str, Any] = {}
        objective_terms: list[Any] = []

        for task in tasks:
            pieces = pieces_by_task[task.id]
            for piece in pieces:
                variables = []
                candidates = candidates_by_piece[piece.key]
                for index, candidate in enumerate(candidates):
                    variable = model.NewBoolVar(f"x_{piece.key}_{index}")
                    candidate_vars[(piece.key, index)] = variable
                    variables.append(variable)
                    objective_terms.append(int(round(candidate.score * 10)) * variable)
                model.Add(sum(variables) == active[task.id])
                start_expr[piece.key] = sum(
                    candidates[index].start_slot * candidate_vars[(piece.key, index)]
                    for index in range(len(candidates))
                )
                end_expr[piece.key] = sum(
                    candidates[index].end_slot * candidate_vars[(piece.key, index)]
                    for index in range(len(candidates))
                )
            for previous, following in zip(pieces, pieces[1:], strict=False):
                model.Add(
                    start_expr[following.key]
                    >= end_expr[previous.key] - slot_count * (1 - active[task.id])
                )
            objective_terms.append(self._task_reward(task, prepared["window_start"]) * active[task.id])

        # One task/buffer coverage per free slot.
        coverage: list[list[Any]] = [[] for _ in range(slot_count)]
        for piece_key, candidates in candidates_by_piece.items():
            for index, candidate in enumerate(candidates):
                variable = candidate_vars[(piece_key, index)]
                for slot in range(candidate.start_slot, candidate.cover_end_slot):
                    coverage[slot].append(variable)
        for variables in coverage:
            if variables:
                model.Add(sum(variables) <= 1)

        task_by_id = {task.id: task for task in tasks}
        completed: set[str] = prepared["completed"]
        for task in tasks:
            for dependency in task.dependencies:
                if dependency in completed:
                    continue
                if dependency not in task_by_id:
                    model.Add(active[task.id] == 0)
                    continue
                model.Add(active[task.id] <= active[dependency])
                first = pieces_by_task[task.id][0]
                last_dependency = pieces_by_task[dependency][-1]
                model.Add(
                    start_expr[first.key]
                    >= end_expr[last_dependency.key] - slot_count * (1 - active[task.id])
                )

        model.Maximize(sum(objective_terms))
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = max(0.1, request.solver_seconds)
        solver.parameters.num_search_workers = 8
        solver.parameters.random_seed = 0
        status = solver.Solve(model)
        if status not in {cp_model.OPTIMAL, cp_model.FEASIBLE}:
            raise RuntimeError(f"CP-SAT returned status {solver.StatusName(status)}")

        selected: list[Candidate] = []
        dropped: list[dict[str, Any]] = []
        for task in tasks:
            if solver.Value(active[task.id]) != 1:
                dropped.append(
                    {"task_id": task.id, "title": task.title, "reason": "solver_capacity"}
                )
                continue
            for piece in pieces_by_task[task.id]:
                for index, candidate in enumerate(candidates_by_piece[piece.key]):
                    if solver.Value(candidate_vars[(piece.key, index)]) == 1:
                        selected.append(candidate)
                        break
        return selected, dropped, float(solver.ObjectiveValue()) / 10.0

    def _solve_greedy(
        self, request: SchedulerInput, prepared: dict[str, Any]
    ) -> tuple[list[Candidate], list[dict[str, Any]], float]:
        tasks: list[TaskRecord] = prepared["tasks"]
        task_by_id = {task.id: task for task in tasks}
        completed: set[str] = prepared["completed"]
        pieces_by_task: dict[str, list[Piece]] = prepared["pieces_by_task"]
        candidates_by_piece: dict[str, list[Candidate]] = prepared["candidates_by_piece"]
        occupied = [False] * prepared["slot_count"]
        selected: list[Candidate] = []
        selected_by_task: dict[str, list[Candidate]] = {}
        dropped: list[dict[str, Any]] = []

        pending = {task.id for task in tasks}
        ordered: list[TaskRecord] = []
        while pending:
            ready = [
                task_by_id[task_id]
                for task_id in pending
                if all(dep in completed or dep not in pending for dep in task_by_id[task_id].dependencies)
            ]
            if not ready:
                for task_id in sorted(pending):
                    task = task_by_id[task_id]
                    dropped.append(
                        {"task_id": task.id, "title": task.title, "reason": "dependency_cycle"}
                    )
                pending.clear()
                break
            ready.sort(
                key=lambda task: (
                    -self._task_reward(task, prepared["window_start"]),
                    task.deadline or prepared["window_end"],
                    task.id,
                )
            )
            chosen = ready[0]
            ordered.append(chosen)
            pending.remove(chosen.id)

        for task in ordered:
            unsatisfied = [
                dep
                for dep in task.dependencies
                if dep not in completed and dep not in selected_by_task
            ]
            if unsatisfied:
                dropped.append(
                    {
                        "task_id": task.id,
                        "title": task.title,
                        "reason": "dependency_not_scheduled",
                        "dependencies": unsatisfied,
                    }
                )
                continue
            dependency_end = 0
            for dependency in task.dependencies:
                if dependency in selected_by_task:
                    dependency_end = max(
                        dependency_end,
                        max(item.end_slot for item in selected_by_task[dependency]),
                    )

            chosen_for_task: list[Candidate] = []
            failed = False
            previous_end = dependency_end
            for piece in pieces_by_task[task.id]:
                viable: list[tuple[float, Candidate]] = []
                for candidate in candidates_by_piece[piece.key]:
                    if candidate.start_slot < previous_end:
                        continue
                    if any(occupied[slot] for slot in range(candidate.start_slot, candidate.cover_end_slot)):
                        continue
                    neighbor_bonus = 0.0
                    for other_task_id, other_candidates in selected_by_task.items():
                        other_context = task_by_id[other_task_id].context
                        if other_context != task.context:
                            continue
                        for other in other_candidates:
                            if other.end_slot == candidate.start_slot or candidate.end_slot == other.start_slot:
                                neighbor_bonus = max(neighbor_bonus, 18.0)
                    viable.append((candidate.score + neighbor_bonus, candidate))
                if not viable:
                    failed = True
                    break
                viable.sort(key=lambda item: (-item[0], item[1].start_slot))
                candidate = viable[0][1]
                chosen_for_task.append(candidate)
                previous_end = candidate.end_slot
                for slot in range(candidate.start_slot, candidate.cover_end_slot):
                    occupied[slot] = True

            if failed or len(chosen_for_task) != len(pieces_by_task[task.id]):
                # Roll back partial allocation if a later piece could not fit.
                for candidate in chosen_for_task:
                    for slot in range(candidate.start_slot, candidate.cover_end_slot):
                        occupied[slot] = False
                dropped.append(
                    {"task_id": task.id, "title": task.title, "reason": "greedy_capacity"}
                )
                continue
            selected.extend(chosen_for_task)
            selected_by_task[task.id] = chosen_for_task

        objective = sum(item.score for item in selected) + sum(
            self._task_reward(task_by_id[task_id], prepared["window_start"]) / 10.0
            for task_id in selected_by_task
        )
        return selected, dropped, objective

    @staticmethod
    def _materialize_blocks(
        request: SchedulerInput, prepared: dict[str, Any], selected: list[Candidate]
    ) -> list[PlanBlock]:
        step = timedelta(minutes=request.slot_minutes)
        task_map = {task.id: task for task in prepared["tasks"]}
        pieces_by_task: dict[str, list[Piece]] = prepared["pieces_by_task"]
        blocks: list[PlanBlock] = []
        for candidate in selected:
            task = task_map[candidate.task_id]
            blocks.append(
                PlanBlock(
                    task_id=task.id,
                    task_title=task.title,
                    start=prepared["window_start"] + candidate.start_slot * step,
                    end=prepared["window_start"] + candidate.end_slot * step,
                    piece_index=candidate.piece_index,
                    piece_count=len(pieces_by_task[task.id]),
                    context=task.context,
                    energy=task.energy,
                    score=candidate.score,
                    rationale=list(candidate.rationale),
                )
            )
        blocks.sort(key=lambda item: (item.start, item.end, item.task_id))
        return blocks
