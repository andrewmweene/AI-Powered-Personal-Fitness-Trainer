"""Match onboarding profiles to the closest static workout plan."""

from __future__ import annotations

import logging
from copy import deepcopy

from .plan_library import PLAN_LIBRARY, get_fallback_plan

logger = logging.getLogger(__name__)
MIN_DAYS_BRACKET = [3, 4, 5]
MIN_DURATION_BRACKET = [30, 45, 60]


def _closest(value: int, options: list[int]) -> int:
    """Return the available option closest to a requested integer."""
    return min(options, key=lambda option: abs(option - value))


def match_plan(profile: dict) -> dict:
    """Match a profile to a complete static plan and never return ``None``.

    Args:
        profile: Fitness level, goal, equipment, days, and duration preferences.

    Returns:
        A copied plan from ``PLAN_LIBRARY``.
    """
    fitness_level = str(profile.get("fitness_level", "beginner")).lower()
    goal = str(profile.get("goal", "general_fitness")).lower()
    has_equipment = bool(profile.get("has_equipment", False))
    try:
        days = int(profile.get("days_per_week", 3))
    except (TypeError, ValueError):
        days = 3
    try:
        duration = int(profile.get("workout_duration_minutes", 30))
    except (TypeError, ValueError):
        duration = 30

    equipment = "with_equipment" if has_equipment else "no_equipment"
    days_bracket = _closest(days, MIN_DAYS_BRACKET)
    duration_bracket = _closest(duration, MIN_DURATION_BRACKET)

    exact_key = f"{fitness_level}__{goal}__{equipment}__{days_bracket}d__{duration_bracket}min"
    if exact_key in PLAN_LIBRARY:
        logger.info("Plan matched exactly: %s", exact_key)
        return deepcopy(PLAN_LIBRARY[exact_key])

    for equipment_fallback in ("no_equipment", "with_equipment"):
        fallback_key = f"{fitness_level}__{goal}__{equipment_fallback}__{days_bracket}d__{duration_bracket}min"
        if fallback_key in PLAN_LIBRARY:
            logger.info("Plan matched with equipment fallback: %s", fallback_key)
            return deepcopy(PLAN_LIBRARY[fallback_key])

    prefix = f"{fitness_level}__{goal}__"
    for key, plan in PLAN_LIBRARY.items():
        if key.startswith(prefix):
            logger.info("Plan matched by level and goal: %s", key)
            return deepcopy(plan)

    prefix = f"{fitness_level}__general_fitness__"
    for key, plan in PLAN_LIBRARY.items():
        if key.startswith(prefix):
            logger.info("Plan matched by general-fitness fallback: %s", key)
            return deepcopy(plan)

    logger.warning("No static plan matched profile %s; using beginner fallback", profile)
    return get_fallback_plan("beginner")
