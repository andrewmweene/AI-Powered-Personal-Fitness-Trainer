"""Progress dashboard page displaying analytics summaries and charts."""

from __future__ import annotations

import httpx
import pandas as pd
import streamlit as st

from analytics.charts import (
    make_accuracy_gauge,
    make_accuracy_trend_chart,
    make_exercise_breakdown_chart,
    make_weekly_sessions_chart,
)
from analytics.progress import (
    calculate_accuracy_trend,
    calculate_by_exercise,
    calculate_streak,
    calculate_weekly_breakdown,
)


def _get_backend_url() -> str:
    return st.secrets.get("backend_url", "http://localhost:8000")


def _get_headers() -> dict[str, str]:
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _fetch_api(path: str) -> dict | None:
    try:
        response = httpx.get(path, headers=_get_headers(), timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def render() -> None:
    """Render the dashboard page for user progress insights."""
    st.title("Progress Dashboard")
    st.write("Track your workout history, posture accuracy, and improvements over time.")

    backend_url = _get_backend_url().rstrip("/")
    summary = _fetch_api(f"{backend_url}/analytics/summary") or {}
    recent_sessions = _fetch_api(f"{backend_url}/sessions/recent/30") or []

    current_streak_days, best_streak_days = calculate_streak(recent_sessions)
    avg_accuracy = float(summary.get("avg_accuracy", 0.0))
    total_sessions = int(summary.get("total_sessions", 0))
    total_reps = int(summary.get("total_reps", 0))

    trend_data = calculate_accuracy_trend(recent_sessions, n=30)
    weekly_data = calculate_weekly_breakdown(recent_sessions)
    exercise_data = calculate_by_exercise(recent_sessions)

    delta = 0.0
    if len(trend_data) >= 2:
        delta = trend_data[-1]["accuracy"] - trend_data[-2]["accuracy"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total sessions", total_sessions)
    col2.metric("Total reps", total_reps)
    col3.metric("Avg accuracy", f"{avg_accuracy:.1f}%", delta=f"{delta:+.1f}%")
    col4.metric("Streak", f"{current_streak_days} days")

    chart_col1, chart_col2 = st.columns(2)
    chart_col1.plotly_chart(make_accuracy_trend_chart(trend_data), use_container_width=True)
    chart_col2.plotly_chart(make_weekly_sessions_chart(weekly_data), use_container_width=True)

    st.plotly_chart(make_exercise_breakdown_chart(exercise_data), use_container_width=True)

    gauge_col, table_col = st.columns(2)
    gauge_col.plotly_chart(make_accuracy_gauge(avg_accuracy), use_container_width=True)

    if trend_data:
        table_data = []
        for session in sorted(trend_data, key=lambda item: item.get("created_at", ""), reverse=True)[:10]:
            table_data.append(
                {
                    "Date": session.get("created_at", "")[:10],
                    "Exercise": session.get("exercise_type", "Unknown"),
                    "Reps": int(session.get("total_reps", 0)),
                    "Correct": int(session.get("correct_reps", 0)),
                    "Accuracy": f"{float(session.get('posture_accuracy', 0.0)):.1f}%",
                    "Duration": float(session.get("duration_seconds", 0.0)),
                }
            )
        df = pd.DataFrame(table_data)
        table_col.dataframe(df, use_container_width=True, hide_index=True)
    else:
        table_col.info("No recent session data available to display.")

    if summary is None or trend_data is None:
        st.warning("Unable to load analytics data from the backend. Check your backend URL and authentication settings.")
