"""LLM-based workout plan generation using Gemini API."""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

try:
    from google import genai as google_genai
except ImportError:  # pragma: no cover - compatibility fallback
    google_genai = None

API_KEY = os.getenv("GEMINI_API_KEY", "")


def _load_genai_module() -> Any:
    """Return the supported Gemini SDK when available, otherwise the legacy client."""
    if google_genai is not None:
        return google_genai

    try:
        import google.generativeai as legacy_genai  # type: ignore
    except ImportError:  # pragma: no cover - compatibility fallback
        return None
    return legacy_genai


def get_gemini_client(api_key: str) -> Any:
    """Create a Gemini client using the current SDK if installed."""
    genai_module = _load_genai_module()
    if genai_module is None:
        raise RuntimeError("Neither google-genai nor google-generativeai is installed.")

    if hasattr(genai_module, "Client"):
        return genai_module.Client(api_key=api_key)

    genai_module.configure(api_key=api_key)
    return genai_module


def get_fallback_plan(difficulty: str) -> dict[str, Any]:
    """Return a static fallback weekly plan when the LLM planner fails."""
    base_plan = {
        "beginner": {
            "monday": {
                "is_rest": False,
                "exercises": [
                    {"exercise": "Squat", "sets": 3, "reps": 10, "notes": "Focus on depth."},
                    {"exercise": "Bicep Curl", "sets": 3, "reps": 8, "notes": "Keep elbows close to your body."},
                    {"exercise": "Push-up", "sets": 3, "reps": 8, "notes": "Maintain a straight line from head to heels."},
                ],
            },
            "tuesday": {"is_rest": True, "exercises": []},
            "wednesday": {
                "is_rest": False,
                "exercises": [
                    {"exercise": "Squat", "sets": 3, "reps": 10, "notes": "Drive through your heels."},
                    {"exercise": "Bicep Curl", "sets": 3, "reps": 8, "notes": "Move with control."},
                    {"exercise": "Push-up", "sets": 3, "reps": 8, "notes": "Keep elbows tucked."},
                ],
            },
            "thursday": {"is_rest": True, "exercises": []},
            "friday": {
                "is_rest": False,
                "exercises": [
                    {"exercise": "Squat", "sets": 3, "reps": 10, "notes": "Keep your chest up."},
                    {"exercise": "Bicep Curl", "sets": 3, "reps": 8, "notes": "Pause at the top."},
                    {"exercise": "Push-up", "sets": 3, "reps": 8, "notes": "Lower with control."},
                ],
            },
            "saturday": {"is_rest": True, "exercises": []},
            "sunday": {"is_rest": True, "exercises": []},
            "difficulty": "beginner",
            "generated_by": "rule_based",
            "notes": "Use these foundation workouts to build consistency and form before increasing volume.",
        },
        "intermediate": {
            "monday": {
                "is_rest": False,
                "exercises": [
                    {"exercise": "Squat", "sets": 4, "reps": 12, "notes": "Keep knees tracking over toes."},
                    {"exercise": "Dumbbell Fly", "sets": 3, "reps": 12, "notes": "Maintain a soft bend in the elbows."},
                    {"exercise": "Bicep Curl", "sets": 3, "reps": 12, "notes": "Control the lowering phase."},
                ],
            },
            "tuesday": {
                "is_rest": False,
                "exercises": [
                    {"exercise": "Push-up", "sets": 4, "reps": 15, "notes": "Keep your core tight."},
                    {"exercise": "Dumbbell Kickback", "sets": 3, "reps": 12, "notes": "Fully extend the arm without swinging."},
                    {"exercise": "Bicep Curl", "sets": 3, "reps": 15, "notes": "Use a full range of motion."},
                ],
            },
            "wednesday": {"is_rest": True, "exercises": []},
            "thursday": {
                "is_rest": False,
                "exercises": [
                    {"exercise": "Squat", "sets": 4, "reps": 12, "notes": "Increase depth gradually."},
                    {"exercise": "Dumbbell Fly", "sets": 3, "reps": 12, "notes": "Focus on chest contraction."},
                    {"exercise": "Bicep Curl", "sets": 3, "reps": 12, "notes": "Keep elbows stationary."},
                ],
            },
            "friday": {
                "is_rest": False,
                "exercises": [
                    {"exercise": "Push-up", "sets": 4, "reps": 15, "notes": "Lower your chest close to the floor."},
                    {"exercise": "Dumbbell Kickback", "sets": 3, "reps": 12, "notes": "Squeeze the triceps at the top."},
                    {"exercise": "Bicep Curl", "sets": 3, "reps": 15, "notes": "Keep the movement steady."},
                ],
            },
            "saturday": {"is_rest": True, "exercises": []},
            "sunday": {"is_rest": True, "exercises": []},
            "difficulty": "intermediate",
            "generated_by": "rule_based",
            "notes": "Build strength consistently with balanced workout days and recovery.",
        },
        "advanced": {
            "monday": {
                "is_rest": False,
                "exercises": [
                    {"exercise": "Squat", "sets": 5, "reps": 12, "notes": "Use a challenging load while maintaining form."},
                    {"exercise": "Dumbbell Fly", "sets": 4, "reps": 12, "notes": "Keep tension on the chest."},
                ],
            },
            "tuesday": {
                "is_rest": False,
                "exercises": [
                    {"exercise": "Push-up", "sets": 5, "reps": 20, "notes": "Control tempo on every rep."},
                    {"exercise": "Dumbbell Kickback", "sets": 4, "reps": 12, "notes": "Focus on slow, full extensions."},
                ],
            },
            "wednesday": {
                "is_rest": False,
                "exercises": [
                    {"exercise": "Squat", "sets": 4, "reps": 15, "notes": "Aim for depth and power."},
                    {"exercise": "Push-up", "sets": 4, "reps": 18, "notes": "Keep a braced core."},
                ],
            },
            "thursday": {
                "is_rest": False,
                "exercises": [
                    {"exercise": "Dumbbell Fly", "sets": 4, "reps": 12, "notes": "Use a controlled arc."},
                    {"exercise": "Bicep Curl", "sets": 4, "reps": 15, "notes": "Maximize contraction."},
                ],
            },
            "friday": {
                "is_rest": False,
                "exercises": [
                    {"exercise": "Push-up", "sets": 5, "reps": 20, "notes": "Maintain perfect shoulder alignment."},
                    {"exercise": "Dumbbell Kickback", "sets": 4, "reps": 15, "notes": "Slow negatives for extra control."},
                ],
            },
            "saturday": {"is_rest": True, "exercises": []},
            "sunday": {"is_rest": True, "exercises": []},
            "difficulty": "advanced",
            "generated_by": "rule_based",
            "notes": "Push volume and intensity with smart recovery on the weekend.",
        },
    }

    return base_plan.get(difficulty, base_plan["beginner"])


