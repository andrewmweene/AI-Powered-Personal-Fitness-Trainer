"""Two-phase recommendation orchestrator."""

from __future__ import annotations

import logging
from typing import Any

from . import llm_planner, plan_matcher

logger = logging.getLogger(__name__)
MIN_SESSIONS_FOR_AI = 5


def generate_plan(
    user_profile: dict[str, Any],
    user_metrics: dict[str, Any],
    session_count: int = 0,
) -> dict[str, Any]:
    """Choose a static onboarding plan or a performance-based AI plan.

    Args:
        user_profile: Onboarding profile including fitness and scheduling fields.
        user_metrics: Aggregated performance metrics for recent sessions.
        session_count: Total completed sessions; AI starts at five.

    Returns:
        A complete weekly plan with phase metadata.
    """
    fitness_level = str(user_profile.get("fitness_level", "beginner"))
    if session_count < MIN_SESSIONS_FOR_AI:
        logger.info("Phase 1: %s sessions, AI threshold is %s", session_count, MIN_SESSIONS_FOR_AI)
        plan = plan_matcher.match_plan(user_profile)
        plan["generated_by"] = "static_library"
        plan["phase"] = 1
        plan["sessions_until_ai"] = max(0, MIN_SESSIONS_FOR_AI - session_count)
        return plan

    logger.info("Phase 2: %s sessions, generating Gemini plan", session_count)
    plan = llm_planner.generate_weekly_plan(user_profile, user_metrics)
    plan["phase"] = 2
    plan["sessions_until_ai"] = 0
    plan.setdefault("difficulty", fitness_level)
    return plan
