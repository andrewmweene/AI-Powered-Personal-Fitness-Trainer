# Feature guide: frontend (`frontend/`)

> Open this file alongside the relevant page file in VS Code.
> Use Copilot inline chat (`Ctrl+I`) on each stub.

---

## Overview

The frontend is a Streamlit multipage application. Streamlit is chosen because
it lets us embed the live OpenCV webcam feed directly in a Python web app
without needing a separate React/JavaScript build step.

**Pages:**

| File | URL path | Purpose |
|---|---|---|
| `app.py` | `/` | Entry point, session state init, navigation |
| `pages/home.py` | `/home` | Login and registration forms |
| `pages/exercise.py` | `/exercise` | Live webcam workout session |
| `pages/dashboard.py` | `/dashboard` | Progress charts and history |
| `pages/workout_plan.py` | `/workout_plan` | Generated weekly plan |

---

## `app.py` — entry point

```python
# Copilot prompt:
# Configure Streamlit page: title="AI Personal Trainer",
#   layout="wide", initial_sidebar_state="expanded".
# Initialise st.session_state keys if not already set:
#   "token": None  (JWT token string after login)
#   "user": None   (user dict from /users/me)
#   "api_base": "http://localhost:8000"
# Build a sidebar navigation:
#   If session_state.token is None, show links to Home only.
#   If logged in, show: Exercise, Dashboard, Workout Plan, and a Logout button.
#   Logout button clears token and user from session_state and reruns.
# Use st.switch_page or st.navigation to route to the selected page.
```

---

## `pages/home.py` — login and registration

```python
# Copilot prompt:
# Implement two Streamlit tabs: "Login" and "Register".
#
# LOGIN TAB:
#   st.text_input for username, st.text_input(type="password") for password.
#   On "Login" button click:
#     POST to {api_base}/users/login with {username, password}.
#     If 200: store token in session_state.token.
#              GET {api_base}/users/me with Authorization: Bearer {token}.
#              Store response JSON in session_state.user.
#              st.success("Welcome back!") then st.switch_page("pages/exercise.py").
#     If error: st.error("Invalid username or password").
#
# REGISTER TAB:
#   Inputs: username, email, password, confirm_password, age (number),
#     fitness_level (selectbox: beginner/intermediate/advanced),
#     goal (selectbox: weight_loss/muscle_gain/endurance/general_fitness).
#   Validate passwords match before submitting.
#   POST to {api_base}/users/register.
#   On success: st.success("Account created! Please log in.") and switch to Login tab.
#   On error: display the error message from the API response.
```

---

## `pages/exercise.py` — live webcam exercise session

This is the most complex page. It runs a real-time OpenCV loop inside Streamlit.

### Architecture note

Streamlit reruns the entire script on each widget interaction. For a real-time
video loop, we use `st.empty()` as a placeholder and update it in a `while` loop.
The loop exits when the user clicks "Stop session".

```python
# Copilot prompt — overall structure:
# 1. Guard: if not st.session_state.token, st.warning and st.stop().
# 2. Sidebar: exercise selector (selectbox with Squat, Bicep Curl, Push-up,
#      Dumbbell Fly, Dumbbell Kickback).
# 3. Layout: two columns — left (video feed, 60% width), right (stats, 40% width).
# 4. Left column: st.empty() placeholder for the annotated frame.
# 5. Right column: three st.metric placeholders for Reps, Accuracy %, Feedback.
# 6. "Start Session" and "Stop Session" buttons in session_state.
#
# Copilot prompt — the video loop:
# Import PoseDetector, CameraManager, ExerciseStateMachine.
# Import the selected exercise class dynamically based on selectbox value.
# Instantiate detector, state_machine, exercise.
# correct_reps = 0; incorrect_reps = 0; start_time = time.time()
#
# with CameraManager() as cam:
#   while st.session_state.get("running", False):
#     frame = cam.read_frame()
#     results = detector.detect(frame)
#     if results.pose_landmarks:
#       coords = extract_landmark_coords(results, exercise, frame.shape)
#       angle = calculate_angle(*coords)
#       state, rep_done = state_machine.update(angle, exercise.get_angle_thresholds())
#       if rep_done:
#         if state_machine was valid: correct_reps += 1
#         else: incorrect_reps += 1
#       feedback = exercise.get_feedback(angle, state)
#       frame = draw_feedback_overlay(frame, correct_reps,
#               correct_reps/(correct_reps+incorrect_reps+1e-6)*100, feedback, state)
#     frame_placeholder.image(frame, channels="RGB", use_container_width=True)
#     reps_metric.metric("Reps", correct_reps)
#     accuracy_metric.metric("Accuracy", f"{accuracy:.0f}%")
#     feedback_placeholder.info(feedback or "Looking good!")
#
# Copilot prompt — on stop:
# duration = int(time.time() - start_time)
# POST to {api_base}/sessions/ with session data and Bearer token.
# Show st.success("Session saved!") with a summary.
# Offer "View Dashboard" button.
```

