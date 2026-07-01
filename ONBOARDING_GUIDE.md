# Feature guide: onboarding flow & static plan library

> Open this file in a split pane next to the file you are implementing.
> Each section maps to one file. Paste the Copilot inline prompts (`Ctrl+I`)
> directly onto the relevant function stub.

---

## Overview of what changed

The old flow: **Register → Dashboard**

The new flow: **Register → Screen 2 (Body) → Screen 3 (Goal) → Screen 4 (Equipment) → Screen 5 (Availability) → Dashboard**

On completion of Screen 5, the system **matches** the user to a pre-built plan from
`plan_library.py` instead of calling the LLM. This means:
- Zero API latency on first login
- Deterministic, consistent plans per profile type
- No Gemini API quota used for new user onboarding

The LLM (`llm_planner.py`) is now reserved for returning users who click
**"Refresh my plan"** after several weeks of sessions.

---

## `backend/models.py` — UserProfile model

```python
# Copilot prompt — add UserProfile model:
# Create class UserProfile(Base) with __tablename__ = "user_profiles".
# Columns:
#   id: UUID primary key, server_default=str(uuid4())
#   user_id: UUID, ForeignKey("users.id"), unique=True, nullable=False
#   age: Integer, nullable=False
#   gender: String(30), nullable=True
#   height_cm: Float, nullable=False
#   weight_kg: Float, nullable=False
#   bmi: Float, nullable=False
#   fitness_level: String(20), nullable=False
#   goal: String(30), nullable=False
#   has_equipment: Boolean, nullable=False, default=False
#   equipment_list: JSON, nullable=True
#   days_per_week: Integer, nullable=False
#   workout_duration_minutes: Integer, nullable=False
#   preferred_time: String(50), nullable=False
#   onboarding_complete: Boolean, default=False
#   created_at: DateTime, default=datetime.utcnow
#   updated_at: DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
#   user = relationship("User", back_populates="profile")
#
# Also add to the existing User model:
#   profile = relationship("UserProfile", back_populates="user", uselist=False)
#   onboarding_complete: Boolean, default=False
#
# Run: alembic revision --autogenerate -m "add user_profiles table"
# Then: alembic upgrade head
```

---

## `backend/schemas_onboarding.py` — validation schemas

```python
# Copilot prompt:
# Create schemas_onboarding.py.
#
# OnboardingComplete(BaseModel):
#   age: int = Field(..., ge=13, le=100)
#   gender: Optional[str] = None
#   height_cm: float = Field(..., ge=50.0, le=300.0)
#   weight_kg: float = Field(..., ge=20.0, le=300.0)
#   fitness_level: Literal["beginner", "intermediate", "advanced"]
#   goal: Literal["weight_loss", "muscle_gain", "strength_training",
#                 "endurance", "general_fitness", "flexibility", "sports_specific"]
#   has_equipment: bool
#   equipment_list: list[str] = []
#   days_per_week: int = Field(..., ge=1, le=7)
#   workout_duration_minutes: Literal[15, 20, 30, 45, 60, 75, 90]
#   preferred_time: str
#
# UserProfileResponse(BaseModel):
#   id: UUID
#   user_id: UUID
#   age: int
#   gender: Optional[str]
#   height_cm: float
#   weight_kg: float
#   bmi: float
#   fitness_level: str
#   goal: str
#   has_equipment: bool
#   equipment_list: Optional[list[str]]
#   days_per_week: int
#   workout_duration_minutes: int
#   preferred_time: str
#   onboarding_complete: bool
#   class Config: from_attributes = True
```

---

## `recommendation/plan_library.py` — static plan definitions

This is the most content-heavy file. The structure for every plan:

```python
PLAN_LIBRARY = {
    "beginner__weight_loss__no_equipment__3d__30min": {
        "monday": {
            "is_rest": False,
            "exercises": [
                {"exercise": "Squat",  "sets": 3, "reps": 10, "notes": "Keep chest up, drive through heels"},
                {"exercise": "Push-up", "sets": 3, "reps": 8,  "notes": "Keep core tight, elbows at 45 degrees"},
            ]
        },
        "tuesday":   {"is_rest": True,  "exercises": []},
        "wednesday": {
            "is_rest": False,
            "exercises": [
                {"exercise": "Squat",  "sets": 3, "reps": 12, "notes": "Go to parallel depth"},
                {"exercise": "Push-up", "sets": 3, "reps": 10, "notes": "Full range — chest to floor"},
            ]
        },
        "thursday":  {"is_rest": True, "exercises": []},
        "friday": {
            "is_rest": False,
            "exercises": [
                {"exercise": "Squat",  "sets": 3, "reps": 10, "notes": "Pause 1 second at the bottom"},
                {"exercise": "Push-up", "sets": 3, "reps": 8,  "notes": "Slow eccentric — 3 seconds down"},
            ]
        },
        "saturday":  {"is_rest": True, "exercises": []},
        "sunday":    {"is_rest": True, "exercises": []},
        "notes": "Rest at least 60 seconds between sets. Focus on form before adding volume.",
        "generated_by": "static_library",
        "match_key": "beginner__weight_loss__no_equipment__3d__30min"
    },
    # ... (21 plans total — see plan list in COPILOT_ONBOARDING_PROMPT.md)
}
```

