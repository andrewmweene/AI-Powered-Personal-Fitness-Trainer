"""Recommendation package for workout difficulty and plan generation."""

from .engine import generate_plan
from .llm_planner import generate_weekly_plan
from .rule_based import predict_difficulty
from .schemas import ExerciseEntry, WeeklyPlan

__all__ = ["generate_plan", "generate_weekly_plan", "predict_difficulty", "ExerciseEntry", "WeeklyPlan"]
