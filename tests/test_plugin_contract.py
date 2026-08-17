from __future__ import annotations

import json
from pathlib import Path

from hermes_ai_reminder.plugin import register


class FakeState:
    def __init__(self):
        self.values = {}

    def get(self, key, default=None):
        return self.values.get(key, default)

    def set(self, key, value):
        self.values[key] = value


class FakeContext:
    def __init__(self, tmp_path: Path):
        self.config = {"data_dir": str(tmp_path), "timezone": "UTC"}
        self.tools = {}
        self.hooks = {}
        self.skills = {}
        self.commands = {}
        self.state = FakeState()
        self.jobs = []

    def get_config(self, key, default=None):
        return self.config.get(key, default)

    def register_tool(self, *, name, toolset, schema, handler, **kwargs):
        self.tools[name] = {"toolset": toolset, "schema": schema, "handler": handler}

    def register_hook(self, name, callback):
        self.hooks[name] = callback

    def register_skill(self, name, path):
        self.skills[name] = Path(path)

    def register_command(self, name, handler, description="", args_hint=""):
        self.commands[name] = handler

    def dispatch_tool(self, name, arguments):
        assert name == "cronjob"
        if arguments["action"] == "list":
            return {"jobs": list(self.jobs)}
        if arguments["action"] == "create":
            job = {"id": f"job-{len(self.jobs)+1}", **arguments}
            self.jobs.append(job)
            return job
        raise AssertionError(arguments)


def test_plugin_registers_native_surfaces(tmp_path):
    ctx = FakeContext(tmp_path)
    register(ctx)
    assert set(ctx.tools) == {
        "secretary_task",
        "secretary_plan",
        "secretary_feedback",
        "secretary_preferences",
        "secretary_brief",
        "secretary_health",
    }
    assert ctx.hooks.keys() == {"pre_llm_call"}
    assert set(ctx.skills) == {
        "personal-secretary",
        "task-capture",
        "daily-brief",
        "replanning",
        "weekly-review",
    }
    assert {"agenda", "tasks", "secretary-setup"} <= set(ctx.commands)

    payload = json.loads(
        ctx.tools["secretary_task"]["handler"](
            {"action": "create", "title": "Test", "estimate_minutes": 30}
        )
    )
    assert payload["ok"] is True

    injected = ctx.hooks["pre_llm_call"](
        session_id="s", user_message="请帮我安排今天的任务", is_first_turn=True
    )
    assert "Hermes AI Reminder" in injected["context"]


def test_secretary_setup_is_idempotent(tmp_path):
    ctx = FakeContext(tmp_path)
    register(ctx)
    first = json.loads(ctx.commands["secretary-setup"]("morning=07:30"))
    second = json.loads(ctx.commands["secretary-setup"]("morning=07:30"))
    assert first["ok"] is True
    assert len(ctx.jobs) == 3
    assert all(item["status"] == "already_exists" for item in second["jobs"])
