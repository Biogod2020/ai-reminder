from __future__ import annotations

from datetime import datetime, timedelta, timezone

from hermes_ai_reminder.evaluation import evaluate_schedule
from hermes_ai_reminder.models import Interval
from hermes_ai_reminder.scheduler import ConstraintScheduler

from test_scheduler import base_request, task


def test_evaluation_reports_zero_hard_violations():
    start = datetime(2026, 8, 17, 9, tzinfo=timezone.utc)
    request = base_request(
        [
            task("a", "A", 60, deadline=start + timedelta(hours=5)),
            task("b", "B", 60, dependencies=["a"]),
        ]
    )
    result = ConstraintScheduler(prefer_ortools=False).schedule(request)
    metrics = evaluate_schedule(request, result)
    assert metrics["hard_constraint_violations"] == 0
    assert metrics["scheduled_minutes"] == 120
    assert metrics["coverage"] == 1.0
    assert all(isinstance(item, Interval) for item in request.availability)