### Handling the camera view check

Before entering the main loop, check that the user is in the correct orientation:

```python
# Copilot prompt:
# Before starting the rep-counting loop, run 30 frames of orientation check.
# For each frame, extract NOSE (0) and LEFT_SHOULDER (11) landmarks.
# Call calculate_offset_angle(nose_coords, shoulder_coords).
# If exercise.requires_side_view() and offset > 65:
#   Show st.warning("Please position your camera to your side") and continue.
# If not requires_side_view() and offset < 35:
#   Show st.warning("Please face the camera directly") and continue.
# Once orientation is confirmed for 10 consecutive frames, begin the main loop.
```

---

## `pages/dashboard.py` — progress visualisation

```python
# Copilot prompt:
# Guard: require token.
# Fetch data:
#   GET {api_base}/analytics/summary  -> summary dict
#   GET {api_base}/analytics/weekly   -> list of {date, sessions, avg_accuracy}
#   GET {api_base}/analytics/by-exercise -> list of {exercise, count, avg_accuracy}
#   GET {api_base}/analytics/accuracy-trend -> list of {session_num, accuracy}
#
# Layout:
#   Row 1: Four st.metric cards in columns:
#     Total sessions, Total reps, Average accuracy %, Current streak (days)
#
#   Row 2: Two Plotly charts side by side:
#     Left: Line chart of accuracy_trend (x=session number, y=accuracy %)
#           Title: "Posture accuracy over time"
#     Right: Bar chart of weekly sessions (x=date, y=session count)
#           Title: "Sessions per day (last 7 days)"
#
#   Row 3: Horizontal bar chart of sessions by exercise type.
#           Title: "Workouts by exercise"
#
#   Row 4: st.dataframe showing last 10 sessions with columns:
#     Date, Exercise, Reps, Correct reps, Accuracy%, Duration
#
# Use st.plotly_chart(fig, use_container_width=True) for all charts.
# All charts must use a clean theme: template="plotly_white".
```

---

## `pages/workout_plan.py` — generated weekly plan

```python
# Copilot prompt:
# Guard: require token.
# GET {api_base}/recommendations/plan with Bearer token.
# Parse the plan_data JSON.
#
# Display layout:
#   Header: "Your workout plan — week of {week_start_date}"
#   Subtitle: "Generated based on your recent performance"
#   "Refresh Plan" button -> POST to /recommendations/plan/refresh
#
#   Show 7 day cards using st.columns (arrange 4 columns on row 1, 3 on row 2):
#   Each card shows:
#     Day name (bold header)
#     If rest day: "Rest day" in muted text
#     If workout day: list of exercises as:
#       "{exercise_name} — {sets} sets x {reps} reps"
#       Small notes in muted italic text below each exercise
#
#   Use st.container() with st.markdown and custom HTML for card styling.
#   Highlight today's day card with a coloured border.
```

---

## Running the frontend

```bash
# Make sure the backend is running first on port 8000, then:
streamlit run frontend/app.py
```

The app will open at `http://localhost:8501`.

---

## Streamlit session state reference

Always check `if "token" not in st.session_state` before accessing session state
keys — Streamlit reruns the entire page on any widget interaction, so state can
be lost if not initialised in `app.py`.

Key state variables used across pages:

| Key | Type | Description |
|---|---|---|
| `token` | `str \| None` | JWT access token |
| `user` | `dict \| None` | Current user profile from `/users/me` |
| `api_base` | `str` | Base URL of the FastAPI backend |
| `running` | `bool` | Whether the webcam exercise loop is active |
| `selected_exercise` | `str` | Currently selected exercise name |
