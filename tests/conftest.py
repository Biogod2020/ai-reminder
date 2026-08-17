from __future__ import annotations

import pytest

from hermes_ai_reminder.service import AiReminderService, ServiceSettings


@pytest.fixture
def service(tmp_path):
    return AiReminderService(
        tmp_path / "secretary.db",
        ServiceSettings(timezone="UTC", slot_minutes=15, planning_horizon_days=7),
    )
