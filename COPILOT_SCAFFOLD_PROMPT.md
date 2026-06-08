# Copilot Scaffold Prompt — AI Personal Trainer

> **How to use:** Open GitHub Copilot Chat in VS Code. Paste the entire prompt below
> into the chat window and send it. Copilot will generate the full project skeleton.
> After scaffolding, open each file in `docs/` to guide implementation of each feature.

---

## Prompt to paste into Copilot Chat

```
You are helping me scaffold a Python project called "AI Personal Trainer" — 
an AI-powered fitness coaching system that uses computer vision to analyse 
exercise posture in real time, track workout performance, and generate 
personalised workout recommendations.

Please create the full project folder structure and all starter files listed 
below. For each file, include:
- Module-level docstring describing the file's purpose
- All necessary imports
- Empty function/class stubs with detailed docstrings explaining what each 
  function must do, its parameters, and its return type
- TODO comments inside each stub marking exactly what needs to be implemented
- Type hints on all function signatures

---

## Tech stack

- Python 3.11+
- MediaPipe (pose estimation)
- OpenCV (video capture and overlay rendering)
- NumPy (angle calculations)
- FastAPI (REST API backend)
- SQLAlchemy + Alembic (ORM and database migrations)
- PostgreSQL (database)
- Streamlit (frontend UI)
- scikit-learn (recommendation engine)
- Pandas (data processing)
- bcrypt (password hashing)
- python-jose (JWT tokens)
- google-generativeai (Gemini API for LLM workout plans)
- pytest (testing)

---

## Project structure to generate

ai-personal-trainer/
├── pose_engine/
│   ├── __init__.py
│   ├── detector.py          # MediaPipe pose detection wrapper
│   ├── angle_utils.py       # Joint angle calculation utilities
│   ├── state_machine.py     # Exercise state machine (s1/s2/s3)
│   ├── feedback.py          # Feedback message generation
│   ├── camera.py            # OpenCV webcam capture manager
│   └── exercises/
│       ├── __init__.py
│       ├── base_exercise.py # Abstract base class for all exercises
│       ├── squat.py         # Squat exercise logic
│       ├── bicep_curl.py    # Bicep curl exercise logic
│       ├── pushup.py        # Push-up exercise logic
│       ├── dumbbell_fly.py  # Dumbbell fly exercise logic
│       └── kickback.py      # Dumbbell kickback exercise logic
│
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point, router registration
│   ├── database.py          # SQLAlchemy engine, session factory
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth.py              # bcrypt hashing, JWT token creation/verification
│   ├── dependencies.py      # FastAPI dependency injection (get_db, get_current_user)
│   └── routers/
│       ├── __init__.py
│       ├── users.py         # User registration and profile endpoints
│       ├── sessions.py      # Exercise session recording endpoints
│       ├── analytics.py     # Dashboard analytics endpoints
│       └── recommendations.py # Workout plan endpoints
│
├── recommendation/
│   ├── __init__.py
│   ├── engine.py            # Main recommendation orchestrator
│   ├── rule_based.py        # scikit-learn rule-based difficulty model
│   ├── llm_planner.py       # Gemini API weekly plan generator
│   └── schemas.py           # WorkoutPlan and Exercise pydantic models
│
├── analytics/
│   ├── __init__.py
│   ├── metrics.py           # Posture accuracy, rep count, streak calculations
│   ├── charts.py            # Plotly chart generation functions
│   └── progress.py          # Long-term progress trend analysis
│
├── frontend/
│   ├── app.py               # Streamlit multipage app entry point
│   └── pages/
│       ├── home.py          # Landing page, login, registration
│       ├── exercise.py      # Live webcam exercise page
│       ├── dashboard.py     # Progress dashboard page
│       └── workout_plan.py  # Generated workout plan page
│
├── docs/
│   ├── POSE_ENGINE.md
│   ├── BACKEND.md
│   ├── FRONTEND.md
│   ├── RECOMMENDATION.md
│   └── ANALYTICS_DASHBOARD.md
│
├── tests/
│   ├── __init__.py
│   ├── test_angle_utils.py
│   ├── test_state_machine.py
│   ├── test_auth.py
│   └── test_recommendations.py
│
├── alembic/
│   └── env.py
│
├── .env.example
├── requirements.txt
├── README.md
├── docker-compose.yml
└── alembic.ini

---

## Key implementation details to encode in stubs

### pose_engine/detector.py
- Class `PoseDetector` wrapping `mp.solutions.pose.Pose`
- `__init__` accepts `min_detection_confidence` and `min_tracking_confidence`
- `detect(frame: np.ndarray) -> mp.solutions.pose.PoseLandmark | None`
- `draw_landmarks(frame, results) -> np.ndarray`

### pose_engine/angle_utils.py
- `calculate_angle(a, b, c) -> float`
  Uses numpy arctan2 to compute angle at point b given three (x,y) coordinate 
  tuples a, b, c. Returns angle in degrees (0-360).
- `get_landmark_coords(landmarks, landmark_id, frame_shape) -> tuple[int, int]`
  Converts normalised MediaPipe landmark coordinates to pixel coordinates.
- `calculate_offset_angle(p1, p2) -> float`
  Computes the angle between two points relative to vertical — used to verify 
  correct camera orientation (side vs frontal view).

### pose_engine/state_machine.py
- Class `ExerciseStateMachine`
- States: `REST`, `TRANSITION`, `COMPLETE`
- `update(angle: float, thresholds: dict) -> tuple[str, bool]`
  Returns (current_state, rep_completed). A rep is counted only when the 
  full sequence REST->TRANSITION->COMPLETE->TRANSITION->REST is observed.
- `reset()` — resets counter and state on inactivity timeout

### pose_engine/exercises/base_exercise.py
- Abstract class `BaseExercise`
- Abstract method `get_required_landmarks() -> list[int]`
- Abstract method `get_angle_thresholds() -> dict`
- Abstract method `get_feedback(angle: float, state: str) -> str`
- Abstract method `requires_side_view() -> bool`

### backend/models.py
Generate SQLAlchemy models for:
- `User` (id, username, email, hashed_password, age, fitness_level, goal, created_at)
- `ExerciseSession` (id, user_id FK, exercise_type, total_reps, correct_reps, 
  incorrect_reps, posture_accuracy, duration_seconds, created_at)
- `WorkoutPlan` (id, user_id FK, plan_data JSON, generated_at, week_start_date)
- `PostureFeedbackLog` (id, session_id FK, timestamp, feedback_message, joint_angle)

### backend/auth.py
- `hash_password(plain: str) -> str` using bcrypt
- `verify_password(plain: str, hashed: str) -> bool`
- `create_access_token(data: dict, expires_delta: timedelta) -> str` using JWT
- `decode_access_token(token: str) -> dict | None`

### recommendation/rule_based.py
- `build_model() -> sklearn.pipeline.Pipeline`
  Trains a simple decision tree on synthetic data mapping 
  (avg_accuracy, sessions_per_week, avg_reps) -> difficulty_level (0,1,2)
- `predict_difficulty(user_metrics: dict) -> str`
  Returns "beginner", "intermediate", or "advanced"

### recommendation/llm_planner.py
- `generate_weekly_plan(user_profile: dict, difficulty: str) -> dict`
  Calls Gemini API with a structured prompt. Returns JSON with keys:
  monday, tuesday, wednesday, thursday, friday, saturday, sunday —
  each containing a list of {exercise, sets, reps, notes}.
  Must handle API errors gracefully and fall back to rule_based plan.

### frontend/pages/exercise.py
- Use `st.camera_input()` or `cv2.VideoCapture` in a Streamlit loop
- Display the annotated frame via `st.image()`
- Show rep counter, posture accuracy percentage, and live feedback text
- On session end, POST session data to the FastAPI backend

---

## .env.example contents
DATABASE_URL=postgresql://postgres.otteffbxmquiuwfarjzh:+FREAK9@aws-0-eu-west-1.pooler.supabase.com:6543/postgres
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GEMINI_API_KEY=your-gemini-api-key-here

---

## requirements.txt — include all packages with pinned major versions

mediapipe>=0.10
opencv-python>=4.8
numpy>=1.26
fastapi>=0.110
uvicorn[standard]>=0.27
sqlalchemy>=2.0
alembic>=1.13
psycopg2-binary>=2.9
pydantic[email]>=2.6
python-jose[cryptography]>=3.3
bcrypt>=4.1
passlib>=1.7
streamlit>=1.32
scikit-learn>=1.4
pandas>=2.2
plotly>=5.20
google-generativeai>=0.5
python-dotenv>=1.0
pytest>=8.0
httpx>=0.27

---

## docker-compose.yml — include a PostgreSQL service and the app service

---

Please generate all files now. Each Python file must have complete stubs 
with docstrings and TODO comments. Do not leave any file empty.
```
