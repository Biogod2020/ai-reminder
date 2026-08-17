"""Timezone-safe parsing and interval helpers."""

from __future__ import annotations

import math
import os
from datetime import date, datetime, time, timedelta, timezone, tzinfo
from typing import Any, Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .models import Interval

UTC = timezone.utc


def utc_now() -> datetime:
    return datetime.now(UTC)


def get_timezone(name: str | None) -> tzinfo:
    value = (name or os.getenv("TZ") or "UTC").strip()
    if value.lower() in {"local", "system"}:
        return datetime.now().astimezone().tzinfo or UTC
    try:
        return ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown timezone: {value}") from exc


def parse_datetime(value: str | datetime | None, default_tz: tzinfo) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        text = value.strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError as exc:
            raise ValueError(f"Invalid ISO-8601 datetime: {value}") from exc
    else:
        raise TypeError("Datetime values must be strings or datetime objects")

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=default_tz)
    return parsed


def parse_interval(value: dict[str, Any], default_tz: tzinfo) -> Interval:
    if not isinstance(value, dict):
        raise ValueError("Each interval must be an object with start and end")
    start = parse_datetime(value.get("start"), default_tz)
    end = parse_datetime(value.get("end"), default_tz)
    if start is None or end is None:
        raise ValueError("Interval start and end are required")
    if end <= start:
        raise ValueError("Interval end must be after start")
    return Interval(
        start=start,
        end=end,
        label=str(value.get("label") or value.get("summary") or ""),
        external_id=(str(value["id"]) if value.get("id") is not None else None),
    )


def parse_intervals(values: Iterable[dict[str, Any]] | None, default_tz: tzinfo) -> list[Interval]:
    if values is None:
        return []
    return [parse_interval(value, default_tz) for value in values]


def ceil_minutes(value: int, quantum: int) -> int:
    if quantum <= 0:
        raise ValueError("quantum must be positive")
    return int(math.ceil(max(0, value) / quantum) * quantum)


def floor_datetime(value: datetime, minutes: int) -> datetime:
    discard = timedelta(
        minutes=value.minute % minutes,
        seconds=value.second,
        microseconds=value.microsecond,
    )
    return value - discard


def ceil_datetime(value: datetime, minutes: int) -> datetime:
    floored = floor_datetime(value, minutes)
    if floored == value:
        return value
    return floored + timedelta(minutes=minutes)


def merge_intervals(intervals: Iterable[Interval]) -> list[Interval]:
    ordered = sorted(intervals, key=lambda item: (item.start, item.end))
    if not ordered:
        return []
    merged: list[Interval] = [ordered[0]]
    for current in ordered[1:]:
        previous = merged[-1]
        if current.start <= previous.end:
            merged[-1] = Interval(
                start=previous.start,
                end=max(previous.end, current.end),
                label=previous.label or current.label,
            )
        else:
            merged.append(current)
    return merged


def default_work_windows() -> dict[str, list[list[str]]]:
    # Keys follow Python weekday numbering: Monday=0, Sunday=6.
    return {
        "0": [["09:00", "12:00"], ["13:00", "18:00"]],
        "1": [["09:00", "12:00"], ["13:00", "18:00"]],
        "2": [["09:00", "12:00"], ["13:00", "18:00"]],
        "3": [["09:00", "12:00"], ["13:00", "18:00"]],
        "4": [["09:00", "12:00"], ["13:00", "18:00"]],
        "5": [],
        "6": [],
    }


def default_energy_profile() -> dict[str, float]:
    # Neutral, human-editable prior. Feedback gradually overrides it.
    values: dict[str, float] = {}
    for hour in range(24):
        if 9 <= hour < 12:
            score = 0.90
        elif 14 <= hour < 17:
            score = 0.78
        elif 7 <= hour < 9 or 12 <= hour < 14 or 17 <= hour < 19:
            score = 0.56
        elif 19 <= hour < 22:
            score = 0.38
        else:
            score = 0.20
        values[str(hour)] = score
    return values


def _parse_clock(text: str) -> time:
    try:
        hour_text, minute_text = text.split(":", 1)
        hour = int(hour_text)
        minute = int(minute_text)
        return time(hour=hour, minute=minute)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid HH:MM clock value: {text}") from exc


