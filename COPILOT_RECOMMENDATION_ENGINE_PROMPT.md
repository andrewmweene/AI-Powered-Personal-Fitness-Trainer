# Copilot Prompt — Recommendation Engine Implementation
## Static Plan Library + AI Switching Logic + Gemini Integration

> **How to use:**
> 1. Open GitHub Copilot Chat in VS Code (`Ctrl+Shift+I`)
> 2. Paste the entire prompt block below and send it
> 3. Copilot will create or modify every file listed
> 4. After generation, follow the VERIFICATION CHECKLIST at the bottom

---

## Prompt — paste into Copilot Chat

```
I need to implement the full recommendation engine for my AI Personal
Trainer project. The engine uses a two-phase approach:

  Phase 1 (new users, fewer than 5 sessions):
    → Use a static pre-built plan from plan_library.py matched to the
      user's onboarding profile (fitness level, goal, equipment, etc.)

  Phase 2 (returning users, 5+ sessions):
    → Use the Google Gemini API to generate a personalised plan based
      on the user's real session performance data

The switching happens automatically inside the engine — the frontend
and the recommendation API endpoint never need to know which phase
is active.

Do not modify any React frontend files, any database models, any
auth logic, or any pose engine files. Only the files listed below.

---

## File 1: `recommendation/plan_library.py`  [CREATE]

Create this file. It defines PLAN_LIBRARY — a Python dict of 21
pre-built weekly workout plans. This is the source of truth for
Phase 1 recommendations.

### Structure of each plan

Each key follows the format:
  "{fitness_level}__{goal}__{equipment}__{days}d__{duration}min"

Examples:
  "beginner__weight_loss__no_equipment__3d__30min"
  "intermediate__muscle_gain__with_equipment__4d__60min"
  "advanced__strength_training__with_equipment__5d__60min"

Each value is a dict with these keys:
  monday, tuesday, wednesday, thursday, friday, saturday, sunday
  Each day is: {"is_rest": bool, "exercises": [...]}
  Each exercise is: {"exercise": str, "sets": int, "reps": int, "notes": str}

  Top-level keys also include:
  "notes": str  (1-2 sentences of general plan advice)
  "generated_by": "static_library"
  "match_key": the key string used for this plan

### Exercises available
Only these 5 exercises exist in the system:
  Squat, Bicep Curl, Push-up, Dumbbell Fly, Dumbbell Kickback

No-equipment plans: use ONLY Squat and Push-up
With-equipment plans: use all 5 exercises distributed across workout days

### Rep and set schemes by goal (based on exercise science)

| Goal               | Sets | Reps  | Rest    |
|--------------------|------|-------|---------|
| weight_loss        | 3    | 15-20 | 30-45s  |
| muscle_gain        | 4    | 8-12  | 60-90s  |
| strength_training  | 4-5  | 4-6   | 2-3 min |
| endurance          | 3    | 20-25 | 20-30s  |
| general_fitness    | 3    | 12-15 | 45-60s  |
| flexibility        | 3    | 10-12 | 60s     |
| sports_specific    | 4    | 8-10  | 60-90s  |

### Workout day structures

Beginner (3 days): workout Mon/Wed/Fri, rest all other days
  2-3 exercises per day
  3 sets, 8-15 reps depending on goal

Intermediate (4 days): workout Mon/Tue/Thu/Fri, rest Wed/Sat/Sun
  3-4 exercises per day
  3-4 sets, 10-15 reps depending on goal

Advanced (5 days): workout Mon-Fri, rest Sat/Sun
  4 exercises per day
  4-5 sets, 8-20 reps depending on goal

### Form cue notes for each exercise

Use these specific notes in the "notes" field — vary them across
fitness levels so each plan feels distinct:

Squat:
  beginner:     "Keep chest up, drive through heels at the top"
  intermediate: "Go below parallel, brace core throughout"
  advanced:     "Pause 2 seconds at the bottom, explosive drive up"

Push-up:
  beginner:     "Keep elbows at 45 degrees, full range of motion"
  intermediate: "3-second eccentric, chest to floor every rep"
  advanced:     "Controlled tempo — 3 seconds down, 1 second up"

Bicep Curl:
  beginner:     "Pin elbows to sides, full extension at bottom"
  intermediate: "Supinate at the top, slow 3-second negative"
  advanced:     "Alternating arms, pause 1 second at peak contraction"

Dumbbell Fly:
  beginner:     "Slight elbow bend throughout, feel the chest stretch"
  intermediate: "Full stretch at bottom, squeeze pecs at top"
  advanced:     "Slow eccentric, pause at full stretch position"

Dumbbell Kickback:
  beginner:     "Upper arm parallel to floor, control the movement"
  intermediate: "Full lockout at extension, pause 1 second"
  advanced:     "Isometric hold at top for 2 seconds each rep"

### The 21 plans to generate

Generate all 21 plans below. Each must be a complete dict with all
7 days, following the workout day structures above.

BEGINNER plans (3d, 30min):
  beginner__weight_loss__no_equipment__3d__30min
    Mon/Wed/Fri: Squat 3x15, Push-up 3x12
    goal notes: "Focus on keeping heart rate elevated between sets.
                 Rest only 30-45 seconds."

  beginner__weight_loss__with_equipment__3d__30min
    Mon: Squat 3x15, Bicep Curl 3x15
    Wed: Push-up 3x12, Dumbbell Fly 3x15
    Fri: Squat 3x12, Dumbbell Kickback 3x15
    goal notes: "Circuit-style training burns more calories. Keep
                 rest periods short."

  beginner__muscle_gain__with_equipment__3d__45min
    Mon: Squat 4x10, Dumbbell Fly 4x10
    Wed: Bicep Curl 4x10, Push-up 4x10
    Fri: Squat 4x8, Dumbbell Kickback 4x10
    goal notes: "Progressive overload is key. Add one rep per week
                 when current reps feel easy."

  beginner__strength_training__with_equipment__3d__45min
    Mon: Squat 4x6, Push-up 4x6
    Wed: Bicep Curl 4x5, Dumbbell Kickback 4x5
    Fri: Squat 4x5, Dumbbell Fly 4x6
    goal notes: "Rest fully between sets (2-3 minutes). Quality over
                 quantity — never sacrifice form."

  beginner__general_fitness__no_equipment__3d__30min
    Mon/Wed/Fri: Squat 3x12, Push-up 3x12
    goal notes: "Balanced training for overall health. Stay consistent
                 rather than pushing too hard too soon."

  beginner__flexibility__no_equipment__3d__30min
    Mon/Wed/Fri: Squat 3x12 slow, Push-up 3x10 slow
    Use slow tempo notes — e.g. "3-second eccentric, pause at bottom"
    goal notes: "Move slowly through full range of motion. The stretch
                 at end range is where flexibility improves."

  beginner__endurance__no_equipment__3d__30min
    Mon/Wed/Fri: Squat 3x20, Push-up 3x18
    goal notes: "Keep rest periods to 20-30 seconds. Build up the
                 ability to sustain effort over time."

INTERMEDIATE plans (4d, 45min):
  intermediate__weight_loss__no_equipment__4d__45min
    Mon/Tue: Squat 3x18, Push-up 3x15
    Thu/Fri: Squat 3x20, Push-up 3x18
    Wed/Sat/Sun: rest
    goal notes: "Four sessions keeps metabolism elevated. Short rest
                 periods maximise calorie burn."

  intermediate__weight_loss__with_equipment__4d__45min
    Mon: Squat 3x18, Bicep Curl 3x18
    Tue: Push-up 3x15, Dumbbell Fly 3x18
    Thu: Squat 3x15, Dumbbell Kickback 3x18
    Fri: Push-up 3x18, Bicep Curl 3x15
    goal notes: "Vary exercises daily to prevent adaptation. Keep
                 heart rate elevated throughout."

  intermediate__muscle_gain__with_equipment__4d__60min
    Mon: Squat 4x10, Dumbbell Fly 4x10
    Tue: Bicep Curl 4x10, Dumbbell Kickback 4x10
    Thu: Squat 4x12, Push-up 4x12
    Fri: Bicep Curl 4x12, Dumbbell Fly 4x10
    goal notes: "Split training allows muscle groups to recover.
                 Target 10-12 reps to maximise hypertrophy."

  intermediate__strength_training__with_equipment__4d__60min
    Mon: Squat 4x5, Dumbbell Fly 4x6
    Tue: Bicep Curl 4x5, Dumbbell Kickback 4x5
    Thu: Squat 5x4, Push-up 4x8
    Fri: Bicep Curl 4x6, Dumbbell Kickback 5x4
    goal notes: "Strength is built at low reps with heavy resistance.
                 Rest 2-3 minutes between every set."

  intermediate__general_fitness__no_equipment__4d__45min
    Mon/Tue: Squat 3x15, Push-up 3x12
    Thu/Fri: Squat 3x12, Push-up 3x15
    goal notes: "Balanced workout frequency for sustainable progress.
                 Alternate between squat-focused and push-focused days."

  intermediate__flexibility__no_equipment__4d__30min
    Mon/Tue/Thu/Fri: Squat 3x12 slow, Push-up 3x10 slow
    All exercises use slow-tempo notes
    goal notes: "Four days builds the habit without overloading recovery.
                 Prioritise quality of movement over quantity."

  intermediate__endurance__no_equipment__4d__45min
    Mon/Tue: Squat 3x22, Push-up 3x20
    Thu/Fri: Squat 3x25, Push-up 3x22
    goal notes: "Progressive rep increase week over week. Endurance
                 adapts fastest with consistent high-volume training."

ADVANCED plans (5d, 60min):
  advanced__weight_loss__with_equipment__5d__60min
    Mon: Squat 4x20, Bicep Curl 3x20
    Tue: Push-up 4x18, Dumbbell Fly 3x20
    Wed: Squat 4x18, Dumbbell Kickback 4x20
    Thu: Push-up 4x20, Bicep Curl 4x18
    Fri: Squat 4x20, Dumbbell Fly 4x18
    goal notes: "Five days maximises weekly volume. Keep rest to 30
                 seconds to sustain fat-burning intensity."

  advanced__muscle_gain__with_equipment__5d__60min
    Mon: Squat 4x10, Dumbbell Fly 4x10
    Tue: Bicep Curl 4x12, Dumbbell Kickback 4x10
    Wed: Squat 5x8, Push-up 4x12
    Thu: Dumbbell Fly 4x12, Bicep Curl 4x10
    Fri: Squat 4x12, Dumbbell Kickback 4x12
    goal notes: "High-frequency training with adequate recovery per
                 muscle group. Aim to increase weight every two weeks."

  advanced__strength_training__with_equipment__5d__60min
    Mon: Squat 5x5, Dumbbell Fly 4x6
    Tue: Bicep Curl 5x4, Dumbbell Kickback 5x4
    Wed: Squat 5x4, Push-up 5x6
    Thu: Dumbbell Fly 5x5, Bicep Curl 4x5
    Fri: Squat 5x3, Dumbbell Kickback 5x5
    goal notes: "Maximum strength requires maximum rest. Never skip
                 rest days — strength is built during recovery."

  advanced__endurance__no_equipment__5d__60min
    Mon-Fri: Squat 4x25, Push-up 4x20
    goal notes: "Daily training at this level builds exceptional
                 muscular endurance. Monitor recovery closely."

  advanced__general_fitness__with_equipment__5d__60min
    Mon: Squat 4x12, Bicep Curl 4x12
    Tue: Push-up 4x15, Dumbbell Fly 4x12
    Wed: Squat 4x10, Dumbbell Kickback 4x12
    Thu: Bicep Curl 4x15, Push-up 4x12
    Fri: Squat 4x15, Dumbbell Fly 4x10
    goal notes: "Well-rounded programme hitting all muscle groups
                 across the week with manageable daily volume."

  advanced__flexibility__no_equipment__4d__45min
    Mon/Tue/Thu/Fri: Squat 4x12 slow, Push-up 3x12 slow
    Use advanced slow-tempo form cue notes
    goal notes: "Advanced flexibility work requires attention to
                 the end-range position on every single repetition."

  advanced__sports_specific__with_equipment__5d__60min
    Mon: Squat 4x8 explosive, Dumbbell Kickback 4x8
    Tue: Bicep Curl 4x8, Push-up 4x10 explosive
    Wed: Squat 5x6 explosive, Dumbbell Fly 4x8
    Thu: Dumbbell Kickback 4x10, Bicep Curl 4x10
    Fri: Squat 4x6 explosive, Push-up 4x8 explosive
    Use notes like: "Explosive concentric phase, controlled eccentric"
    goal notes: "Power development requires maximum intent on every
                 rep. Reset fully between repetitions."

Also implement these two helper functions at the bottom of the file:

def get_fallback_plan(fitness_level: str) -> dict:
    """
    Returns a general_fitness plan for the given fitness level.
    Used when the LLM fails and no closer match is found.
    Falls back to beginner if level not found.
    """
    fallbacks = {
        "beginner":     "beginner__general_fitness__no_equipment__3d__30min",
        "intermediate": "intermediate__general_fitness__no_equipment__4d__45min",
        "advanced":     "advanced__general_fitness__with_equipment__5d__60min",
    }
    key = fallbacks.get(fitness_level, fallbacks["beginner"])
    return PLAN_LIBRARY[key]

def list_plan_keys() -> list[str]:
    """Returns all available plan keys. Useful for debugging."""
    return list(PLAN_LIBRARY.keys())

---

## File 2: `recommendation/plan_matcher.py`  [CREATE]

Create this file. It contains the matching logic that picks the best
plan from PLAN_LIBRARY given a user's profile.

```python
"""
plan_matcher.py

Matches a user profile to the closest plan in PLAN_LIBRARY.
Uses a 5-step fallback chain to always return a valid plan.
Never returns None.
"""
from .plan_library import PLAN_LIBRARY, get_fallback_plan
import logging

