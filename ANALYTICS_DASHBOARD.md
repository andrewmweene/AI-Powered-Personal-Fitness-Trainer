# Feature guide: analytics and dashboard (`analytics/`)

> Open this file alongside the relevant source file in VS Code.
> Use Copilot inline chat (`Ctrl+I`) on each stub.

---

## Overview

The analytics module processes stored session data to produce the statistics and
charts shown on the Dashboard page. It sits between the database (via the
FastAPI backend) and the Streamlit frontend.

Three files:

| File | Responsibility |
|---|---|
| `metrics.py` | Pure functions that calculate summary statistics from session lists |
| `charts.py` | Plotly figure factories — each function returns a `go.Figure` |
| `progress.py` | Trend analysis and streak calculation logic |

---

## `metrics.py` — summary statistics

All functions here accept a list of session dicts (as returned by the
`/sessions/` API endpoint) and return computed values.

```python
# Copilot prompt:
# Implement the following functions. Each takes sessions: list[dict] as input.
# Session dict keys: exercise_type, total_reps, correct_reps, incorrect_reps,
#   posture_accuracy, duration_seconds, created_at (ISO datetime string).
#
# calculate_total_sessions(sessions) -> int:
#   Return len(sessions).
#
# calculate_total_reps(sessions) -> int:
#   Return sum of total_reps across all sessions.
#
# calculate_average_accuracy(sessions) -> float:
#   Return mean of posture_accuracy. Return 0.0 if sessions is empty.
#
# calculate_sessions_per_week(sessions) -> float:
#   Count sessions in the last 7 days (compare created_at to today - 7 days).
#   Return the count as a float.
#
# calculate_average_reps_per_session(sessions) -> float:
#   Return total_reps / len(sessions) if sessions else 0.0.
#
# build_user_metrics_dict(sessions) -> dict:
#   Return {
#     "avg_posture_accuracy": calculate_average_accuracy(sessions),
#     "sessions_per_week": calculate_sessions_per_week(sessions),
#     "avg_reps_per_session": calculate_average_reps_per_session(sessions),
#   }
#   This dict is the input format expected by recommendation/rule_based.py.
```

---

## `progress.py` — streak and trend calculations

```python
# Copilot prompt:
# Implement calculate_streak(sessions: list[dict]) -> tuple[int, int]:
#   Returns (current_streak_days, best_streak_days).
#   A "streak day" is any calendar day (in user's local timezone) on which
#   at least one session occurred.
#   Algorithm:
#     1. Extract unique dates from created_at strings (date part only).
#     2. Sort dates descending.
#     3. current_streak: count consecutive days starting from today going back.
#        If today has no session, check if yesterday does. If neither, streak = 0.
#     4. best_streak: scan the full sorted date list for the longest consecutive run.
#     5. Return (current_streak, best_streak).
#
# Implement calculate_weekly_breakdown(sessions: list[dict]) -> list[dict]:
#   Return one dict per day for the last 7 days:
#   [{"date": "2026-03-18", "session_count": 2, "avg_accuracy": 78.5}, ...]
#   Days with no sessions should still appear with session_count=0, avg_accuracy=0.
#
# Implement calculate_accuracy_trend(sessions: list[dict], n: int = 30) -> list[dict]:
#   Take the last n sessions ordered by created_at ascending.
#   Return [{"session_num": 1, "accuracy": 65.0}, {"session_num": 2, ...}, ...]
#   This is used to draw the accuracy-over-time line chart.
#
# Implement calculate_by_exercise(sessions: list[dict]) -> list[dict]:
#   Group sessions by exercise_type.
#   Return [{"exercise": "Squat", "count": 5, "avg_accuracy": 72.3}, ...]
#   Sort by count descending.
```

---

## `charts.py` — Plotly figure factories

Each function returns a `plotly.graph_objects.Figure`. The Streamlit dashboard
calls these functions and renders them with `st.plotly_chart(fig, use_container_width=True)`.

