# Feature guide: recommendation engine (`recommendation/`)

> Open this file alongside the relevant source file in VS Code.
> Use Copilot inline chat (`Ctrl+I`) on each stub.

---

## Overview

The recommendation engine generates personalised weekly workout plans. It uses
two complementary approaches:

1. **Rule-based model** (`rule_based.py`): A scikit-learn decision tree that
   analyses the user's last 7 days of session metrics and classifies their
   current fitness tier (beginner / intermediate / advanced). This always works,
   even without network access.

2. **LLM planner** (`llm_planner.py`): Takes the user profile and difficulty
   tier, then calls the Google Gemini API to generate a rich, natural-language
   weekly plan with exercise variety, progression logic, and rest days.

The `engine.py` orchestrator calls the rule-based model first to determine
difficulty, then passes that to the LLM planner. If the LLM call fails (no API
key, rate limit, network error), it falls back to a template-based plan.

---

## `recommendation/schemas.py` — data structures

```python
# Copilot prompt:
# Implement Pydantic v2 schemas:
#
# class ExerciseEntry(BaseModel):
#   exercise: str          (e.g. "Squat", "Bicep Curl")
#   sets: int
#   reps: int
#   notes: str = ""        (e.g. "Focus on depth", "Keep elbows in")
#
# class DayPlan(BaseModel):
#   is_rest: bool = False
#   exercises: list[ExerciseEntry] = []
#
# class WeeklyPlan(BaseModel):
#   monday: DayPlan
#   tuesday: DayPlan
#   wednesday: DayPlan
#   thursday: DayPlan
#   friday: DayPlan
#   saturday: DayPlan
#   sunday: DayPlan
#   difficulty: str        ("beginner" / "intermediate" / "advanced")
#   generated_by: str      ("llm" / "rule_based")
#   notes: str = ""
```

---

## `rule_based.py` — scikit-learn difficulty classifier

### What to implement

```python
# Copilot prompt:
# Implement build_and_train_model() -> sklearn.pipeline.Pipeline:
#   Create synthetic training data representing three difficulty tiers.
#   Features: [avg_posture_accuracy, sessions_per_week, avg_reps_per_session]
#   Labels: 0=beginner, 1=intermediate, 2=advanced
#   Synthetic data examples:
#     Beginner:      accuracy < 60%, < 2 sessions/week, < 8 reps avg
#     Intermediate:  accuracy 60-80%, 2-4 sessions/week, 8-15 reps avg
#     Advanced:      accuracy > 80%, > 4 sessions/week, > 15 reps avg
#   Generate ~150 samples per class with some gaussian noise.
#   Build a Pipeline with StandardScaler and DecisionTreeClassifier(max_depth=5).
#   Fit the pipeline on the synthetic data.
#   Return the fitted pipeline.
#
# Implement predict_difficulty(user_metrics: dict) -> str:
#   user_metrics keys: avg_posture_accuracy, sessions_per_week, avg_reps_per_session
#   If any metric is missing, default to 0.
#   Load or build the model (cache it as a module-level variable after first call).
#   Predict on [[avg_posture_accuracy, sessions_per_week, avg_reps_per_session]].
#   Map prediction 0->beginner, 1->intermediate, 2->advanced.
#   Return the string label.
```

### Why synthetic data is appropriate here

The classifier is not learning from personal biometric data — it is a simple
business-logic tier assignment. Synthetic data with clear cluster boundaries
is standard practice for this kind of rule-reification model. For the final
project report, note this explicitly under "methodology".

---

## `llm_planner.py` — Gemini API workout plan generator

### What to implement

