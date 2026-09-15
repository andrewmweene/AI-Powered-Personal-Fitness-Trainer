"""Pure analytics functions over serialized exercise session dictionaries."""

from __future__ import annotations

import statistics
from datetime import date, datetime, timedelta
from typing import Any


def _datetime(value: Any) -> datetime | None:
    """Parse a datetime value, accepting timezone-aware ISO strings."""
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return None
    return None


def calculate_posture_accuracy(scores: list[float]) -> float:
    """Return a percentage from normalized posture scores."""
    return float(sum(scores) / len(scores) * 100) if scores else 0.0


def count_reps(states: list[str]) -> int:
    """Count completed repetitions in a state sequence."""
    return sum(state == "COMPLETE" for state in states)


def calculate_total_sessions(sessions: list[dict]) -> int:
    """Return the number of sessions."""
    return len(sessions)


def calculate_total_reps(sessions: list[dict]) -> int:
    """Return total completed and attempted repetitions recorded."""
    return sum(int(session.get("total_reps", 0) or 0) for session in sessions)


def calculate_average_accuracy(sessions: list[dict]) -> float:
    """Return the mean non-null posture accuracy rounded to one decimal."""
    values = [float(s["posture_accuracy"]) for s in sessions if s.get("posture_accuracy") is not None]
    return round(statistics.mean(values), 1) if values else 0.0


def calculate_sessions_per_week(sessions: list[dict]) -> float:
    """Count sessions created during the preceding seven days."""
    cutoff = datetime.utcnow() - timedelta(days=7)
    return float(sum(1 for session in sessions if (created := _datetime(session.get("created_at"))) and created >= cutoff))


def calculate_average_reps_per_session(sessions: list[dict]) -> float:
    """Return average total repetitions per session."""
    return round(calculate_total_reps(sessions) / len(sessions), 1) if sessions else 0.0


def build_user_metrics_dict(sessions: list[dict]) -> dict[str, float | int]:
    """Build metrics consumed by the recommendation engine."""
    return {
        "avg_posture_accuracy": calculate_average_accuracy(sessions),
        "sessions_per_week": calculate_sessions_per_week(sessions),
        "avg_reps_per_session": calculate_average_reps_per_session(sessions),
        "total_sessions": calculate_total_sessions(sessions),
        "total_reps": calculate_total_reps(sessions),
    }


def calculate_streak(sessions: list[dict] | int, total_reps: int | None = None) -> tuple[int, int] | float:
    """Return current and best consecutive session-day streaks."""
    if isinstance(sessions, int):
        return float(sessions / total_reps * 100) if total_reps else 0.0
    dates = {created.date() for session in sessions if (created := _datetime(session.get("created_at")))}
    if not dates:
        return 0, 0
    ordered = sorted(dates)
    best = current = 1
    run = 1
    for previous, current_date in zip(ordered, ordered[1:]):
        run = run + 1 if current_date == previous + timedelta(days=1) else 1
        best = max(best, run)
    current = 0
    cursor = date.today()
    if cursor not in dates:
        cursor -= timedelta(days=1)
    while cursor in dates:
        current += 1
        cursor -= timedelta(days=1)
    return current, best


def calculate_weekly_breakdown(sessions: list[dict]) -> list[dict]:
    """Return session count and average accuracy for each of the last seven days."""
    result = []
    for offset in range(6, -1, -1):
        target = date.today() - timedelta(days=offset)
        day_sessions = [s for s in sessions if (created := _datetime(s.get("created_at"))) and created.date() == target]
        result.append({"date": target.isoformat(), "session_count": len(day_sessions), "avg_accuracy": calculate_average_accuracy(day_sessions)})
    return result


def calculate_accuracy_trend(sessions: list[dict], n: int = 30) -> list[dict]:
    """Return the last ``n`` session accuracies in chronological order."""
    ordered = sorted((s for s in sessions if _datetime(s.get("created_at"))), key=lambda s: _datetime(s.get("created_at")))
    return [{"session_num": index, "accuracy": round(float(session.get("posture_accuracy") or 0), 1)} for index, session in enumerate(ordered[-n:], 1)]


def calculate_by_exercise(sessions: list[dict]) -> list[dict]:
    """Group sessions by exercise and return count plus average accuracy."""
    groups: dict[str, list[dict]] = {}
    for session in sessions:
        groups.setdefault(str(session.get("exercise_type", "Unknown")), []).append(session)
    return sorted(
        [{"exercise": exercise, "count": len(group), "avg_accuracy": calculate_average_accuracy(group)} for exercise, group in groups.items()],
        key=lambda item: item["count"], reverse=True,
    )