```python
# Copilot prompt:
# Generate all 21 plan entries following the structure above.
# Rules:
#   No-equipment plans: use only Squat and Push-up.
#   Equipment plans: use all 5 exercises (Squat, Bicep Curl, Push-up,
#     Dumbbell Fly, Dumbbell Kickback). Distribute so each appears at
#     least once per week.
#   Beginner 3-day: workout Mon/Wed/Fri, rest other days. 3 sets, 8-12 reps.
#   Intermediate 4-day: workout Mon/Tue/Thu/Fri, rest Wed/Sat/Sun.
#     3-4 sets, 10-15 reps.
#   Advanced 5-day: workout Mon-Fri, rest Sat/Sun.
#     4 sets, 12-20 reps.
#   Each exercise entry must have a unique form-cue note — do not repeat
#   the same note string across exercises within the same plan.
#   The plan-level "notes" field gives 1-2 sentences of advice specific
#   to that goal and fitness level combination.
```

### Form cue reference (use these as the basis for notes fields)

| Exercise | Beginner cue | Intermediate cue | Advanced cue |
|---|---|---|---|
| Squat | "Keep chest up, drive through heels" | "Go below parallel, brace your core" | "Pause 2s at bottom, explosive drive up" |
| Push-up | "Keep elbows at 45°, full range" | "3-second eccentric, chest to floor" | "Archer variation — shift weight side to side" |
| Bicep Curl | "Elbows pinned to sides, full extension" | "Supinate at the top, slow lower" | "Alternating with controlled negative" |
| Dumbbell Fly | "Slight elbow bend, squeeze at top" | "Full stretch at bottom, controlled" | "Drop set on last set" |
| Dumbbell Kickback | "Upper arm parallel to floor" | "Full lockout at the top" | "Pause 1s at full extension" |

---

## `recommendation/plan_matcher.py` — matching logic

```python
# Copilot prompt:
# Implement match_plan(profile: dict) -> dict.
#
# profile keys: fitness_level, goal, has_equipment, days_per_week,
#               workout_duration_minutes
#
# Step 1 — build the lookup key:
#   equipment_str = "with_equipment" if has_equipment else "no_equipment"
#   days_bracket = min([3,4,5], key=lambda d: abs(d - days_per_week))
#   duration_bracket = min([30,45,60], key=lambda d: abs(d - workout_duration_minutes))
#   key = f"{fitness_level}__{goal}__{equipment_str}__{days_bracket}d__{duration_bracket}min"
#
# Step 2 — try exact lookup:
#   if key in PLAN_LIBRARY: return PLAN_LIBRARY[key]
#
# Step 3 — fallback: drop equipment requirement, try with no_equipment:
#   fallback_key = f"{fitness_level}__{goal}__no_equipment__{days_bracket}d__{duration_bracket}min"
#   if fallback_key in PLAN_LIBRARY: return PLAN_LIBRARY[fallback_key]
#
# Step 4 — fallback: drop days and duration, just match level + goal:
#   for key in PLAN_LIBRARY:
#     if key.startswith(f"{fitness_level}__{goal}"): return PLAN_LIBRARY[key]
#
# Step 5 — last resort: return the general_fitness plan for that level:
#   for key in PLAN_LIBRARY:
#     if key.startswith(f"{fitness_level}__general_fitness"): return PLAN_LIBRARY[key]
#
# If all fallbacks fail, return PLAN_LIBRARY[list(PLAN_LIBRARY.keys())[0]].
# This function must NEVER return None.
#
# Log a warning whenever a fallback is used so it is clear in the logs
# which step matched.
```

---

## `backend/routers/onboarding.py` — API endpoints

```python
# Copilot prompt — POST /onboarding/complete:
# Accept OnboardingComplete body + current_user from get_current_user dependency.
# 1. Compute bmi = round(weight_kg / (height_cm / 100)**2, 1)
# 2. Check if UserProfile already exists for this user_id.
#    If yes, update it. If no, create it.
# 3. Set all fields from the request body plus the computed bmi.
# 4. Set onboarding_complete = True on both UserProfile and User.
# 5. Call plan_matcher.match_plan({
#      "fitness_level": body.fitness_level,
#      "goal": body.goal,
#      "has_equipment": body.has_equipment,
#      "days_per_week": body.days_per_week,
#      "workout_duration_minutes": body.workout_duration_minutes
#    }) -> plan_dict
# 6. Compute this_monday = date.today() - timedelta(days=date.today().weekday())
# 7. Check if a WorkoutPlan already exists for this user + week_start_date.
#    If yes, update plan_data. If no, create it.
# 8. Commit all changes. Refresh all objects.
# 9. Return {"profile": profile, "plan": plan} using response models.
#
# Copilot prompt — GET /onboarding/status:
# Query User by current_user.id.
# Return {"onboarding_complete": user.onboarding_complete}
#
# Copilot prompt — GET /onboarding/profile:
# Query UserProfile by user_id = current_user.id.
# If not found: raise HTTPException(status_code=404, detail="Profile not found")
# Return UserProfileResponse.
```