logger = logging.getLogger(__name__)

MIN_DAYS_BRACKET = [3, 4, 5]
MIN_DURATION_BRACKET = [30, 45, 60]


def _closest(value: int, options: list[int]) -> int:
    """Returns the option closest to value."""
    return min(options, key=lambda x: abs(x - value))


def match_plan(profile: dict) -> dict:
    """
    Match a user profile to the best available plan in PLAN_LIBRARY.

    Args:
        profile: dict with keys:
            fitness_level (str): beginner | intermediate | advanced
            goal (str): weight_loss | muscle_gain | strength_training |
                        endurance | general_fitness | flexibility | sports_specific
            has_equipment (bool)
            days_per_week (int): 1-7
            workout_duration_minutes (int): 15-90

    Returns:
        A plan dict from PLAN_LIBRARY. Never None.
    """
    fitness_level = profile.get("fitness_level", "beginner")
    goal          = profile.get("goal", "general_fitness")
    has_equipment = profile.get("has_equipment", False)
    days          = profile.get("days_per_week", 3)
    duration      = profile.get("workout_duration_minutes", 30)

    equipment_str    = "with_equipment" if has_equipment else "no_equipment"
    days_bracket     = _closest(days, MIN_DAYS_BRACKET)
    duration_bracket = _closest(duration, MIN_DURATION_BRACKET)

    # Step 1: exact match
    key = f"{fitness_level}__{goal}__{equipment_str}__{days_bracket}d__{duration_bracket}min"
    if key in PLAN_LIBRARY:
        logger.info(f"Plan matched exactly: {key}")
        return PLAN_LIBRARY[key]

    # Step 2: try no_equipment fallback (equipment is optional)
    fallback_key = f"{fitness_level}__{goal}__no_equipment__{days_bracket}d__{duration_bracket}min"
    if fallback_key in PLAN_LIBRARY:
        logger.info(f"Plan matched (no_equipment fallback): {fallback_key}")
        return PLAN_LIBRARY[fallback_key]

    # Step 3: try with_equipment fallback
    fallback_key = f"{fitness_level}__{goal}__with_equipment__{days_bracket}d__{duration_bracket}min"
    if fallback_key in PLAN_LIBRARY:
        logger.info(f"Plan matched (with_equipment fallback): {fallback_key}")
        return PLAN_LIBRARY[fallback_key]

    # Step 4: drop days and duration, match only fitness_level + goal
    for key in PLAN_LIBRARY:
        if key.startswith(f"{fitness_level}__{goal}"):
            logger.info(f"Plan matched (level+goal only): {key}")
            return PLAN_LIBRARY[key]

    # Step 5: match fitness_level + general_fitness
    for key in PLAN_LIBRARY:
        if key.startswith(f"{fitness_level}__general_fitness"):
            logger.info(f"Plan matched (general_fitness fallback): {key}")
            return PLAN_LIBRARY[key]

    # Last resort: beginner general fitness
    logger.warning(f"No match found for profile {profile}. Using ultimate fallback.")
    return get_fallback_plan("beginner")
