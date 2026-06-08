"""Plotly chart helpers for progress and posture analytics."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import plotly.graph_objects as go

PRIMARY_COLOR = "#1976D2"
SUCCESS_COLOR = "#388E3C"
WARNING_COLOR = "#F57C00"
DANGER_COLOR = "#D32F2F"


def make_accuracy_trend_chart(trend_data: list[dict[str, Any]]) -> go.Figure:
    """Create a posture accuracy trend line chart."""
    x = [row["session_num"] for row in trend_data]
    y = [row["accuracy"] for row in trend_data]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines+markers",
            line=dict(color=PRIMARY_COLOR, width=3),
            marker=dict(color=PRIMARY_COLOR),
            name="Accuracy",
            fill="tozeroy",
            fillcolor="rgba(25, 118, 210, 0.1)",
        )
    )
    fig.add_shape(
        type="line",
        x0=min(x) if x else 0,
        x1=max(x) if x else 0,
        y0=80,
        y1=80,
        line=dict(color="rgba(25, 118, 210, 0.6)", width=2, dash="dash"),
    )
    fig.add_annotation(
        x=max(x) if x else 0,
        y=80,
        xanchor="left",
        yanchor="bottom",
        text="Target (80%)",
        showarrow=False,
        font=dict(color=PRIMARY_COLOR),
    )
    fig.update_layout(
        template="plotly_white",
        title="Posture accuracy over time",
        xaxis_title="Session",
        yaxis_title="Accuracy (%)",
        yaxis=dict(range=[0, 100]),
        margin=dict(t=50, b=40, l=40, r=20),
    )
    return fig


def make_weekly_sessions_chart(weekly_data: list[dict[str, Any]]) -> go.Figure:
    """Create a weekly sessions bar chart for the last seven days."""
    labels = []
    counts = []
    text = []
    for row in weekly_data:
        date_label = row["date"]
        formatted = date_label
        try:
            parsed = datetime.fromisoformat(date_label)
            formatted = parsed.strftime("%a %d")
        except ValueError:
            pass
        labels.append(formatted)
        counts.append(int(row.get("session_count", 0)))
        text.append(str(int(row.get("session_count", 0))))

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=counts,
            marker_color=PRIMARY_COLOR,
            text=text,
            textposition="outside",
        )
    )
    fig.update_layout(
        template="plotly_white",
        title="Sessions per day (last 7 days)",
        xaxis_title="",
        yaxis_title="Sessions",
        margin=dict(t=50, b=40, l=40, r=20),
    )
    return fig


def make_exercise_breakdown_chart(breakdown_data: list[dict[str, Any]]) -> go.Figure:
    """Create a horizontal bar chart grouping workouts by exercise."""
    exercises = [row["exercise"] for row in breakdown_data]
    counts = [int(row.get("count", 0)) for row in breakdown_data]
    avg_accuracies = [float(row.get("avg_accuracy", 0.0)) for row in breakdown_data]
    colors = [
        SUCCESS_COLOR if val >= 80 else WARNING_COLOR if 60 <= val < 80 else DANGER_COLOR
        for val in avg_accuracies
    ]
    text = [f"Avg: {val:.0f}%" for val in avg_accuracies]

    fig = go.Figure(
        go.Bar(
            x=counts,
            y=exercises,
            orientation="h",
            marker_color=colors,
            text=text,
            textposition="inside",
        )
    )
    fig.update_layout(
        template="plotly_white",
        title="Workouts by exercise",
        xaxis_title="Count",
        yaxis_title="Exercise",
        margin=dict(t=50, b=40, l=120, r=20),
    )
    return fig


def make_accuracy_gauge(avg_accuracy: float) -> go.Figure:
    """Create a gauge chart showing the average posture accuracy."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=avg_accuracy,
            title={"text": "Average posture accuracy"},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "darkgray"},
                "bar": {"color": PRIMARY_COLOR},
                "steps": [
                    {"range": [0, 60], "color": DANGER_COLOR},
                    {"range": [60, 80], "color": WARNING_COLOR},
                    {"range": [80, 100], "color": SUCCESS_COLOR},
                ],
            },
        )
    )
    fig.update_layout(template="plotly_white", margin=dict(t=50, b=20, l=20, r=20))
    return fig
