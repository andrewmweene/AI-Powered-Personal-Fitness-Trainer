"""Gemini planner for returning users, with a static fallback."""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from .plan_library import get_fallback_plan

logger = logging.getLogger(__name__)
DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


def _load_genai_module() -> Any:
    """Return the current Gemini SDK, or the legacy SDK if installed."""
    try:
        from google import genai
        return genai
    except ImportError:
        try:
            import google.generativeai as legacy_genai  # type: ignore
            return legacy_genai
        except ImportError:
            return None


def get_gemini_client(api_key: str) -> Any:
    """Create a client from the installed Gemini SDK.

    Args:
        api_key: Gemini API credential.

    Returns:
        A current SDK client or configured legacy module.

    Raises:
        RuntimeError: If neither supported SDK is installed.
    """
    genai = _load_genai_module()
    if genai is None:
        raise RuntimeError("Neither google-genai nor google-generativeai is installed")
    if hasattr(genai, "Client"):
        return genai.Client(api_key=api_key)
    genai.configure(api_key=api_key)
    return genai


def _prompt(user_profile: dict[str, Any], user_metrics: dict[str, Any]) -> str:
    """Build the constrained JSON prompt sent to Gemini."""
    fitness_level = user_profile.get("fitness_level", "beginner")
    goal = str(user_profile.get("goal", "general_fitness")).replace("_", " ")
    has_equipment = bool(user_profile.get("has_equipment", False))
    days = max(1, min(7, int(user_profile.get("days_per_week", 3))))
    duration = user_profile.get("workout_duration_minutes", 30)
    accuracy = float(user_metrics.get("avg_posture_accuracy", 0) or 0)
    sessions = float(user_metrics.get("sessions_per_week", 0) or 0)
    reps = float(user_metrics.get("avg_reps_per_session", 0) or 0)
    equipment_note = "Use all five exercises." if has_equipment else "Use only Squat and Push-up."
    accuracy_note = (
        "Reduce volume by 20 percent and emphasise form cues."
        if accuracy < 60
        else "Increase reps by 10-15 percent and include progression notes."
        if accuracy >= 80
        else "Maintain the current volume."
    )
    return f"""You are a certified personal trainer AI. Generate a personalised 7-day workout plan.

PROFILE:
- Fitness level: {fitness_level}
- Goal: {goal}
- Workout days: {days}; rest days: {7 - days}
- Session duration: {duration} minutes
- {equipment_note}

RECENT PERFORMANCE:
- Average posture accuracy: {accuracy:.1f}%
- Sessions per week: {sessions:.1f}
- Average reps per session: {reps:.1f}
- {accuracy_note}

Available exercises: Squat, Bicep Curl, Push-up, Dumbbell Fly, Dumbbell Kickback.
Schedule exactly {days} workout days. Include a form cue in every exercise notes field.
Respond with only valid JSON and all seven day keys plus a notes string.
Each day must be {{\"is_rest\": boolean, \"exercises\": [{{\"exercise\": string, \"sets\": integer, \"reps\": integer, \"notes\": string}}]}}.
"""


def _parse_response(response: Any, fitness_level: str) -> dict[str, Any]:
    """Parse and minimally validate a Gemini response."""
    raw = getattr(response, "text", "") or getattr(response, "output_text", "")
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.IGNORECASE)
    plan = json.loads(raw)
    if not isinstance(plan, dict) or any(day not in plan for day in DAYS):
        raise ValueError("Gemini response is missing one or more day keys")
    plan["difficulty"] = fitness_level
    plan["generated_by"] = "llm"
    plan.setdefault("notes", "Use controlled form and recover between training days.")
    return plan


def generate_weekly_plan(user_profile: dict[str, Any], user_metrics: dict[str, Any]) -> dict[str, Any]:
    """Generate a personalised plan with Gemini or return a static fallback.

    Args:
        user_profile: Onboarding fields and user identity information.
        user_metrics: Aggregated recent session performance metrics.

    Returns:
        A weekly plan containing all seven days and ``generated_by``.
    """
    fitness_level = str(user_profile.get("fitness_level", "beginner"))
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.info("GEMINI_API_KEY is not set; using static fallback")
        return get_fallback_plan(fitness_level)

    try:
        prompt = _prompt(user_profile, user_metrics)
        client = get_gemini_client(api_key)
        if hasattr(client, "models"):
            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        else:
            response = client.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
        return _parse_response(response, fitness_level)
    except Exception:
        logger.exception("Gemini weekly plan generation failed; using static fallback")
        return get_fallback_plan(fitness_level)