```

---

## File 3: `recommendation/llm_planner.py`  [CREATE or REPLACE]

Create or fully replace this file. It generates AI plans using Gemini.

```python
"""
llm_planner.py

Generates personalised weekly workout plans using the Google Gemini API.
Called only for returning users (session_count >= MIN_SESSIONS_FOR_AI).
Falls back to the static plan library if the API call fails.
"""
import os, json, re, logging
from .plan_library import get_fallback_plan

logger = logging.getLogger(__name__)


def generate_weekly_plan(user_profile: dict, user_metrics: dict) -> dict:
    """
    Call Gemini to generate a personalised weekly plan.

    Args:
        user_profile: dict with username, age, fitness_level, goal,
                      has_equipment, days_per_week, workout_duration_minutes
        user_metrics: dict with avg_posture_accuracy, sessions_per_week,
                      avg_reps_per_session

    Returns:
        Plan dict matching WeeklyPlan schema, with generated_by = "llm"
        Falls back to static plan on any error.
    """
    try:
        import google.generativeai as genai
    except ImportError:
        logger.error("google-generativeai not installed. Run: pip install google-generativeai")
        return get_fallback_plan(user_profile.get("fitness_level", "beginner"))

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not set in environment. Falling back to static plan.")
        return get_fallback_plan(user_profile.get("fitness_level", "beginner"))

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    fitness_level = user_profile.get("fitness_level", "beginner")
    goal          = user_profile.get("goal", "general_fitness").replace("_", " ")
    has_equipment = user_profile.get("has_equipment", False)
    days          = user_profile.get("days_per_week", 3)
    duration      = user_profile.get("workout_duration_minutes", 30)

    avg_accuracy    = user_metrics.get("avg_posture_accuracy", 0)
    sessions_pw     = user_metrics.get("sessions_per_week", 0)
    avg_reps        = user_metrics.get("avg_reps_per_session", 0)

    equipment_note = (
        "The user has access to dumbbells and gym equipment. Use all 5 exercises."
        if has_equipment
        else "The user has NO equipment. Use ONLY Squat and Push-up."
    )

    accuracy_note = (
        "Accuracy is below 60%: reduce volume by 20% and emphasise form correction cues."
        if avg_accuracy < 60
        else "Accuracy is above 80%: increase reps by 10-15% and add progression notes."
        if avg_accuracy >= 80
        else "Accuracy is in the normal range: maintain current volume."
    )

    prompt = f"""You are a certified personal trainer AI.
Generate a personalised 7-day workout plan for this user.

PROFILE:
- Fitness level: {fitness_level}
- Goal: {goal}
- Days available per week: {days}
- Preferred session duration: {duration} minutes
- {equipment_note}

RECENT PERFORMANCE (last 14 sessions):
- Average posture accuracy: {avg_accuracy:.1f}%
- Sessions per week: {sessions_pw:.1f}
- Average reps per session: {avg_reps:.1f}
- {accuracy_note}

AVAILABLE EXERCISES (the only exercises in the system):
  Squat, Bicep Curl, Push-up, Dumbbell Fly, Dumbbell Kickback

INSTRUCTIONS:
1. Schedule {days} workout days and {7 - days} rest days.
2. Use sets and reps appropriate for {fitness_level} level and {goal} goal.
3. Distribute exercises so no muscle group is trained two days in a row.
4. Include a specific form cue in the notes field of every exercise entry.
5. The plan-level notes field must give 1-2 sentences of general advice.

RESPOND WITH ONLY VALID JSON. No markdown. No explanation. No preamble.
JSON structure (all 7 day keys required):
{{
  "monday":    {{"is_rest": false, "exercises": [{{"exercise": "Squat", "sets": 3, "reps": 12, "notes": "form cue"}}]}},
  "tuesday":   {{"is_rest": true,  "exercises": []}},
  "wednesday": {{"is_rest": false, "exercises": [...]}},
  "thursday":  {{"is_rest": true,  "exercises": []}},
  "friday":    {{"is_rest": false, "exercises": [...]}},
  "saturday":  {{"is_rest": true,  "exercises": []}},
  "sunday":    {{"is_rest": true,  "exercises": []}},
  "notes": "General plan advice here."
}}"""

    try:
        response = model.generate_content(prompt)
        raw = re.sub(r"```json|```", "", response.text).strip()
        plan = json.loads(raw)

        # Validate all 7 days are present
        required_days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
        for day in required_days:
            if day not in plan:
                raise ValueError(f"Missing day in LLM response: {day}")

        plan["generated_by"] = "llm"
        logger.info("Gemini plan generated successfully.")
        return plan

    except json.JSONDecodeError as e:
        logger.error(f"Gemini returned invalid JSON: {e}. Raw: {response.text[:200]}")
        return get_fallback_plan(fitness_level)
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return get_fallback_plan(fitness_level)
```

---

## File 4: `recommendation/engine.py`  [CREATE or REPLACE]

Create or fully replace this file. It is the orchestrator that decides
which plan source to use based on session count.

```python
"""
engine.py

Main recommendation orchestrator.
Decides between static plan library (Phase 1) and Gemini AI (Phase 2)
based on how many sessions the user has completed.
"""
import logging
from . import plan_matcher, llm_planner
from analytics.metrics import build_user_metrics_dict

