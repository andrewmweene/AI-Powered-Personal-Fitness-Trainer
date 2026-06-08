"""Dashboard analytics endpoints for summarizing workout progress."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..dependencies import get_current_user, get_db
from ..models import ExerciseSession
from ..schemas import AnalyticsSummary
from analytics.progress import calculate_streak, calculate_weekly_breakdown, calculate_by_exercise, calculate_accuracy_trend
from analytics.metrics import calculate_total_reps, calculate_average_accuracy

router = APIRouter()


def _serialize_sessions(sessions: List[ExerciseSession]) -> list[dict]:
    return [
        {
            "id": s.id,
            "exercise_type": s.exercise_type,
            "total_reps": s.total_reps,
            "correct_reps": s.correct_reps,
            "incorrect_reps": s.incorrect_reps,
            "posture_accuracy": float(s.posture_accuracy) if s.posture_accuracy is not None else 0.0,
            "duration_seconds": s.duration_seconds,
            "created_at": s.created_at.isoformat() if s.created_at is not None else "",
        }
        for s in sessions
    ]


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> AnalyticsSummary:
    """Return aggregated analytics for the current user's exercise history."""
    sessions = db.query(ExerciseSession).filter(ExerciseSession.user_id == current_user.id).all()
    serialized = _serialize_sessions(sessions)
    total_sessions = len(serialized)
    total_reps = calculate_total_reps(serialized)
    avg_accuracy = calculate_average_accuracy(serialized)
    current_streak, best_streak = calculate_streak(serialized)
    # sessions this week: created_at >= this Monday
    today = datetime.utcnow().date()
    monday = today - timedelta(days=today.weekday())
    sessions_this_week = sum(1 for s in serialized if s.get("created_at") and datetime.fromisoformat(s["created_at"]).date() >= monday)
    return AnalyticsSummary(
        total_sessions=total_sessions,
        total_reps=total_reps,
        avg_accuracy=avg_accuracy,
        current_streak_days=current_streak,
        best_streak_days=best_streak,
        sessions_this_week=sessions_this_week,
    )


@router.get("/weekly")
def get_weekly(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[dict]:
    sessions = db.query(ExerciseSession).filter(ExerciseSession.user_id == current_user.id).all()
    serialized = _serialize_sessions(sessions)
    return calculate_weekly_breakdown(serialized)


@router.get("/by-exercise")
def by_exercise(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[dict]:
    sessions = db.query(ExerciseSession).filter(ExerciseSession.user_id == current_user.id).all()
    serialized = _serialize_sessions(sessions)
    return calculate_by_exercise(serialized)


@router.get("/accuracy-trend")
def accuracy_trend(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[dict]:
    sessions = db.query(ExerciseSession).filter(ExerciseSession.user_id == current_user.id).order_by(ExerciseSession.created_at.asc()).all()
    serialized = _serialize_sessions(sessions)
    return calculate_accuracy_trend(serialized)