```python
# Copilot prompt:
# Implement generate_weekly_plan(user_profile: dict, difficulty: str) -> dict:
#
# user_profile keys: username, age, fitness_level, goal
#
# Build a structured prompt string:
# """
# You are a certified personal trainer AI.
# Generate a 7-day workout plan for the following user:
#   Name: {username}
#   Age: {age}
#   Fitness level: {difficulty}
#   Goal: {goal}
#
# Available exercises: Squat, Bicep Curl, Push-up, Dumbbell Fly, Dumbbell Kickback.
# Include 3-4 workout days and 3-4 rest/active recovery days.
# For each workout day, prescribe 3-4 exercises with sets and reps appropriate
# for a {difficulty} level user pursuing {goal}.
#
# Respond ONLY with a valid JSON object. No preamble, no markdown, no explanation.
# The JSON must have exactly these keys:
# monday, tuesday, wednesday, thursday, friday, saturday, sunday
# Each key maps to an object with:
#   "is_rest": boolean
#   "exercises": array of {"exercise": string, "sets": int, "reps": int, "notes": string}
#   (exercises array is empty if is_rest is true)
# Also include "notes": string at the top level with general advice.
# """
#
# Call Gemini:
#   import google.generativeai as genai
#   genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
#   model = genai.GenerativeModel("gemini-1.5-flash")
#   response = model.generate_content(prompt)
#   raw = response.text.strip()
#   Remove markdown code fences if present: raw = re.sub(r"```json|```", "", raw).strip()
#   parsed = json.loads(raw)
#   parsed["generated_by"] = "llm"
#   Return parsed
#
# Wrap the entire Gemini call in try/except Exception as e:
#   Log the error.
#   Return get_fallback_plan(difficulty) instead.
```

### `get_fallback_plan(difficulty: str) -> dict`

```python
# Copilot prompt:
# Implement a static fallback plan for each difficulty level.
# Beginner plan: 3 workout days (Mon, Wed, Fri), rest on others.
#   Workout: Squat 3x10, Bicep Curl 3x8, Push-up 3x8
# Intermediate plan: 4 workout days (Mon, Tue, Thu, Fri).
#   Mon/Thu: Squat 4x12, Dumbbell Fly 3x12, Bicep Curl 3x12
#   Tue/Fri: Push-up 4x15, Dumbbell Kickback 3x12, Bicep Curl 3x15
# Advanced plan: 5 workout days (Mon-Fri).
#   Vary between push/pull/legs splits.
# Set "generated_by": "rule_based" in all fallback plans.
# Return the dict matching the WeeklyPlan schema structure.
```

---

## `engine.py` — orchestrator

```python
# Copilot prompt:
# Implement generate_plan(user_profile: dict, user_metrics: dict) -> dict:
#   1. Call rule_based.predict_difficulty(user_metrics) -> difficulty string
#   2. Call llm_planner.generate_weekly_plan(user_profile, difficulty) -> plan dict
#   3. Validate the plan dict can be parsed into WeeklyPlan schema.
#      If validation fails, fall back to llm_planner.get_fallback_plan(difficulty).
#   4. Return the validated plan dict.
```

---

## Testing the recommendation engine

```bash
# Quick test without API key (uses fallback):
python -c "
from recommendation.engine import generate_plan

profile = {'username': 'Andrew', 'age': 22, 'fitness_level': 'beginner', 'goal': 'muscle_gain'}
metrics = {'avg_posture_accuracy': 55.0, 'sessions_per_week': 1.5, 'avg_reps_per_session': 7.0}
plan = generate_plan(profile, metrics)
import json; print(json.dumps(plan, indent=2))
"

# With Gemini API key set in .env:
pytest tests/test_recommendations.py -v
```

---

## Prompt engineering notes

If the LLM returns malformed JSON, check these common issues:

- Gemini sometimes wraps the JSON in ` ```json ``` ` markdown fences — the
  `re.sub` step in `llm_planner.py` handles this.
- If the plan is missing a day key, the `WeeklyPlan` Pydantic validation will
  raise a `ValidationError` — this triggers the fallback in `engine.py`.
- To improve reliability, you can add `response_mime_type="application/json"`
  to the Gemini call in newer SDK versions to force JSON output mode.