logger = logging.getLogger(__name__)

MIN_SESSIONS_FOR_AI = 5


def generate_plan(
    user_profile: dict,
    user_metrics: dict,
    session_count: int
) -> dict:
    """
    Generate a weekly workout plan for the user.

    Phase 1 (session_count < MIN_SESSIONS_FOR_AI):
      Uses the static plan library. Fast, deterministic, no API call.

    Phase 2 (session_count >= MIN_SESSIONS_FOR_AI):
      Uses the Gemini API to generate a plan personalised to actual
      performance data. Falls back to static plan on error.

    Args:
        user_profile: dict with fitness_level, goal, has_equipment,
                      days_per_week, workout_duration_minutes,
                      username, age
        user_metrics: dict with avg_posture_accuracy, sessions_per_week,
                      avg_reps_per_session
        session_count: total number of exercise sessions completed

    Returns:
        A valid plan dict with all 7 day keys and generated_by field.
    """
    fitness_level = user_profile.get("fitness_level", "beginner")

    if session_count < MIN_SESSIONS_FOR_AI:
        logger.info(
            f"Phase 1: user has {session_count} sessions "
            f"(threshold: {MIN_SESSIONS_FOR_AI}). Using static plan."
        )
        plan = plan_matcher.match_plan({
            "fitness_level":            fitness_level,
            "goal":                     user_profile.get("goal", "general_fitness"),
            "has_equipment":            user_profile.get("has_equipment", False),
            "days_per_week":            user_profile.get("days_per_week", 3),
            "workout_duration_minutes": user_profile.get("workout_duration_minutes", 30),
        })
        plan["generated_by"] = "static_library"
        plan["phase"] = 1
        plan["sessions_until_ai"] = MIN_SESSIONS_FOR_AI - session_count
        return plan

    else:
        logger.info(
            f"Phase 2: user has {session_count} sessions. "
            f"Using Gemini AI recommendation."
        )
        plan = llm_planner.generate_weekly_plan(user_profile, user_metrics)
        plan["phase"] = 2
        plan["sessions_until_ai"] = 0
        return plan
