"""Standalone demonstration of the domain engine without Hermes."""

from __future__ import annotations

import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from hermes_ai_reminder.service import AiReminderService, ServiceSettings


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        service = AiReminderService(
            Path(tmp) / "secretary.db",
            ServiceSettings(timezone="UTC", slot_minutes=15),
        )
        first = service.handle_task(
            {
                "action": "create",
                "title": "Draft rebuttal",
                "estimate_minutes": 180,
                "priority": 5,
                "deadline": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
                "energy": "high",
                "context": "writing",
            }
        )["data"]
        service.handle_task(
            {
                "action": "create",
                "title": "Process email backlog",
                "estimate_minutes": 45,
                "priority": 2,
                "energy": "low",
                "context": "admin",
            }
        )
        start = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0)
        result = service.handle_plan(
            {
                "action": "generate",
                "window_start": start.isoformat(),
                "window_end": (start + timedelta(days=1)).isoformat(),
                "availability": [
                    {"start": start.isoformat(), "end": (start + timedelta(hours=8)).isoformat()}
                ],
                "busy_blocks": [
                    {
                        "start": (start + timedelta(hours=2)).isoformat(),
                        "end": (start + timedelta(hours=3)).isoformat(),
                        "label": "Fixed meeting",
                    }
                ],
            }
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"Created task: {first['id']}")


if __name__ == "__main__":
    main()