def generate_weekly_plan(user_profile: dict[str, Any], difficulty: str) -> dict[str, Any]:
    """Generate a weekly workout plan through Gemini or fallback to a static plan."""
    username = user_profile.get("username", "User")
    age = user_profile.get("age", "unknown")
    goal = user_profile.get("goal", "general fitness")

    prompt = f"""
You are a certified personal trainer AI.
Generate a 7-day workout plan for the following user:
  Name: {username}
  Age: {age}
  Fitness level: {difficulty}
  Goal: {goal}

Available exercises: Squat, Bicep Curl, Push-up, Dumbbell Fly, Dumbbell Kickback.
Include 3-4 workout days and 3-4 rest/active recovery days.
For each workout day, prescribe 3-4 exercises with sets and reps appropriate
for a {difficulty} level user pursuing {goal}.

Respond ONLY with a valid JSON object. No preamble, no markdown, no explanation.
The JSON must have exactly these keys:
  monday, tuesday, wednesday, thursday, friday, saturday, sunday
Each key maps to an object with:
  "is_rest": boolean
  "exercises": array of {{"exercise": string, "sets": int, "reps": int, "notes": string}}
  (exercises array is empty if is_rest is true)
Also include "notes": string at the top level with general advice.
"""

    try:
        genai_module = _load_genai_module()
        if google_genai is not None:
            client = get_gemini_client(API_KEY)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
        elif legacy_genai is not None:
            legacy_genai.configure(api_key=API_KEY)
            model = legacy_genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
        else:
            logging.warning("No Gemini SDK installed; using fallback plan.")
            return get_fallback_plan(difficulty)

        raw = getattr(response, "text", "")
        if not raw:
            raw = getattr(response, "output_text", "")
        raw = raw.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        parsed = json.loads(raw)
        parsed["generated_by"] = "llm"
        return parsed
    except Exception:
        logging.exception("Gemini weekly plan generation failed, using fallback plan.")
        return get_fallback_plan(difficulty)