```

---

## File 5: `analytics/metrics.py`  [CREATE or REPLACE]

Create or fully replace this file. It provides the pure functions
that calculate user metrics from session data. These metrics feed
both the recommendation engine and the dashboard.

```python
"""
metrics.py

Pure functions for calculating user performance metrics from
exercise session data. No database calls — accepts list of dicts.
"""
from datetime import datetime, date, timedelta
import statistics


def calculate_total_sessions(sessions: list[dict]) -> int:
    return len(sessions)


def calculate_total_reps(sessions: list[dict]) -> int:
    return sum(s.get("total_reps", 0) or 0 for s in sessions)


def calculate_average_accuracy(sessions: list[dict]) -> float:
    accuracies = [s.get("posture_accuracy") for s in sessions
                  if s.get("posture_accuracy") is not None]
    return round(statistics.mean(accuracies), 1) if accuracies else 0.0


def calculate_sessions_per_week(sessions: list[dict]) -> float:
    """Count sessions in the last 7 days."""
    cutoff = datetime.utcnow() - timedelta(days=7)
    recent = []
    for s in sessions:
        created = s.get("created_at")
        if isinstance(created, str):
            created = datetime.fromisoformat(created.replace("Z", "+00:00"))
        if created and created.replace(tzinfo=None) >= cutoff:
            recent.append(s)
    return round(len(recent), 1)


def calculate_average_reps_per_session(sessions: list[dict]) -> float:
    if not sessions:
        return 0.0
    return round(calculate_total_reps(sessions) / len(sessions), 1)


def build_user_metrics_dict(sessions: list[dict]) -> dict:
    """
    Build the metrics dict expected by the recommendation engine.
    This is the primary interface between analytics and recommendations.
    """
    return {
        "avg_posture_accuracy":    calculate_average_accuracy(sessions),
        "sessions_per_week":       calculate_sessions_per_week(sessions),
        "avg_reps_per_session":    calculate_average_reps_per_session(sessions),
        "total_sessions":          calculate_total_sessions(sessions),
        "total_reps":              calculate_total_reps(sessions),
    }


