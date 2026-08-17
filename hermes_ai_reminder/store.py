"""SQLite persistence for tasks, plans, feedback, and learned preferences."""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager, nullcontext
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Sequence

from .models import PlanBlock, TaskRecord
from .time_utils import parse_datetime, utc_now

SCHEMA_VERSION = 1
TASK_STATUSES = {"active", "completed", "archived"}
PLAN_STATES = {"draft", "committed", "superseded", "cancelled"}
BLOCK_STATES = {"planned", "committed", "in_progress", "completed", "snoozed", "skipped", "cancelled"}
ENERGY_LEVELS = {"low", "medium", "high"}


def _json_dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _utc_iso(value: datetime | None = None) -> str:
    dt = value or utc_now()
    return dt.astimezone(timezone.utc).isoformat()


def calendar_signature(task_title: str, start_at: str, end_at: str) -> str:
    return _json_dump(
        {
            "summary": f"[Focus] {task_title}",
            "start": start_at,
            "end": end_at,
        }
    )


class StoreError(RuntimeError):
    pass


class SqliteStore:
    """Small, explicit persistence layer with one connection per operation.

    Opening connections per call avoids leaking handles inside Hermes' long-lived
    gateway process. SQLite WAL mode and a write lock make concurrent tool calls
    predictable without forcing callers to share a connection across threads.
    """

    def __init__(self, db_path: str | Path):
        self.path = Path(db_path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._write_lock = threading.RLock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA busy_timeout = 5000")
        return conn

    @contextmanager
    def transaction(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:
        lock = self._write_lock if write else nullcontext()
        with lock:
            conn = self._connect()
            try:
                conn.execute("BEGIN IMMEDIATE" if write else "BEGIN")
                yield conn
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise
            finally:
                conn.close()

    def _initialize(self) -> None:
        with self._write_lock:
            conn = self._connect()
            try:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS tasks (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        notes TEXT NOT NULL DEFAULT '',
                        status TEXT NOT NULL DEFAULT 'active',
                        priority INTEGER NOT NULL DEFAULT 3 CHECK(priority BETWEEN 1 AND 5),
                        estimate_minutes INTEGER NOT NULL CHECK(estimate_minutes > 0),
                        remaining_minutes INTEGER NOT NULL CHECK(remaining_minutes >= 0),
                        deadline TEXT,
                        earliest_start TEXT,
                        energy TEXT NOT NULL DEFAULT 'medium' CHECK(energy IN ('low','medium','high')),
                        cognitive_load REAL NOT NULL DEFAULT 0.5 CHECK(cognitive_load BETWEEN 0 AND 1),
                        splittable INTEGER NOT NULL DEFAULT 1 CHECK(splittable IN (0,1)),
                        min_block_minutes INTEGER NOT NULL DEFAULT 25 CHECK(min_block_minutes > 0),
                        max_block_minutes INTEGER NOT NULL DEFAULT 90 CHECK(max_block_minutes > 0),
                        context TEXT NOT NULL DEFAULT 'general',
                        source TEXT NOT NULL DEFAULT 'conversation',
                        external_id TEXT UNIQUE,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS task_dependencies (
                        task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                        depends_on_task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE RESTRICT,
                        PRIMARY KEY(task_id, depends_on_task_id),
                        CHECK(task_id <> depends_on_task_id)
                    );

                    CREATE TABLE IF NOT EXISTS plans (
                        id TEXT PRIMARY KEY,
                        state TEXT NOT NULL CHECK(state IN ('draft','committed','superseded','cancelled')),
                        window_start TEXT NOT NULL,
                        window_end TEXT NOT NULL,
                        timezone TEXT NOT NULL,
                        backend TEXT NOT NULL,
                        objective_score REAL NOT NULL DEFAULT 0,
                        supersedes_plan_id TEXT REFERENCES plans(id),
                        details_json TEXT NOT NULL DEFAULT '{}',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS plan_blocks (
                        id TEXT PRIMARY KEY,
                        plan_id TEXT NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
                        task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                        task_title TEXT NOT NULL,
                        start_at TEXT NOT NULL,
                        end_at TEXT NOT NULL,
                        piece_index INTEGER NOT NULL,
                        piece_count INTEGER NOT NULL,
                        context TEXT NOT NULL,
                        energy TEXT NOT NULL,
                        score REAL NOT NULL DEFAULT 0,
                        rationale_json TEXT NOT NULL DEFAULT '[]',
                        state TEXT NOT NULL DEFAULT 'planned' CHECK(state IN ('planned','committed','in_progress','completed','snoozed','skipped','cancelled')),
                        locked INTEGER NOT NULL DEFAULT 0 CHECK(locked IN (0,1)),
                        calendar_event_id TEXT,
                        calendar_signature TEXT,
                        source_block_id TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS feedback (
                        id TEXT PRIMARY KEY,
                        task_id TEXT REFERENCES tasks(id) ON DELETE SET NULL,
                        block_id TEXT REFERENCES plan_blocks(id) ON DELETE SET NULL,
                        outcome TEXT NOT NULL,
                        actual_minutes INTEGER,
                        note TEXT NOT NULL DEFAULT '',
                        metadata_json TEXT NOT NULL DEFAULT '{}',
                        created_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS preferences (
                        key TEXT PRIMARY KEY,
                        value_json TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS audit_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT NOT NULL,
                        entity_id TEXT,
                        payload_json TEXT NOT NULL DEFAULT '{}',
                        created_at TEXT NOT NULL
                    );

                    CREATE INDEX IF NOT EXISTS idx_tasks_status_deadline ON tasks(status, deadline);
                    CREATE INDEX IF NOT EXISTS idx_blocks_plan_start ON plan_blocks(plan_id, start_at);
                    CREATE INDEX IF NOT EXISTS idx_blocks_state_start ON plan_blocks(state, start_at);
                    CREATE INDEX IF NOT EXISTS idx_feedback_task_created ON feedback(task_id, created_at);
                    """
                )
                row = conn.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()
                if row is None:
                    conn.execute(
                        "INSERT INTO metadata(key, value) VALUES('schema_version', ?)",
                        (str(SCHEMA_VERSION),),
                    )
                elif int(row["value"]) != SCHEMA_VERSION:
                    raise StoreError(
                        f"Unsupported database schema {row['value']}; expected {SCHEMA_VERSION}"
                    )
            finally:
                conn.close()

    @staticmethod
    def _decode_task(row: sqlite3.Row, dependencies: Sequence[str]) -> TaskRecord:
        tz = timezone.utc
        return TaskRecord(
            id=row["id"],
            title=row["title"],
            notes=row["notes"],
            status=row["status"],
            priority=int(row["priority"]),
            estimate_minutes=int(row["estimate_minutes"]),
            remaining_minutes=int(row["remaining_minutes"]),
            deadline=parse_datetime(row["deadline"], tz),
            earliest_start=parse_datetime(row["earliest_start"], tz),
            energy=row["energy"],
            cognitive_load=float(row["cognitive_load"]),
            splittable=bool(row["splittable"]),
            min_block_minutes=int(row["min_block_minutes"]),
            max_block_minutes=int(row["max_block_minutes"]),
            context=row["context"],
            source=row["source"],
            external_id=row["external_id"],
            created_at=parse_datetime(row["created_at"], tz) or utc_now(),
            updated_at=parse_datetime(row["updated_at"], tz) or utc_now(),
            dependencies=list(dependencies),
        )

    @staticmethod
    def _dependency_map(conn: sqlite3.Connection, task_ids: Sequence[str]) -> dict[str, list[str]]:
        if not task_ids:
            return {}
        placeholders = ",".join("?" for _ in task_ids)
        rows = conn.execute(
            f"SELECT task_id, depends_on_task_id FROM task_dependencies WHERE task_id IN ({placeholders})",
            tuple(task_ids),
        ).fetchall()
        result: dict[str, list[str]] = {task_id: [] for task_id in task_ids}
        for row in rows:
            result.setdefault(row["task_id"], []).append(row["depends_on_task_id"])
        return result

    def _audit(self, conn: sqlite3.Connection, event_type: str, entity_id: str | None, payload: Any) -> None:
        conn.execute(
            "INSERT INTO audit_log(event_type, entity_id, payload_json, created_at) VALUES(?,?,?,?)",
            (event_type, entity_id, _json_dump(payload), _utc_iso()),
        )

    @staticmethod
    def _validate_task_payload(data: dict[str, Any]) -> dict[str, Any]:
        payload = dict(data)
        title = str(payload.get("title") or "").strip()
        if not title:
            raise ValueError("title cannot be blank")
        payload["title"] = title

        status = str(payload.get("status") or "active")
        if status not in TASK_STATUSES:
            raise ValueError(f"Invalid task status: {status}")
        payload["status"] = status

        priority = int(payload.get("priority", 3))
        if not 1 <= priority <= 5:
            raise ValueError("priority must be between 1 and 5")
        payload["priority"] = priority

        estimate = int(payload.get("estimate_minutes", 0))
        if estimate <= 0:
            raise ValueError("estimate_minutes must be positive")
        payload["estimate_minutes"] = estimate

        remaining = int(payload.get("remaining_minutes", estimate))
        if remaining < 0:
            raise ValueError("remaining_minutes cannot be negative")
        if status == "completed" and remaining != 0:
            raise ValueError("completed tasks must have remaining_minutes=0")
        payload["remaining_minutes"] = remaining

        energy = str(payload.get("energy") or "medium").lower()
        if energy not in ENERGY_LEVELS:
            raise ValueError(f"energy must be one of {sorted(ENERGY_LEVELS)}")
        payload["energy"] = energy

        cognitive_load = float(payload.get("cognitive_load", 0.5))
        if not 0.0 <= cognitive_load <= 1.0:
            raise ValueError("cognitive_load must be between 0 and 1")
        payload["cognitive_load"] = cognitive_load

        min_block = int(payload.get("min_block_minutes", 25))
        max_block = int(payload.get("max_block_minutes", 90))
        if min_block <= 0 or max_block <= 0:
            raise ValueError("min_block_minutes and max_block_minutes must be positive")
        if min_block > max_block:
            raise ValueError("min_block_minutes cannot exceed max_block_minutes")
        payload["min_block_minutes"] = min_block
        payload["max_block_minutes"] = max_block

        payload["splittable"] = bool(payload.get("splittable", True))
        payload["notes"] = str(payload.get("notes") or "")
        payload["context"] = str(payload.get("context") or "general").strip() or "general"
        payload["source"] = str(payload.get("source") or "conversation").strip() or "conversation"

        parsed_dates: dict[str, datetime | None] = {}
        for key in ("deadline", "earliest_start"):
            raw = payload.get(key)
            parsed = parse_datetime(raw, timezone.utc) if raw not in (None, "") else None
            parsed_dates[key] = parsed
            payload[key] = _utc_iso(parsed) if parsed else None
        if (
            parsed_dates["deadline"] is not None
            and parsed_dates["earliest_start"] is not None
            and parsed_dates["deadline"] <= parsed_dates["earliest_start"]
        ):
            raise ValueError("deadline must be after earliest_start")
        return payload

    def create_task(self, data: dict[str, Any], dependencies: Sequence[str] | None = None) -> TaskRecord:
        payload = self._validate_task_payload(data)
        task_id = str(data.get("id") or uuid.uuid4())
        now = _utc_iso()

        with self.transaction(write=True) as conn:
            conn.execute(
                """
                INSERT INTO tasks(
                    id,title,notes,status,priority,estimate_minutes,remaining_minutes,
                    deadline,earliest_start,energy,cognitive_load,splittable,
                    min_block_minutes,max_block_minutes,context,source,external_id,
                    created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    task_id,
                    payload["title"],
                    payload["notes"],
                    payload["status"],
                    payload["priority"],
                    payload["estimate_minutes"],
                    payload["remaining_minutes"],
                    payload["deadline"],
                    payload["earliest_start"],
                    payload["energy"],
                    payload["cognitive_load"],
                    1 if payload["splittable"] else 0,
                    payload["min_block_minutes"],
                    payload["max_block_minutes"],
                    payload["context"],
                    payload["source"],
                    payload.get("external_id"),
                    now,
                    now,
                ),
            )
            self._replace_dependencies(conn, task_id, dependencies or [])
            self._audit(conn, "task.created", task_id, payload)
        return self.get_task(task_id)

    def _replace_dependencies(
        self, conn: sqlite3.Connection, task_id: str, dependencies: Sequence[str]
    ) -> None:
        unique = list(dict.fromkeys(str(item) for item in dependencies if item))
        if task_id in unique:
            raise ValueError("A task cannot depend on itself")
        if unique:
            placeholders = ",".join("?" for _ in unique)
            rows = conn.execute(
                f"SELECT id FROM tasks WHERE id IN ({placeholders})", tuple(unique)
            ).fetchall()
            existing = {row["id"] for row in rows}
            missing = [item for item in unique if item not in existing]
            if missing:
                raise ValueError(f"Unknown dependency task ids: {missing}")

        rows = conn.execute(
            "SELECT task_id,depends_on_task_id FROM task_dependencies WHERE task_id <> ?",
            (task_id,),
        ).fetchall()
        graph: dict[str, set[str]] = {}
        for row in rows:
            graph.setdefault(row["task_id"], set()).add(row["depends_on_task_id"])
        graph[task_id] = set(unique)

        def reaches(start: str, target: str) -> bool:
            stack = [start]
            visited: set[str] = set()
            while stack:
                current = stack.pop()
                if current == target:
                    return True
                if current in visited:
                    continue
                visited.add(current)
                stack.extend(graph.get(current, ()))
            return False

        if any(reaches(dependency, task_id) for dependency in unique):
            raise ValueError("Task dependencies would create a cycle")
        conn.execute("DELETE FROM task_dependencies WHERE task_id=?", (task_id,))
        conn.executemany(
            "INSERT INTO task_dependencies(task_id, depends_on_task_id) VALUES(?,?)",
            [(task_id, dependency) for dependency in unique],
        )

    def get_task(self, task_id: str) -> TaskRecord:
        with self.transaction() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
            if row is None:
                raise KeyError(f"Task not found: {task_id}")
            deps = [
                item["depends_on_task_id"]
                for item in conn.execute(
                    "SELECT depends_on_task_id FROM task_dependencies WHERE task_id=?",
                    (task_id,),
                ).fetchall()
            ]
            return self._decode_task(row, deps)

    def get_task_by_external_id(self, external_id: str) -> TaskRecord | None:
        with self.transaction() as conn:
            row = conn.execute("SELECT id FROM tasks WHERE external_id=?", (external_id,)).fetchone()
        return self.get_task(row["id"]) if row else None

    def update_task(
        self,
        task_id: str,
        changes: dict[str, Any],
        dependencies: Sequence[str] | None = None,
    ) -> TaskRecord:
        allowed = {
            "title",
            "notes",
            "status",
            "priority",
            "estimate_minutes",
            "remaining_minutes",
            "deadline",
            "earliest_start",
            "energy",
            "cognitive_load",
            "splittable",
            "min_block_minutes",
            "max_block_minutes",
            "context",
            "source",
            "external_id",
        }
        requested = {key: value for key, value in changes.items() if key in allowed}
        with self.transaction(write=True) as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
            if row is None:
                raise KeyError(f"Task not found: {task_id}")
            complete = dict(row)
            complete.update(requested)
            complete["splittable"] = bool(complete["splittable"])
            payload = self._validate_task_payload(complete)
            fields = {key: payload[key] for key in requested}
            if "splittable" in fields:
                fields["splittable"] = 1 if fields["splittable"] else 0
            fields["updated_at"] = _utc_iso()
            if fields:
                assignments = ",".join(f"{key}=?" for key in fields)
                conn.execute(
                    f"UPDATE tasks SET {assignments} WHERE id=?",
                    tuple(fields.values()) + (task_id,),
                )
            if dependencies is not None:
                self._replace_dependencies(conn, task_id, dependencies)
            self._audit(conn, "task.updated", task_id, {"changes": changes, "dependencies": dependencies})
        return self.get_task(task_id)

    def list_tasks(
        self,
        *,
        statuses: Sequence[str] | None = None,
        due_before: str | None = None,
        limit: int = 200,
    ) -> list[TaskRecord]:
        clauses: list[str] = []
        params: list[Any] = []
        if statuses:
            invalid = [status for status in statuses if status not in TASK_STATUSES]
            if invalid:
                raise ValueError(f"Invalid task statuses: {invalid}")
            placeholders = ",".join("?" for _ in statuses)
            clauses.append(f"status IN ({placeholders})")
            params.extend(statuses)
        if due_before:
            clauses.append("deadline IS NOT NULL AND deadline <= ?")
            params.append(due_before)
        sql = "SELECT * FROM tasks"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY CASE WHEN deadline IS NULL THEN 1 ELSE 0 END, deadline, priority DESC, created_at LIMIT ?"
        params.append(max(1, min(int(limit), 1000)))
        with self.transaction() as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()
            dep_map = self._dependency_map(conn, [row["id"] for row in rows])
            return [self._decode_task(row, dep_map.get(row["id"], [])) for row in rows]

    def create_plan(
        self,
        *,
        window_start: str,
        window_end: str,
        timezone_name: str,
        backend: str,
        objective_score: float,
        blocks: Sequence[PlanBlock],
        details: dict[str, Any],
        supersedes_plan_id: str | None = None,
    ) -> dict[str, Any]:
        plan_id = str(uuid.uuid4())
        now = _utc_iso()
        with self.transaction(write=True) as conn:
            conn.execute(
                """
                INSERT INTO plans(
                    id,state,window_start,window_end,timezone,backend,objective_score,
                    supersedes_plan_id,details_json,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    plan_id,
                    "draft",
                    window_start,
                    window_end,
                    timezone_name,
                    backend,
                    objective_score,
                    supersedes_plan_id,
                    _json_dump(details),
                    now,
                    now,
                ),
            )
            for block in blocks:
                block_id = str(uuid.uuid4())
                block.id = block_id
                block.plan_id = plan_id
                conn.execute(
                    """
                    INSERT INTO plan_blocks(
                        id,plan_id,task_id,task_title,start_at,end_at,piece_index,piece_count,
                        context,energy,score,rationale_json,state,locked,calendar_event_id,
                        calendar_signature,source_block_id,created_at,updated_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        block_id,
                        plan_id,
                        block.task_id,
                        block.task_title,
                        _utc_iso(block.start),
                        _utc_iso(block.end),
                        block.piece_index,
                        block.piece_count,
                        block.context,
                        block.energy,
                        block.score,
                        _json_dump(block.rationale),
                        block.state,
                        1 if block.locked else 0,
                        block.calendar_event_id,
                        block.calendar_signature,
                        block.source_block_id,
                        now,
                        now,
                    ),
                )
            self._audit(conn, "plan.created", plan_id, {"backend": backend, "blocks": len(blocks)})
        return self.get_plan(plan_id)

    def get_plan(self, plan_id: str | None = None, *, state: str | None = None) -> dict[str, Any]:
        with self.transaction() as conn:
            if plan_id:
                row = conn.execute("SELECT * FROM plans WHERE id=?", (plan_id,)).fetchone()
            elif state:
                row = conn.execute(
                    "SELECT * FROM plans WHERE state=? ORDER BY created_at DESC LIMIT 1", (state,)
                ).fetchone()
            else:
                row = conn.execute("SELECT * FROM plans ORDER BY created_at DESC LIMIT 1").fetchone()
            if row is None:
                raise KeyError("Plan not found")
            block_rows = conn.execute(
                "SELECT * FROM plan_blocks WHERE plan_id=? ORDER BY start_at, piece_index",
                (row["id"],),
            ).fetchall()
        blocks = [self._decode_block(item) for item in block_rows]
        return {
            "id": row["id"],
            "state": row["state"],
            "window_start": row["window_start"],
            "window_end": row["window_end"],
            "timezone": row["timezone"],
            "backend": row["backend"],
            "objective_score": row["objective_score"],
            "supersedes_plan_id": row["supersedes_plan_id"],
            "details": json.loads(row["details_json"] or "{}"),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "blocks": blocks,
        }

    @staticmethod
    def _decode_block(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "plan_id": row["plan_id"],
            "task_id": row["task_id"],
            "task_title": row["task_title"],
            "start": row["start_at"],
            "end": row["end_at"],
            "duration_minutes": int(
                (
                    (parse_datetime(row["end_at"], timezone.utc) or utc_now())
                    - (parse_datetime(row["start_at"], timezone.utc) or utc_now())
                ).total_seconds()
                // 60
            ),
            "piece_index": row["piece_index"],
            "piece_count": row["piece_count"],
            "context": row["context"],
            "energy": row["energy"],
            "score": row["score"],
            "rationale": json.loads(row["rationale_json"] or "[]"),
            "state": row["state"],
            "locked": bool(row["locked"]),
            "calendar_event_id": row["calendar_event_id"],
            "calendar_signature": row["calendar_signature"],
            "source_block_id": row["source_block_id"],
        }

    def list_plans(self, limit: int = 20) -> list[dict[str, Any]]:
        with self.transaction() as conn:
            rows = conn.execute(
                "SELECT id,state,window_start,window_end,timezone,backend,objective_score,created_at FROM plans ORDER BY created_at DESC LIMIT ?",
                (max(1, min(limit, 100)),),
            ).fetchall()
            return [dict(row) for row in rows]

    def set_plan_state(self, plan_id: str, state: str) -> dict[str, Any]:
        if state not in PLAN_STATES:
            raise ValueError(f"Invalid plan state: {state}")
        now = _utc_iso()
        with self.transaction(write=True) as conn:
            row = conn.execute("SELECT state,supersedes_plan_id FROM plans WHERE id=?", (plan_id,)).fetchone()
            if row is None:
                raise KeyError(f"Plan not found: {plan_id}")
            conn.execute("UPDATE plans SET state=?,updated_at=? WHERE id=?", (state, now, plan_id))
            if state == "committed":
                conn.execute(
                    "UPDATE plan_blocks SET state=CASE WHEN state='planned' THEN 'committed' ELSE state END, updated_at=? WHERE plan_id=?",
                    (now, plan_id),
                )
                supersedes = row["supersedes_plan_id"]
                if supersedes:
                    conn.execute(
                        "UPDATE plans SET state='superseded',updated_at=? WHERE id=? AND state <> 'cancelled'",
                        (now, supersedes),
                    )
            self._audit(conn, "plan.state", plan_id, {"from": row["state"], "to": state})
        return self.get_plan(plan_id)

    def set_block_state(self, block_id: str, state: str, *, locked: bool | None = None) -> dict[str, Any]:
        if state not in BLOCK_STATES:
            raise ValueError(f"Invalid block state: {state}")
        updates: dict[str, Any] = {"state": state, "updated_at": _utc_iso()}
        if locked is not None:
            updates["locked"] = 1 if locked else 0
        with self.transaction(write=True) as conn:
            if conn.execute("SELECT 1 FROM plan_blocks WHERE id=?", (block_id,)).fetchone() is None:
                raise KeyError(f"Block not found: {block_id}")
            assignments = ",".join(f"{key}=?" for key in updates)
            conn.execute(
                f"UPDATE plan_blocks SET {assignments} WHERE id=?",
                tuple(updates.values()) + (block_id,),
            )
            self._audit(conn, "block.state", block_id, updates)
        return self.get_block(block_id)

    def get_block(self, block_id: str) -> dict[str, Any]:
        with self.transaction() as conn:
            row = conn.execute("SELECT * FROM plan_blocks WHERE id=?", (block_id,)).fetchone()
            if row is None:
                raise KeyError(f"Block not found: {block_id}")
            return self._decode_block(row)

    def link_calendar_event(self, block_id: str, event_id: str) -> dict[str, Any]:
        with self.transaction(write=True) as conn:
            row = conn.execute(
                "SELECT task_title,start_at,end_at FROM plan_blocks WHERE id=?", (block_id,)
            ).fetchone()
            if row is None:
                raise KeyError(f"Block not found: {block_id}")
            conn.execute(
                "UPDATE plan_blocks SET calendar_event_id=?,calendar_signature=?,updated_at=? WHERE id=?",
                (
                    event_id,
                    calendar_signature(row["task_title"], row["start_at"], row["end_at"]),
                    _utc_iso(),
                    block_id,
                ),
            )
            self._audit(conn, "block.calendar_linked", block_id, {"calendar_event_id": event_id})
        return self.get_block(block_id)

    def unlink_calendar_event(self, block_id: str) -> dict[str, Any]:
        with self.transaction(write=True) as conn:
            row = conn.execute(
                "SELECT calendar_event_id FROM plan_blocks WHERE id=?", (block_id,)
            ).fetchone()
            if row is None:
                raise KeyError(f"Block not found: {block_id}")
            conn.execute(
                "UPDATE plan_blocks SET calendar_event_id=NULL,calendar_signature=NULL,updated_at=? WHERE id=?",
                (_utc_iso(), block_id),
            )
            self._audit(
                conn,
                "block.calendar_unlinked",
                block_id,
                {"calendar_event_id": row["calendar_event_id"]},
            )
        return self.get_block(block_id)

    def blocks_between(
        self,
        start_at: str,
        end_at: str,
        *,
        plan_states: Sequence[str] = ("committed", "draft"),
        plan_id: str | None = None,
    ) -> list[dict[str, Any]]:
        placeholders = ",".join("?" for _ in plan_states)
        plan_clause = " AND p.id=?" if plan_id else ""
        with self.transaction() as conn:
            rows = conn.execute(
                f"""
                SELECT b.* FROM plan_blocks b
                JOIN plans p ON p.id=b.plan_id
                WHERE p.state IN ({placeholders})
                  {plan_clause}
                  AND b.start_at < ? AND b.end_at > ?
                  AND b.state NOT IN ('cancelled','skipped')
                ORDER BY b.start_at
                """,
                tuple(plan_states) + ((plan_id,) if plan_id else ()) + (end_at, start_at),
            ).fetchall()
            return [self._decode_block(row) for row in rows]

    def record_feedback(
        self,
        *,
        task_id: str | None,
        block_id: str | None,
        outcome: str,
        actual_minutes: int | None,
        note: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        feedback_id = str(uuid.uuid4())
        created_at = _utc_iso()
        with self.transaction(write=True) as conn:
            conn.execute(
                "INSERT INTO feedback(id,task_id,block_id,outcome,actual_minutes,note,metadata_json,created_at) VALUES(?,?,?,?,?,?,?,?)",
                (
                    feedback_id,
                    task_id,
                    block_id,
                    outcome,
                    actual_minutes,
                    note,
                    _json_dump(metadata or {}),
                    created_at,
                ),
            )
            self._audit(conn, "feedback.recorded", feedback_id, {"task_id": task_id, "block_id": block_id, "outcome": outcome})
        return {
            "id": feedback_id,
            "task_id": task_id,
            "block_id": block_id,
            "outcome": outcome,
            "actual_minutes": actual_minutes,
            "note": note,
            "metadata": metadata or {},
            "created_at": created_at,
        }

    def latest_feedback_for_block(self, block_id: str) -> dict[str, Any] | None:
        with self.transaction() as conn:
            row = conn.execute(
                "SELECT * FROM feedback WHERE block_id=? ORDER BY created_at DESC LIMIT 1",
                (block_id,),
            ).fetchone()
            if row is None:
                return None
            return {
                "id": row["id"],
                "task_id": row["task_id"],
                "block_id": row["block_id"],
                "outcome": row["outcome"],
                "actual_minutes": row["actual_minutes"],
                "note": row["note"],
                "metadata": json.loads(row["metadata_json"] or "{}"),
                "created_at": row["created_at"],
            }

    def feedback_stats(self, *, days: int = 30) -> dict[str, Any]:
        with self.transaction() as conn:
            rows = conn.execute(
                """
                SELECT outcome, COUNT(*) AS count, AVG(actual_minutes) AS avg_actual
                FROM feedback
                WHERE created_at >= datetime('now', ?)
                GROUP BY outcome
                ORDER BY count DESC
                """,
                (f"-{max(1, days)} days",),
            ).fetchall()
        return {
            row["outcome"]: {"count": row["count"], "avg_actual_minutes": row["avg_actual"]}
            for row in rows
        }

    def get_preference(self, key: str, default: Any = None) -> Any:
        with self.transaction() as conn:
            row = conn.execute("SELECT value_json FROM preferences WHERE key=?", (key,)).fetchone()
            return json.loads(row["value_json"]) if row else default

    def all_preferences(self) -> dict[str, Any]:
        with self.transaction() as conn:
            rows = conn.execute("SELECT key,value_json FROM preferences ORDER BY key").fetchall()
            return {row["key"]: json.loads(row["value_json"]) for row in rows}

    def set_preference(self, key: str, value: Any) -> Any:
        with self.transaction(write=True) as conn:
            conn.execute(
                """
                INSERT INTO preferences(key,value_json,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json,updated_at=excluded.updated_at
                """,
                (key, _json_dump(value), _utc_iso()),
            )
            self._audit(conn, "preference.set", key, value)
        return value

    def delete_preference(self, key: str) -> None:
        with self.transaction(write=True) as conn:
            conn.execute("DELETE FROM preferences WHERE key=?", (key,))
            self._audit(conn, "preference.deleted", key, {})

    def counts(self) -> dict[str, int]:
        with self.transaction() as conn:
            return {
                "active_tasks": conn.execute("SELECT COUNT(*) FROM tasks WHERE status='active'").fetchone()[0],
                "completed_tasks": conn.execute("SELECT COUNT(*) FROM tasks WHERE status='completed'").fetchone()[0],
                "draft_plans": conn.execute("SELECT COUNT(*) FROM plans WHERE state='draft'").fetchone()[0],
                "committed_plans": conn.execute("SELECT COUNT(*) FROM plans WHERE state='committed'").fetchone()[0],
                "feedback_events": conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0],
            }
