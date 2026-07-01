"""Static plan matcher that chooses the best pre-built workout plan."""

from __future__ import annotations

from .plan_library import PLAN_LIBRARY


def _equipment_key(has_equipment: bool) -> str:
    return "equipment" if has_equipment else "no_equipment"


def _parse_key(key: str) -> tuple[str, str, str, int, int]:
    parts = key.split("__")
    if len(parts) != 5:
        raise ValueError(f"Invalid plan key: {key}")
    fitness_level, goal, equipment, days_part, duration_part = parts
    days = int(days_part[:-1])
    duration = int(duration_part[:-3])
    return fitness_level, goal, equipment, days, duration


def _plan_score(key: str, target_equipment: str, target_days: int, target_duration: int) -> tuple[int, int, int]:
    _, _, equipment, days, duration = _parse_key(key)
    equipment_penalty = 0 if equipment == target_equipment else 100
    return equipment_penalty, abs(days - target_days), abs(duration - target_duration)


def match_plan(profile: dict[str, object]) -> dict[str, object]:
    """Match a static workout plan to a user's onboarding profile."""
    fitness_level = str(profile.get("fitness_level", "")).lower()
    goal = str(profile.get("goal", "")).lower()
    has_equipment = bool(profile.get("has_equipment", False))
    target_days = int(profile.get("days_per_week", 3))
    target_duration = int(profile.get("workout_duration_minutes", 30))

    equipment_key = _equipment_key(has_equipment)
    exact_key = f"{fitness_level}__{goal}__{equipment_key}__{target_days}d__{target_duration}min"
    if exact_key in PLAN_LIBRARY:
        plan = PLAN_LIBRARY[exact_key].copy()
        plan["generated_by"] = "static_library"
        plan["match_key"] = exact_key
        return plan

    candidates = [key for key in PLAN_LIBRARY if key.startswith(f"{fitness_level}__{goal}__")]
    if not candidates:
        # Fallback to the full library if the exact fitness-level or goal is missing.
        candidates = list(PLAN_LIBRARY.keys())

    best_key = min(candidates, key=lambda key: _plan_score(key, equipment_key, target_days, target_duration))
    plan = PLAN_LIBRARY[best_key].copy()
    plan["generated_by"] = "static_library"
    plan["match_key"] = best_key
    return plan