def calculate_streak(sessions: list[dict]) -> tuple[int, int]:
    """
    Returns (current_streak_days, best_streak_days).
    A streak day = any calendar day with at least one session.
    """
    if not sessions:
        return 0, 0

    dates = set()
    for s in sessions:
        created = s.get("created_at")
        if isinstance(created, str):
            created = datetime.fromisoformat(created.replace("Z", "+00:00"))
        if created:
            dates.add(created.date() if hasattr(created, 'date') else created)

    sorted_dates = sorted(dates, reverse=True)
    today = date.today()

    # Current streak
    current = 0
    check = today
    for d in sorted_dates:
        if d == check or d == check - timedelta(days=1):
            current += 1
            check = d - timedelta(days=1)
        else:
            break

    # Best streak
    best = 0
    streak = 1
    all_sorted = sorted(dates)
    for i in range(1, len(all_sorted)):
        if all_sorted[i] - all_sorted[i-1] == timedelta(days=1):
            streak += 1
            best = max(best, streak)
        else:
            streak = 1
    best = max(best, current, 1 if dates else 0)

    return current, best


def calculate_weekly_breakdown(sessions: list[dict]) -> list[dict]:
    """
    Returns one dict per day for the last 7 days.
    Days with no sessions appear with session_count=0, avg_accuracy=0.
    """
    result = []
    for i in range(6, -1, -1):
        target_date = date.today() - timedelta(days=i)
        day_sessions = []
        for s in sessions:
            created = s.get("created_at")
            if isinstance(created, str):
                created = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if created and created.date() == target_date:
                day_sessions.append(s)
        avg_acc = calculate_average_accuracy(day_sessions) if day_sessions else 0
        result.append({
            "date":          target_date.isoformat(),
            "session_count": len(day_sessions),
            "avg_accuracy":  avg_acc,
        })
    return result


def calculate_accuracy_trend(sessions: list[dict], n: int = 30) -> list[dict]:
    """Last n sessions ordered by created_at ascending."""
    sorted_sessions = sorted(
        sessions,
        key=lambda s: s.get("created_at") or ""
    )[-n:]
    return [
        {"session_num": i + 1, "accuracy": round(s.get("posture_accuracy") or 0, 1)}
        for i, s in enumerate(sorted_sessions)
    ]


def calculate_by_exercise(sessions: list[dict]) -> list[dict]:
    """Group sessions by exercise_type, return count and avg accuracy."""
    groups = {}
    for s in sessions:
        ex = s.get("exercise_type", "Unknown")
        if ex not in groups:
            groups[ex] = []
        groups[ex].append(s)
    result = []
    for ex, group in groups.items():
        result.append({
            "exercise":    ex,
            "count":       len(group),
            "avg_accuracy": calculate_average_accuracy(group),
        })
    return sorted(result, key=lambda x: x["count"], reverse=True)
```

---

## File 6: `backend/routers/recommendations.py`  [CREATE or REPLACE]

Create or fully replace this file. The endpoint now passes session_count
to the engine and returns the phase and sessions_until_ai in the response.

```python
"""
recommendations.py

FastAPI router for workout plan generation and retrieval.
Handles caching, switching between Phase 1 (static) and Phase 2 (AI),
and plan refresh requests.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from uuid import uuid4

from backend.database import get_db
from backend.models import WorkoutPlan, ExerciseSession, UserProfile
from backend.dependencies import get_current_user
from recommendation.engine import generate_plan
from analytics.metrics import build_user_metrics_dict

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def _get_this_monday() -> date:
    today = date.today()
    return today - timedelta(days=today.weekday())


def _build_plan_for_user(user, db: Session) -> dict:
    """
    Shared logic for both GET and POST (refresh) endpoints.
    Fetches session data, builds metrics, calls the engine.
    """
    # Count total sessions
    session_count = db.query(ExerciseSession)\
        .filter(ExerciseSession.user_id == user.id)\
        .count()

    # Fetch user profile
    profile = db.query(UserProfile)\
        .filter(UserProfile.user_id == user.id).first()

    if not profile:
        # No profile yet — return a default beginner plan
        from recommendation.plan_library import get_fallback_plan
        return get_fallback_plan("beginner")

    # Get recent sessions for metrics
    recent_sessions = db.query(ExerciseSession)\
        .filter(ExerciseSession.user_id == user.id)\
        .order_by(ExerciseSession.created_at.desc())\
        .limit(14).all()

    sessions_list = [
        {
            "exercise_type":    s.exercise_type,
            "total_reps":       s.total_reps,
            "correct_reps":     s.correct_reps,
            "posture_accuracy": s.posture_accuracy,
            "duration_seconds": s.duration_seconds,
            "created_at":       s.created_at.isoformat() if s.created_at else None,
        }
        for s in recent_sessions
    ]

    user_metrics = build_user_metrics_dict(sessions_list)

    user_profile_dict = {
        "username":                 user.username,
        "age":                      profile.age,
        "fitness_level":            profile.fitness_level,
        "goal":                     profile.goal,
        "has_equipment":            profile.has_equipment,
        "days_per_week":            profile.days_per_week,
        "workout_duration_minutes": profile.workout_duration_minutes,
    }

    return generate_plan(user_profile_dict, user_metrics, session_count)


@router.get("/plan")
def get_plan(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Returns the current week's workout plan.
    Serves from cache if this week's plan already exists.
    Generates a new plan (static or AI) if not cached.
    """
    this_monday = _get_this_monday()

    # Check cache
    cached = db.query(WorkoutPlan)\
        .filter(
            WorkoutPlan.user_id == current_user.id,
            WorkoutPlan.week_start_date == this_monday
        ).first()

    if cached:
        return cached.plan_data

    # Generate new plan
    plan = _build_plan_for_user(current_user, db)

    # Save to cache
    db.add(WorkoutPlan(
        id=uuid4(),
        user_id=current_user.id,
        plan_data=plan,
        week_start_date=this_monday,
    ))
    db.commit()
    return plan