def validate_work_windows(value: Any) -> dict[str, list[list[str]]]:
    if not isinstance(value, dict):
        raise ValueError("work_windows must be an object keyed by weekday 0-6")
    normalised: dict[str, list[list[str]]] = {str(day): [] for day in range(7)}
    for raw_day, raw_windows in value.items():
        day = str(raw_day)
        if day not in normalised:
            raise ValueError("work_windows keys must be weekday numbers 0-6")
        if not isinstance(raw_windows, list):
            raise ValueError(f"work_windows[{day}] must be a list")
        parsed: list[list[str]] = []
        for raw in raw_windows:
            if not isinstance(raw, list) or len(raw) != 2:
                raise ValueError("Each work window must be [HH:MM, HH:MM]")
            start_clock = _parse_clock(str(raw[0]))
            end_clock = _parse_clock(str(raw[1]))
            if end_clock == start_clock:
                raise ValueError("A work window cannot have zero duration")
            parsed.append(
                [
                    start_clock.strftime("%H:%M"),
                    end_clock.strftime("%H:%M"),
                ]
            )
        parsed.sort()
        for left, right in zip(parsed, parsed[1:], strict=False):
            left_start = _parse_clock(left[0]).hour * 60 + _parse_clock(left[0]).minute
            left_end = _parse_clock(left[1]).hour * 60 + _parse_clock(left[1]).minute
            right_start = _parse_clock(right[0]).hour * 60 + _parse_clock(right[0]).minute
            if left_end <= left_start:
                left_end += 24 * 60
            if right_start < left_end and right_start >= left_start:
                raise ValueError(f"work_windows[{day}] contains overlapping intervals")
        normalised[day] = parsed
    return normalised


def validate_energy_profile(value: Any) -> dict[str, float]:
    if not isinstance(value, dict):
        raise ValueError("energy_profile must be an object keyed by hour 0-23")
    normalised: dict[str, float] = {}
    for raw_hour, raw_score in value.items():
        try:
            hour = int(raw_hour)
            score = float(raw_score)
        except (TypeError, ValueError) as exc:
            raise ValueError("energy_profile keys and values must be numeric") from exc
        if not 0 <= hour <= 23:
            raise ValueError("energy_profile hours must be between 0 and 23")
        if not 0.0 <= score <= 1.0:
            raise ValueError("energy_profile scores must be between 0 and 1")
        normalised[str(hour)] = score
    return normalised


def build_availability(
    window_start: datetime,
    window_end: datetime,
    timezone_name: str,
    work_windows: dict[str, list[list[str]]] | None = None,
) -> list[Interval]:
    tz = get_timezone(timezone_name)
    work_windows = validate_work_windows(
        default_work_windows() if work_windows is None else work_windows
    )
    local_start = window_start.astimezone(tz)
    local_end = window_end.astimezone(tz)

    current: date = local_start.date()
    last: date = local_end.date()
    intervals: list[Interval] = []
    while current <= last:
        weekday_windows = work_windows.get(str(current.weekday()), [])
        for raw in weekday_windows:
            if not isinstance(raw, list) or len(raw) != 2:
                raise ValueError("Each work window must be [HH:MM, HH:MM]")
            start_clock, end_clock = _parse_clock(raw[0]), _parse_clock(raw[1])
            start_dt = datetime.combine(current, start_clock, tzinfo=tz)
            end_dt = datetime.combine(current, end_clock, tzinfo=tz)
            if end_dt <= start_dt:
                end_dt += timedelta(days=1)
            clipped_start = max(start_dt, window_start.astimezone(tz))
            clipped_end = min(end_dt, window_end.astimezone(tz))
            if clipped_end > clipped_start:
                intervals.append(Interval(clipped_start, clipped_end, label="work_window"))
        current += timedelta(days=1)
    return merge_intervals(intervals)


def day_range(reference: datetime, mode: str, timezone_name: str) -> tuple[datetime, datetime]:
    tz = get_timezone(timezone_name)
    local = reference.astimezone(tz)
    mode = mode.lower()
    if mode == "tomorrow":
        target = local.date() + timedelta(days=1)
        start = datetime.combine(target, time.min, tzinfo=tz)
        return start, start + timedelta(days=1)
    if mode == "week":
        start = datetime.combine(local.date(), time.min, tzinfo=tz)
        return start, start + timedelta(days=7)
    start = datetime.combine(local.date(), time.min, tzinfo=tz)
    return start, start + timedelta(days=1)
