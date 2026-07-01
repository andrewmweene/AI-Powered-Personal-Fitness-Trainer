# Copilot Prompt — Onboarding Flow & Static Workout Plan Library

> **How to use:**
> 1. Open GitHub Copilot Chat in VS Code (`Ctrl+Shift+I`)
> 2. Paste the full prompt block below and send it
> 3. Copilot will generate all files listed. Review each one before accepting.
> 4. Open `ONBOARDING_GUIDE.md` for per-file implementation instructions.

---

## Prompt — paste into Copilot Chat

```
I am extending my AI Personal Trainer project with a multi-step onboarding
flow and a static pre-built workout plan library.

## What needs to be built

### 1. Multi-step user onboarding (5 screens)

When a new user registers, instead of going straight to the dashboard,
they are taken through 5 sequential onboarding screens. Each screen
must validate input before allowing the user to proceed.

Screen 1 — Account creation (already exists — reuse the existing register
  form but add a "Continue to profile setup" redirect after success)

Screen 2 — Body profile
  Fields:
    - age: integer (required, 13–100)
    - gender: select (optional) — Male, Female, Non-binary, Prefer not to say
    - height_cm: float (required, 50–300 cm)
    - weight_kg: float (required, 20–300 kg)
    - bmi: float (auto-calculated from height and weight, read-only display)
      Formula: bmi = weight_kg / (height_cm / 100) ** 2
      Display the BMI category next to the value:
        < 18.5  = "Underweight"
        18.5–24.9 = "Normal weight"
        25–29.9 = "Overweight"
        >= 30   = "Obese"
      Note: BMI is displayed for informational purposes only. The system
      does not restrict or judge users based on BMI category.
    - fitness_level: radio (required) — Beginner, Intermediate, Advanced

Screen 3 — Workout goal
  Single-select radio group (required). Options:
    - weight_loss        → "Weight loss"
    - muscle_gain        → "Muscle gain"
    - strength_training  → "Strength training"
    - endurance          → "Endurance improvement"
    - general_fitness    → "General fitness"
    - flexibility        → "Flexibility and mobility"
    - sports_specific    → "Sports-specific training"

Screen 4 — Equipment
  - has_equipment: boolean radio (required) — "I have equipment" / "Bodyweight only"
  - If has_equipment is True, show a multi-select checkbox group:
      equipment_list: list of strings
      Options: Dumbbells, Resistance bands, Pull-up bar, Kettlebell,
               Barbell + rack, Bench, Cables/machine, Full gym access
  - If has_equipment is False, set equipment_list = []

Screen 5 — Availability
  - days_per_week: integer slider (required, 1–7)
  - workout_duration_minutes: select (required)
      Options: 15, 20, 30, 45, 60, 75, 90 minutes
  - preferred_time: select (required)
      Options: Early morning (5–8 am), Morning (8–11 am),
               Midday (11 am–2 pm), Afternoon (2–5 pm),
               Evening (5–8 pm), Late evening (8–11 pm)

After Screen 5, call the backend to:
  a. Save the full user profile to the database
  b. Match and assign a static workout plan from the plan library
  c. Redirect to the dashboard

---

### 2. Database changes

Add a new table `user_profiles` to store the onboarding data.
Create a new SQLAlchemy model `UserProfile` with these columns:

  id: UUID primary key, default uuid4
  user_id: UUID ForeignKey("users.id") unique not null
  age: Integer not null
  gender: String(30) nullable
  height_cm: Float not null
  weight_kg: Float not null
  bmi: Float not null
  fitness_level: String(20) not null  (beginner/intermediate/advanced)
  goal: String(30) not null
  has_equipment: Boolean not null default False
  equipment_list: JSON nullable  (list of strings)
  days_per_week: Integer not null
  workout_duration_minutes: Integer not null
  preferred_time: String(50) not null
  onboarding_complete: Boolean default False
  created_at: DateTime default utcnow
  updated_at: DateTime default utcnow onupdate utcnow

  Relationship: user = relationship("User", back_populates="profile")

Also add to the User model:
  profile = relationship("UserProfile", back_populates="user", uselist=False)
  onboarding_complete: Boolean default False

---

### 3. Pydantic schemas for onboarding

Create `backend/schemas_onboarding.py` with these schemas:

  BodyProfileCreate(BaseModel):
    age: int (Field ge=13, le=100)
    gender: Optional[str] = None
    height_cm: float (Field ge=50, le=300)
    weight_kg: float (Field ge=20, le=300)
    fitness_level: Literal["beginner", "intermediate", "advanced"]

  GoalCreate(BaseModel):
    goal: Literal["weight_loss", "muscle_gain", "strength_training",
                  "endurance", "general_fitness", "flexibility", "sports_specific"]

  EquipmentCreate(BaseModel):
    has_equipment: bool
    equipment_list: list[str] = []

  AvailabilityCreate(BaseModel):
    days_per_week: int (Field ge=1, le=7)
    workout_duration_minutes: Literal[15, 20, 30, 45, 60, 75, 90]
    preferred_time: str

  OnboardingComplete(BaseModel):
    (combines all four schemas above into one payload)
    age: int
    gender: Optional[str] = None
    height_cm: float
    weight_kg: float
    fitness_level: str
    goal: str
    has_equipment: bool
    equipment_list: list[str] = []
    days_per_week: int
    workout_duration_minutes: int
    preferred_time: str

  UserProfileResponse(BaseModel):
    (all fields of UserProfile ORM model)
    Config: from_attributes = True

---

### 4. Backend onboarding router

Create `backend/routers/onboarding.py` with these endpoints:

  POST /onboarding/complete
    - Accepts OnboardingComplete body + current_user from JWT
    - Compute bmi = weight_kg / (height_cm / 100) ** 2, round to 1 decimal
    - Create or update UserProfile for current_user.id
    - Set user.onboarding_complete = True
    - Call plan_matcher.match_plan(profile_data) to get the plan
    - Save matched plan to WorkoutPlan table with week_start_date = this Monday
    - Return {"profile": UserProfileResponse, "plan": WorkoutPlanResponse}

  GET /onboarding/status
    - Returns {"onboarding_complete": bool} for current user
    - Used by frontend to decide whether to show onboarding or dashboard

  GET /onboarding/profile
    - Returns full UserProfileResponse for current user
    - Raise 404 if profile not yet created

Register this router in backend/main.py with prefix="/onboarding".

---

### 5. Static plan matcher

Create `recommendation/plan_matcher.py`.

This module replaces the LLM + rule-based generator for new users.
Instead of generating a plan, it matches the user's profile to a
pre-built plan from a static library. This ensures every user gets
a consistent, high-quality plan immediately on registration, with no
API calls and no latency.

Implement `match_plan(profile: dict) -> dict`:

  profile keys: fitness_level, goal, has_equipment, days_per_week,
                workout_duration_minutes

  Matching logic (priority order):
    1. Match on fitness_level (beginner / intermediate / advanced)
    2. Match on goal (weight_loss / muscle_gain / strength_training /
                      endurance / general_fitness / flexibility / sports_specific)
    3. Match on has_equipment (True / False)
    4. Find the closest days_per_week match (3, 4, or 5 day plans available)
    5. Find the closest duration match (30, 45, or 60 minute plans)

  Return the best matching plan dict from PLAN_LIBRARY.
  If no exact match, use the closest match on steps 1-2 (always match
  fitness_level and goal exactly; approximate the rest).

  Set "generated_by": "static_library" and "match_key": the key used
  in the lookup, so it is clear which template was applied.

---

### 6. Static plan library

Create `recommendation/plan_library.py`.

This file defines PLAN_LIBRARY — a dict of pre-built weekly workout plans.
Keys follow the format: "{fitness_level}__{goal}__{equipment}__{days}d__{duration}min"
Example key: "beginner__weight_loss__no_equipment__3d__30min"

Each plan value is a dict matching the WeeklyPlan schema:
{
  "monday":    {"is_rest": bool, "exercises": [...]},
  "tuesday":   {"is_rest": bool, "exercises": [...]},
  "wednesday": {"is_rest": bool, "exercises": [...]},
  "thursday":  {"is_rest": bool, "exercises": [...]},
  "friday":    {"is_rest": bool, "exercises": [...]},
  "saturday":  {"is_rest": bool, "exercises": [...]},
  "sunday":    {"is_rest": bool, "exercises": [...]},
  "notes": "string with general plan advice",
  "generated_by": "static_library",
  "match_key": "the key string"
}

Each exercise entry:
{
  "exercise": "Squat",       (must be one of the 5 supported exercises)
  "sets": 3,
  "reps": 10,
  "notes": "Keep chest up"  (form cue specific to this exercise in this plan)
}

The 5 supported exercises are: Squat, Bicep Curl, Push-up, Dumbbell Fly,
Dumbbell Kickback.

Generate plans for these combinations (21 plans total):

FITNESS LEVEL: beginner
  goal: weight_loss,     equipment: False, 3d, 30min
  goal: weight_loss,     equipment: True,  3d, 30min
  goal: muscle_gain,     equipment: True,  3d, 45min
  goal: strength_training, equipment: True, 3d, 45min
  goal: general_fitness, equipment: False, 3d, 30min
  goal: flexibility,     equipment: False, 3d, 30min
  goal: endurance,       equipment: False, 3d, 30min

FITNESS LEVEL: intermediate
  goal: weight_loss,     equipment: False, 4d, 45min
  goal: weight_loss,     equipment: True,  4d, 45min
  goal: muscle_gain,     equipment: True,  4d, 60min
  goal: strength_training, equipment: True, 4d, 60min
  goal: general_fitness, equipment: False, 4d, 45min
  goal: flexibility,     equipment: False, 4d, 30min
  goal: endurance,       equipment: False, 4d, 45min

FITNESS LEVEL: advanced
  goal: weight_loss,     equipment: True,  5d, 60min
  goal: muscle_gain,     equipment: True,  5d, 60min
  goal: strength_training, equipment: True, 5d, 60min
  goal: endurance,       equipment: False, 5d, 60min
  goal: general_fitness, equipment: True,  5d, 60min
  goal: flexibility,     equipment: False, 4d, 45min
  goal: sports_specific, equipment: True,  5d, 60min

Rules for building each plan:
  - Beginner plans: 3 workout days, rest days Mon/Wed/Fri or Tue/Thu/Sat.
    2-3 exercises per day, 3 sets, 8-12 reps. Rest between workout days.
  - Intermediate plans: 4 workout days with one mid-week rest.
    3-4 exercises per day, 3-4 sets, 10-15 reps.
  - Advanced plans: 5 workout days, 2 rest days on weekend.
    4 exercises per day, 4 sets, 12-20 reps. Higher volume.
  - No-equipment plans: use only Squat and Push-up.
  - Equipment plans: use all 5 exercises, distributing them across days
    so each exercise appears at least once per week.
  - Include specific form cues in the "notes" field of each exercise
    (e.g. "Drive through heels at the top" for Squat, "Pinch shoulder
    blades together" for Dumbbell Fly).
  - The plan-level "notes" field should give 1-2 sentences of general
    advice for that fitness level and goal combination.

---

### 7. Frontend onboarding wizard

Create `frontend/pages/onboarding.py` — a Streamlit multipage onboarding
wizard with progress tracking.

Implementation requirements:

  Progress bar: st.progress((step - 1) / 4) at the top of every screen.
  Step indicator text: "Step {n} of 5 — {step_name}" in muted style.
  
  Use st.session_state to accumulate data across steps:
    st.session_state["onboarding_step"] = 1 (initialise in app.py if not set)
    st.session_state["onboarding_data"] = {} (accumulate fields here)

  Each step has:
    - A header with the step name
    - All input fields for that step
    - A "Continue →" button that validates and advances to the next step
    - A "← Back" button (except on step 2) that goes back one step

  Step 2 — Body profile:
    - Show BMI as a read-only st.metric that updates as the user changes
      height and weight. Calculate BMI in Python on every rerun.
    - Show the BMI category label below the metric value.
    - Add a small note: "BMI is shown for reference only and does not
      affect your workout plan."

  Step 3 — Workout goal:
    - Display goals as styled radio buttons using st.radio.
    - Show a one-sentence description below each goal option explaining
      what it focuses on. Use st.caption for descriptions.

  Step 4 — Equipment:
    - Use st.radio for the yes/no equipment question.
    - If "I have equipment" is selected, use st.multiselect to show
      the equipment list. Require at least one item to be selected.

  Step 5 — Availability:
    - days_per_week: st.slider(min=1, max=7, value=3)
    - workout_duration_minutes: st.selectbox
    - preferred_time: st.selectbox
    - Show a summary card at the bottom of step 5 before submission:
      "Here is your profile summary — please confirm before we build
      your plan." Display all collected data in two columns using
      st.columns(2). Each field shown as st.metric or st.write.
    - "Build my plan →" button (not "Continue") on the final step.
    - On submit: POST to {api_base}/onboarding/complete with full
      onboarding_data dict and Bearer token.
    - On success: set st.session_state["onboarding_complete"] = True
      and st.switch_page("pages/workout_plan.py").
    - On error: display st.error with the error message from the API.

  Guard in app.py:
    After login, GET /onboarding/status.
    If onboarding_complete is False: redirect to onboarding page.
    If True: show normal nav (Exercise, Dashboard, Workout Plan).

---

### 8. Files to create or modify

CREATE:
  backend/routers/onboarding.py
  backend/schemas_onboarding.py
  recommendation/plan_matcher.py
  recommendation/plan_library.py
  frontend/pages/onboarding.py

MODIFY:
  backend/models.py          — add UserProfile model, update User
  backend/main.py            — register onboarding router
  frontend/app.py            — add onboarding status check after login
  frontend/pages/home.py     — redirect to onboarding after register
  recommendation/engine.py   — call plan_matcher for new users, LLM for returning users

---

### Coding standards

- All Python files: module docstring, type hints on all functions, no bare excepts
- All new endpoints: require JWT authentication via the existing get_current_user dependency
- All Pydantic models: use Field() with validation constraints
- All Streamlit pages: initialise required session_state keys at the top before use
- plan_library.py: each plan must be a complete, valid WeeklyPlan dict with all 7 days
- plan_matcher.py: never return None — always return a plan, even if it is the
  closest approximate match
- All form validation errors displayed to the user with st.error(), not raised as exceptions
```