@router.post("/plan/refresh")
def refresh_plan(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Forces regeneration of the current week's plan.
    Deletes the cached plan and generates a fresh one.
    Used after significant performance changes or user request.
    """
    this_monday = _get_this_monday()

    # Delete cached plan
    existing = db.query(WorkoutPlan)\
        .filter(
            WorkoutPlan.user_id == current_user.id,
            WorkoutPlan.week_start_date == this_monday
        ).first()
    if existing:
        db.delete(existing)
        db.commit()

    # Generate fresh plan
    plan = _build_plan_for_user(current_user, db)

    db.add(WorkoutPlan(
        id=uuid4(),
        user_id=current_user.id,
        plan_data=plan,
        week_start_date=this_monday,
    ))
    db.commit()
    return plan


@router.get("/status")
def get_recommendation_status(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Returns the user's current recommendation phase and how many
    more sessions until AI recommendations activate.
    Used by the frontend to show a progress indicator.
    """
    from recommendation.engine import MIN_SESSIONS_FOR_AI
    session_count = db.query(ExerciseSession)\
        .filter(ExerciseSession.user_id == current_user.id)\
        .count()
    return {
        "session_count":      session_count,
        "min_for_ai":         MIN_SESSIONS_FOR_AI,
        "phase":              2 if session_count >= MIN_SESSIONS_FOR_AI else 1,
        "sessions_until_ai":  max(0, MIN_SESSIONS_FOR_AI - session_count),
        "ai_active":          session_count >= MIN_SESSIONS_FOR_AI,
    }
```

---

## File 7: `recommendation/__init__.py`  [CREATE if not exists]

```python
"""
recommendation package

Phase 1: plan_matcher + plan_library (static, no API)
Phase 2: llm_planner (Gemini API, requires GEMINI_API_KEY)
Orchestrated by: engine.py
"""
```

---

## Coding standards

- Every function must have a Google-style docstring with Args and Returns
- All functions that receive session data accept list[dict] (not ORM objects)
  to keep analytics.py decoupled from SQLAlchemy
- plan_library.py: every plan must have all 7 day keys
- plan_matcher.py: must never return None — the 5-step fallback ensures this
- llm_planner.py: all Gemini calls in try/except — always fall back gracefully
- engine.py: log which phase and why at INFO level on every call
- recommendations.py: the GET /plan endpoint must never return 500 —
  if plan generation fails, return the beginner fallback plan
```

---

## VERIFICATION CHECKLIST

After Copilot generates the files, verify each item:

### plan_library.py
- [ ] All 21 plan keys present — run: `python -c "from recommendation.plan_library import PLAN_LIBRARY; print(len(PLAN_LIBRARY))"`  should print 21
- [ ] All plans have all 7 day keys — run: `python -c "from recommendation.plan_library import PLAN_LIBRARY; [print(k, list(v.keys())) for k,v in PLAN_LIBRARY.items()]"`
- [ ] No-equipment plans contain only Squat and Push-up

### plan_matcher.py
- [ ] Never returns None for any valid input — run:
  ```
  python -c "
  from recommendation.plan_matcher import match_plan
  profiles = [
    {'fitness_level':'beginner','goal':'weight_loss','has_equipment':False,'days_per_week':3,'workout_duration_minutes':30},
    {'fitness_level':'intermediate','goal':'muscle_gain','has_equipment':True,'days_per_week':5,'workout_duration_minutes':75},
    {'fitness_level':'advanced','goal':'sports_specific','has_equipment':False,'days_per_week':7,'workout_duration_minutes':120},
  ]
  for p in profiles:
    result = match_plan(p)
    print(result.get('match_key') or result.get('generated_by'), '— OK' if result else 'FAIL')
  "
  ```

### engine.py
- [ ] Phase 1 triggered when session_count < 5
- [ ] Phase 2 triggered when session_count >= 5
- [ ] plan dict always has generated_by and phase keys

### llm_planner.py
- [ ] Falls back to static plan when GEMINI_API_KEY is not set
- [ ] Test with key set: `python -c "from recommendation.llm_planner import generate_weekly_plan; import json; print(json.dumps(generate_weekly_plan({'fitness_level':'beginner','goal':'weight_loss','has_equipment':False,'days_per_week':3,'workout_duration_minutes':30,'username':'Test','age':22}, {'avg_posture_accuracy':72.0,'sessions_per_week':3.0,'avg_reps_per_session':10.0}), indent=2))"`

### recommendations.py
- [ ] GET /recommendations/plan returns 200 with a valid plan
- [ ] GET /recommendations/status returns session_count, phase, ai_active
- [ ] POST /recommendations/plan/refresh regenerates and returns new plan
- [ ] All tested via FastAPI docs at localhost:8000/docs
```

---

## File 8: `backend/routers/analytics.py`  [CREATE or REPLACE]

Create or fully replace this file. It exposes all analytics data
needed by the React dashboard, using the pure functions from
analytics/metrics.py.

```python
"""
analytics.py

FastAPI router for dashboard analytics endpoints.
All computation delegated to analytics/metrics.py pure functions.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import ExerciseSession
from backend.dependencies import get_current_user
from analytics.metrics import (
    build_user_metrics_dict,
    calculate_streak,
    calculate_weekly_breakdown,
    calculate_accuracy_trend,
    calculate_by_exercise,
    calculate_total_sessions,
    calculate_total_reps,
    calculate_average_accuracy,
    calculate_sessions_per_week,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _get_sessions_list(user_id, db: Session) -> list[dict]:
    """Fetch all sessions for a user and convert to list of dicts."""
    sessions = db.query(ExerciseSession)\
        .filter(ExerciseSession.user_id == user_id)\
        .order_by(ExerciseSession.created_at.desc())\
        .all()
    return [
        {
            "exercise_type":    s.exercise_type,
            "total_reps":       s.total_reps,
            "correct_reps":     s.correct_reps,
            "incorrect_reps":   s.incorrect_reps,
            "posture_accuracy": s.posture_accuracy,
            "duration_seconds": s.duration_seconds,
            "created_at":       s.created_at.isoformat() if s.created_at else None,
        }
        for s in sessions
    ]


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Returns high-level summary statistics for the dashboard header cards.
    """
    sessions = _get_sessions_list(current_user.id, db)
    current_streak, best_streak = calculate_streak(sessions)

    return {
        "total_sessions":       calculate_total_sessions(sessions),
        "total_reps":           calculate_total_reps(sessions),
        "avg_accuracy":         calculate_average_accuracy(sessions),
        "current_streak_days":  current_streak,
        "best_streak_days":     best_streak,
        "sessions_this_week":   calculate_sessions_per_week(sessions),
    }


@router.get("/weekly")
def get_weekly(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Returns session counts and average accuracy for the last 7 days.
    Used by the weekly bar chart on the dashboard.
    """
    sessions = _get_sessions_list(current_user.id, db)
    return calculate_weekly_breakdown(sessions)


@router.get("/by-exercise")
def get_by_exercise(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Returns session count and average accuracy grouped by exercise type.
    Used by the exercise breakdown horizontal bar chart.
    """
    sessions = _get_sessions_list(current_user.id, db)
    return calculate_by_exercise(sessions)


@router.get("/accuracy-trend")
def get_accuracy_trend(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Returns posture accuracy for the last 30 sessions in chronological order.
    Used by the accuracy trend line chart.
    """
    sessions = _get_sessions_list(current_user.id, db)
    return calculate_accuracy_trend(sessions, n=30)
```

---

## File 9: `frontend/src/components/workout/AIProgressBanner.jsx`  [CREATE]

Create this React component. It shows the user how many sessions they
have completed and how many more they need before AI recommendations
activate. Shown on the WorkoutPlan page.

Props:
  sessionCount: number
  minForAi: number        (always 5)
  aiActive: boolean
  phase: number           (1 or 2)

Render:

If aiActive is true (phase 2):
  A green banner:
  Icon: Sparkles (lucide, green)
  Heading: "AI-powered plan active"
  Text: "Your plan is now personalised based on your real
         performance data from {sessionCount} sessions."

If aiActive is false (phase 1):
  A blue information banner:
  Icon: Info (lucide, blue)
  Heading: "Building your profile"
  Text: "Complete {minForAi - sessionCount} more session
         {minForAi - sessionCount === 1 ? '' : 's'} to unlock
         AI-personalised workout plans."
  A progress bar: sessionCount / minForAi × 100%
  Below bar: "{sessionCount} of {minForAi} sessions completed"

Styling:
  Rounded card, padding-4, border, full width
  Phase 1: border-blue-200 bg-blue-50
  Phase 2: border-green-200 bg-green-50

---

## File 10: `frontend/src/pages/WorkoutPlan.jsx`  [MODIFY]

Add the AIProgressBanner to the WorkoutPlan page.

Add this to the existing useEffect that fetches the plan:

```js
// Also fetch recommendation status for the AI progress banner
const statusRes = await client.get('/recommendations/status')
setRecommendationStatus(statusRes.data)
```

Add state:
```js
const [recommendationStatus, setRecommendationStatus] = useState(null)
```

Add the banner to the JSX, directly below the page header and above
the day cards:

```jsx
{recommendationStatus && (
  <AIProgressBanner
    sessionCount={recommendationStatus.session_count}
    minForAi={recommendationStatus.min_for_ai}
    aiActive={recommendationStatus.ai_active}
    phase={recommendationStatus.phase}
  />
)}
```

Also update the plan source label below the page header:
  If plan.generated_by === "static_library":
    Show: "Matched to your onboarding profile"
  If plan.generated_by === "llm":
    Show: "AI-generated based on your performance ✨"

---

## Register new routers in `backend/main.py`

Add these two imports and router registrations if not already present:

```python
from backend.routers import analytics, recommendations

app.include_router(analytics.router)
app.include_router(recommendations.router)
```

---

## Final coding standards reminder

- analytics/metrics.py: all functions accept list[dict], never ORM objects
- recommendations.py: GET /plan always returns 200, never 500
- AIProgressBanner.jsx: pure display component, no API calls
- All new backend endpoints require JWT authentication via
  get_current_user dependency
- All new frontend components documented with JSDoc prop comments