```python
# Copilot prompt:
# All charts use template="plotly_white" and the colour palette:
#   primary = "#1976D2" (blue), success = "#388E3C" (green), 
#   warning = "#F57C00" (amber), danger = "#D32F2F" (red)
#
# make_accuracy_trend_chart(trend_data: list[dict]) -> go.Figure:
#   Line chart. x = session_num, y = accuracy.
#   Add a horizontal dashed line at y=80 labelled "Target (80%)".
#   Colour the line blue. Fill area below the line with light blue opacity 0.1.
#   Title: "Posture accuracy over time"
#   Y-axis: 0-100, label "Accuracy (%)"
#   X-axis: label "Session"
#
# make_weekly_sessions_chart(weekly_data: list[dict]) -> go.Figure:
#   Bar chart. x = date (formatted as "Mon 18"), y = session_count.
#   Colour bars blue. Add text labels on top of each bar.
#   Title: "Sessions per day (last 7 days)"
#
# make_exercise_breakdown_chart(breakdown_data: list[dict]) -> go.Figure:
#   Horizontal bar chart. y = exercise name, x = count.
#   Colour bars by avg_accuracy: green if >= 80, amber if 60-79, red if < 60.
#   Show avg_accuracy as text label on each bar: "Avg: {val:.0f}%"
#   Title: "Workouts by exercise"
#
# make_accuracy_gauge(avg_accuracy: float) -> go.Figure:
#   Gauge chart (go.Indicator mode="gauge+number").
#   Range 0-100. Steps: red 0-60, amber 60-80, green 80-100.
#   Show the needle pointing at avg_accuracy.
#   Title: "Average posture accuracy"
```

---

## Dashboard layout reference

The `pages/dashboard.py` Streamlit page assembles these components:

```
┌─────────────────────────────────────────────────────────────┐
│  Total sessions   Total reps   Avg accuracy   Current streak│  ← st.columns(4) with st.metric
├──────────────────────────────┬──────────────────────────────┤
│  Accuracy trend (line chart) │  Weekly sessions (bar chart) │  ← st.columns(2)
├──────────────────────────────┴──────────────────────────────┤
│  Exercise breakdown (horizontal bar)                        │  ← full width
├──────────────────────────────┬──────────────────────────────┤
│  Accuracy gauge              │  Last 10 sessions table      │  ← st.columns(2)
└──────────────────────────────┴──────────────────────────────┘
```

```python
# Copilot prompt for the full dashboard assembly:
# Fetch all required data from the API endpoints.
# Row 1 — metric cards:
#   col1, col2, col3, col4 = st.columns(4)
#   col1.metric("Total sessions", summary["total_sessions"])
#   col2.metric("Total reps", summary["total_reps"])
#   col3.metric("Avg accuracy", f"{summary['avg_accuracy']:.1f}%",
#               delta="+2.3%" if improving else "-1.1%")
#   col4.metric("Streak", f"{summary['current_streak_days']} days")
#
# Row 2 — trend and weekly charts side by side
# Row 3 — exercise breakdown full width
# Row 4 — gauge and table side by side
#   Table: st.dataframe(df, use_container_width=True, hide_index=True)
#   df columns: Date, Exercise, Reps, Correct, Accuracy, Duration
```

---

## Testing analytics

```bash
# Unit test the pure functions in metrics.py and progress.py:
pytest tests/ -k "analytics" -v

# Quick sanity check with fake data:
python -c "
from analytics.metrics import calculate_average_accuracy, build_user_metrics_dict

fake = [
    {'exercise_type': 'Squat', 'total_reps': 10, 'correct_reps': 8,
     'posture_accuracy': 80.0, 'duration_seconds': 120,
     'created_at': '2026-03-18T10:00:00'},
    {'exercise_type': 'Bicep Curl', 'total_reps': 12, 'correct_reps': 9,
     'posture_accuracy': 75.0, 'duration_seconds': 90,
     'created_at': '2026-03-17T10:00:00'},
]
print(calculate_average_accuracy(fake))   # expected: 77.5
print(build_user_metrics_dict(fake))
"
```