---

## `frontend/pages/onboarding.py` — Streamlit wizard

### Session state keys used

| Key | Type | Set by | Purpose |
|---|---|---|---|
| `onboarding_step` | `int` (1–5) | `app.py` | Current wizard step |
| `onboarding_data` | `dict` | Each step | Accumulates all field values |
| `onboarding_complete` | `bool` | Step 5 submit | Controls nav routing |

### Step 2 — BMI auto-calculation

```python
# Copilot prompt for step 2:
# height_cm = st.number_input("Height (cm)", min_value=50.0, max_value=300.0,
#   value=170.0, step=0.5)
# weight_kg = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0,
#   value=70.0, step=0.5)
# bmi = round(weight_kg / (height_cm / 100) ** 2, 1)
# if bmi < 18.5:   category, color = "Underweight", "blue"
# elif bmi < 25:   category, color = "Normal weight", "green"
# elif bmi < 30:   category, color = "Overweight",   "orange"
# else:            category, color = "Obese",         "red"
# col1, col2 = st.columns(2)
# col1.metric("BMI", bmi)
# col2.write(f"Category: **{category}**")
# st.caption("BMI is shown for informational purposes only and does not affect your plan.")
```

### Step 3 — goal descriptions

```python
# Copilot prompt:
# Display each goal option in st.radio.
# After the radio, show a description for the selected goal using st.info():
# goal_descriptions = {
#   "weight_loss":       "Burns calories through varied intensity circuits...",
#   "muscle_gain":       "Progressive overload with compound and isolation moves...",
#   "strength_training": "Low rep, high resistance to build raw strength...",
#   "endurance":         "High rep, lower rest periods to improve stamina...",
#   "general_fitness":   "Balanced mix of strength, cardio, and flexibility...",
#   "flexibility":       "Focuses on range of motion and joint mobility...",
#   "sports_specific":   "Explosive power and coordination for athletic performance...",
# }
# st.info(goal_descriptions[selected_goal])
```

### Step 5 — profile summary card

```python
# Copilot prompt:
# Before the "Build my plan" button, show a summary:
# st.subheader("Your profile summary")
# col1, col2 = st.columns(2)
# data = st.session_state["onboarding_data"]
# col1.metric("Age",           data["age"])
# col1.metric("Height",        f"{data['height_cm']} cm")
# col1.metric("Weight",        f"{data['weight_kg']} kg")
# col1.metric("Fitness level", data["fitness_level"].capitalize())
# col2.metric("Goal",          data["goal"].replace("_", " ").title())
# col2.metric("Equipment",     "Yes" if data["has_equipment"] else "Bodyweight only")
# col2.metric("Days/week",     data["days_per_week"])
# col2.metric("Duration",      f"{data['workout_duration_minutes']} min")
# st.write(f"**Preferred time:** {data['preferred_time']}")
```

---

## `frontend/app.py` — routing guard

```python
# Copilot prompt — add after login success:
# After storing token and user in session_state, call:
#   response = requests.get(f"{api_base}/onboarding/status",
#                           headers={"Authorization": f"Bearer {token}"})
#   status = response.json()
#   st.session_state["onboarding_complete"] = status["onboarding_complete"]
#
# In the sidebar navigation guard:
#   if not st.session_state.get("onboarding_complete", False):
#     st.switch_page("pages/onboarding.py")
#   else:
#     # show normal navigation
```

---

## Testing checklist

Run through these scenarios manually after implementation:

- [ ] New user registers → redirected to onboarding step 2
- [ ] BMI updates live as height/weight change on step 2
- [ ] Clicking Back on step 3 returns to step 2 with values preserved
- [ ] Selecting "Bodyweight only" hides the equipment checklist on step 4
- [ ] Summary card on step 5 shows all collected data correctly
- [ ] Submitting onboarding creates UserProfile row in database
- [ ] Submitting onboarding creates WorkoutPlan row with `generated_by = "static_library"`
- [ ] Returning user who already completed onboarding skips to dashboard
- [ ] `GET /onboarding/status` returns `{"onboarding_complete": true}` for completed user
- [ ] `plan_matcher.match_plan` never returns None for any valid input combination

```bash
# Quick backend test:
pytest tests/test_onboarding.py -v

# Quick matcher test:
python -c "
from recommendation.plan_matcher import match_plan
plan = match_plan({
  'fitness_level': 'beginner',
  'goal': 'weight_loss',
  'has_equipment': False,
  'days_per_week': 3,
  'workout_duration_minutes': 30
})
print(plan['match_key'])
print([d for d in ['monday','tuesday','wednesday','thursday','friday']
       if not plan[d]['is_rest']])
"
```
