"""Privacy-preserving preference learning from explicit execution feedback."""

from __future__ import annotations

from typing import Any

from .store import SqliteStore
from .time_utils import default_energy_profile


def _bounded(value: float, low: float, high: float) -> float:
    return min(high, max(low, value))


def effective_estimate_multiplier(store: SqliteStore, context: str) -> float:
    biases = store.get_preference("estimate_bias", {})
    entry = biases.get(context) or biases.get("general")
    if not isinstance(entry, dict):
        return 1.0
    return _bounded(float(entry.get("value", 1.0)), 0.6, 2.5)


def learned_energy_profile(store: SqliteStore) -> dict[str, float]:
    base = store.get_preference("energy_profile", default_energy_profile())
    if not isinstance(base, dict):
        base = default_energy_profile()
    profile = {str(hour): float(base.get(str(hour), 0.5)) for hour in range(24)}

    learned = store.get_preference("hour_success", {})
    if not isinstance(learned, dict):
        return profile
    for hour, entry in learned.items():
        if not isinstance(entry, dict):
            continue
        count = int(entry.get("count", 0))
        score = float(entry.get("score", profile.get(str(hour), 0.5)))
        # A cautious empirical-Bayes blend: explicit profile remains the prior.
        weight = min(0.75, count / (count + 8.0))
        profile[str(hour)] = round((1 - weight) * profile.get(str(hour), 0.5) + weight * score, 4)
    return profile


def apply_feedback_learning(
    store: SqliteStore,
    *,
    context: str,
    scheduled_minutes: int,
    actual_minutes: int | None,
    start_hour: int | None,
    outcome: str,
) -> dict[str, Any]:
    updates: dict[str, Any] = {}

    if actual_minutes and scheduled_minutes > 0 and outcome in {"completed", "overrun"}:
        ratio = _bounded(actual_minutes / scheduled_minutes, 0.5, 3.0)
        biases = store.get_preference("estimate_bias", {})
        if not isinstance(biases, dict):
            biases = {}
        current = biases.get(context, {"value": 1.0, "count": 0})
        old_value = float(current.get("value", 1.0))
        old_count = int(current.get("count", 0))
        alpha = 0.25 if old_count < 8 else 0.12
        new_value = _bounded((1 - alpha) * old_value + alpha * ratio, 0.6, 2.5)
        biases[context] = {"value": round(new_value, 4), "count": old_count + 1}
        store.set_preference("estimate_bias", biases)
        updates["estimate_bias"] = {context: biases[context]}

    if start_hour is not None:
        outcome_scores = {
            "completed": 1.0,
            "started": 0.75,
            "accepted": 0.70,
            "overrun": 0.62,
            "snoozed": 0.30,
            "skipped": 0.05,
        }
        if outcome in outcome_scores:
            learned = store.get_preference("hour_success", {})
            if not isinstance(learned, dict):
                learned = {}
            key = str(start_hour)
            current = learned.get(key, {"score": 0.5, "count": 0})
            count = int(current.get("count", 0))
            old_score = float(current.get("score", 0.5))
            observation = outcome_scores[outcome]
            alpha = 1.0 / min(12, count + 2)
            score = _bounded((1 - alpha) * old_score + alpha * observation, 0.0, 1.0)
            learned[key] = {"score": round(score, 4), "count": count + 1}
            store.set_preference("hour_success", learned)
            updates["hour_success"] = {key: learned[key]}

    return updates
