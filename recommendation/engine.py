"""Orchestrator for recommendation workflows and workout plan generation."""

from __future__ import annotations

from .llm_planner import generate_weekly_plan, get_fallback_plan
from .plan_matcher import match_plan
from .rule_based import predict_difficulty
from .schemas import WeeklyPlan


def generate_plan(user_profile: dict[str, object], user_metrics: dict[str, object]) -> dict[str, object]:
    """Generate a workout plan using static onboarding matching or LLM fallback."""
    if not user_profile.get("onboarding_complete"):
        plan_input = {
            "fitness_level": user_profile.get("fitness_level"),
            "goal": user_profile.get("goal"),
            "has_equipment": user_profile.get("has_equipment", False),
            "days_per_week": user_profile.get("days_per_week"),
            "workout_duration_minutes": user_profile.get("workout_duration_minutes"),
        }
        if all(value is not None for value in plan_input.values()):
            return match_plan(plan_input)

    difficulty_level = predict_difficulty(user_metrics)
    plan = generate_weekly_plan(user_profile, difficulty_level)
    try:
        validated_plan = WeeklyPlan.model_validate(plan)
        return validated_plan.model_dump()
    except Exception:
        return get_fallback_plan(difficulty_level)
