"""Long-term progress trend analysis utilities."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, date, timedelta
from typing import Sequence


def _parse_session_date(created_at: str) -> date | None:
    """Parse an ISO formatted created_at timestamp to a local calendar date."""
    try:
        parsed = datetime.fromisoformat(created_at)
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone()
    return parsed.date()


def _sorted_unique_dates(sessions: list[dict]) -> list[date]:
    """Return unique session dates sorted descending."""
    dates = {
        session_date
        for session in (
            _parse_session_date(session.get("created_at", ""))
            for session in sessions
        )
        if session_date is not None
    }
    return sorted(dates, reverse=True)


def calculate_streak(sessions: list[dict]) -> tuple[int, int]:
    """Return the current and best streak of consecutive session days."""
    unique_dates = _sorted_unique_dates(sessions)
    if not unique_dates:
        return 0, 0

    today = date.today()
    current_streak = 0
    check_date = today
    while True:
        if check_date in unique_dates:
            current_streak += 1
            check_date -= timedelta(days=1)
            continue
        if current_streak == 0 and today not in unique_dates:
            yesterday = today - timedelta(days=1)
            if yesterday in unique_dates:
                current_streak = 1
        break

    best_streak = 0
    running_streak = 0
    previous_date: date | None = None
    for session_date in sorted(unique_dates):
        if previous_date is None:
            running_streak = 1
        elif session_date == previous_date + timedelta(days=1):
            running_streak += 1
        else:
            best_streak = max(best_streak, running_streak)
            running_streak = 1
        previous_date = session_date
    best_streak = max(best_streak, running_streak)

    return current_streak, best_streak


def calculate_weekly_breakdown(sessions: list[dict]) -> list[dict]:
    """Return a breakdown of session counts and accuracy for the last seven days."""
    today = date.today()
    window_start = today - timedelta(days=6)
    day_map: dict[date, list[float]] = defaultdict(list)

    for session in sessions:
        session_date = _parse_session_date(session.get("created_at", ""))
        if session_date is None:
            continue
        if window_start <= session_date <= today:
            day_map[session_date].append(float(session.get("posture_accuracy", 0.0)))

    breakdown: list[dict] = []
    for index in range(7):
        current_day = window_start + timedelta(days=index)
        accuracies = day_map.get(current_day, [])
        avg_accuracy = float(sum(accuracies) / len(accuracies)) if accuracies else 0.0
        breakdown.append(
            {
                "date": current_day.isoformat(),
                "session_count": len(accuracies),
                "avg_accuracy": avg_accuracy,
            }
        )
    return breakdown


def calculate_accuracy_trend(sessions: list[dict], n: int = 30) -> list[dict]:
    """Return the last n session accuracies ordered ascending by created_at."""
    parsed_sessions = []
    for session in sessions:
        created_at = session.get("created_at", "")
        parsed_date = _parse_session_date(created_at)
        if parsed_date is None:
            continue
        parsed_sessions.append((parsed_date, float(session.get("posture_accuracy", 0.0))))

    parsed_sessions.sort(key=lambda item: item[0])
    trend = []
    for index, (_, accuracy) in enumerate(parsed_sessions[-n:], start=1):
        trend.append({"session_num": index, "accuracy": accuracy})
    return trend


def calculate_by_exercise(sessions: list[dict]) -> list[dict]:
    """Aggregate sessions by exercise type, returning counts and average accuracy."""
    stats: dict[str, dict[str, float | int]] = {}
    for session in sessions:
        exercise = str(session.get("exercise_type", "Unknown"))
        if exercise not in stats:
            stats[exercise] = {"count": 0, "accuracy_sum": 0.0}
        stats[exercise]["count"] += 1
        stats[exercise]["accuracy_sum"] += float(session.get("posture_accuracy", 0.0))

    results = []
    for exercise, values in stats.items():
        count = int(values["count"])
        avg_accuracy = float(values["accuracy_sum"]) / count if count else 0.0
        results.append(
            {"exercise": exercise, "count": count, "avg_accuracy": avg_accuracy}
        )

    return sorted(results, key=lambda item: item["count"], reverse=True)


def analyze_trends(accuracy_history: Sequence[float]) -> dict[str, float]:
    """Analyze long-term progress trends from posture accuracy history."""
    if not accuracy_history:
        return {"trend": 0.0, "improvement": 0.0}
    start = accuracy_history[0]
    end = accuracy_history[-1]
    improvement = end - start
    trend = improvement / len(accuracy_history) if accuracy_history else 0.0
    return {"trend": float(trend), "improvement": float(improvement)}
