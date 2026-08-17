"""Domain models for the Hermes AI Reminder plugin.

The plugin deliberately uses standard-library dataclasses instead of an ORM or
validation framework.  This keeps a directory-installed Hermes plugin usable in
an otherwise unmodified Hermes environment.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class TaskRecord:
    id: str
    title: str
    notes: str
    status: str
    priority: int
    estimate_minutes: int
    remaining_minutes: int
    deadline: datetime | None
    earliest_start: datetime | None
    energy: str
    cognitive_load: float
    splittable: bool
    min_block_minutes: int
    max_block_minutes: int
    context: str
    source: str
    external_id: str | None
    created_at: datetime
    updated_at: datetime
    dependencies: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("deadline", "earliest_start", "created_at", "updated_at"):
            value = data[key]
            data[key] = value.isoformat() if value is not None else None
        return data


@dataclass(slots=True, frozen=True)
class Interval:
    start: datetime
    end: datetime
    label: str = ""
    external_id: str | None = None

    @property
    def minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)

    def to_dict(self) -> dict[str, Any]:
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "label": self.label,
            "external_id": self.external_id,
        }


@dataclass(slots=True)
class PlanBlock:
    task_id: str
    task_title: str
    start: datetime
    end: datetime
    piece_index: int
    piece_count: int
    context: str
    energy: str
    score: float
    rationale: list[str]
    locked: bool = False
    id: str | None = None
    plan_id: str | None = None
    state: str = "planned"
    calendar_event_id: str | None = None
    calendar_signature: str | None = None
    source_block_id: str | None = None

    @property
    def duration_minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "task_id": self.task_id,
            "task_title": self.task_title,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "duration_minutes": self.duration_minutes,
            "piece_index": self.piece_index,
            "piece_count": self.piece_count,
            "context": self.context,
            "energy": self.energy,
            "score": round(self.score, 3),
            "rationale": list(self.rationale),
            "locked": self.locked,
            "state": self.state,
            "calendar_event_id": self.calendar_event_id,
            "calendar_signature": self.calendar_signature,
            "source_block_id": self.source_block_id,
        }


@dataclass(slots=True)
class ScheduleResult:
    blocks: list[PlanBlock]
    unscheduled: list[dict[str, Any]]
    backend: str
    objective_score: float
    diagnostics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "blocks": [block.to_dict() for block in self.blocks],
            "unscheduled": self.unscheduled,
            "backend": self.backend,
            "objective_score": round(self.objective_score, 3),
            "diagnostics": self.diagnostics,
        }
