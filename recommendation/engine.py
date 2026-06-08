"""Orchestrator for recommendation workflows and workout plan generation."""

from __future__ import annotations

from .llm_planner import generate_weekly_plan, get_fallback_plan
from .rule_based import predict_difficulty
from .schemas import WeeklyPlan


def generate_plan(user_profile: dict[str, object], user_metrics: dict[str, object]) -> dict[str, object]:
    """Generate a workout plan using LLM and fallback rule-based recommendations."""
    difficulty_level = predict_difficulty(user_metrics)
    plan = generate_weekly_plan(user_profile, difficulty_level)
    try:
        validated_plan = WeeklyPlan.model_validate(plan)
        return validated_plan.model_dump()
    except Exception:
        return get_fallback_plan(difficulty_level)
