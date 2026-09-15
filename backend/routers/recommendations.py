"""Authenticated endpoints for weekly recommendation plans."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from analytics.metrics import build_user_metrics_dict
from recommendation.engine import MIN_SESSIONS_FOR_AI, generate_plan
from recommendation.plan_library import get_fallback_plan
from ..database import get_db
from ..dependencies import get_current_user
from ..models import ExerciseSession, WorkoutPlan

router = APIRouter()


def _this_monday() -> date:
    """Return the Monday starting the current week."""
    today = date.today()
    return today - timedelta(days=today.weekday())


def _session_dict(session: ExerciseSession) -> dict:
    """Serialize an exercise session for pure analytics functions."""
    return {
        "exercise_type": session.exercise_type,
        "total_reps": session.total_reps,
        "correct_reps": session.correct_reps,
        "incorrect_reps": session.incorrect_reps,
        "posture_accuracy": session.posture_accuracy,
        "duration_seconds": session.duration_seconds,
        "created_at": session.created_at.isoformat() if session.created_at else None,
    }


def _build_plan_for_user(user, db: Session) -> dict:
    """Build a plan from onboarding data and recent session performance."""
    session_count = db.query(ExerciseSession).filter(ExerciseSession.user_id == user.id).count()
    profile = user.profile
    if profile is None:
        plan = get_fallback_plan("beginner")
        plan.update({"phase": 1, "sessions_until_ai": MIN_SESSIONS_FOR_AI})
        return plan

    recent = (
        db.query(ExerciseSession)
        .filter(ExerciseSession.user_id == user.id)
        .order_by(ExerciseSession.created_at.desc())
        .limit(14)
        .all()
    )
    sessions = [_session_dict(session) for session in recent]
    user_profile = {
        "username": user.username,
        "age": profile.age,
        "fitness_level": profile.fitness_level,
        "goal": profile.goal,
        "has_equipment": profile.has_equipment,
        "days_per_week": profile.days_per_week,
        "workout_duration_minutes": profile.workout_duration_minutes,
    }
    return generate_plan(user_profile, build_user_metrics_dict(sessions), session_count)


def _save_plan(plan: dict, user, db: Session) -> WorkoutPlan:
    """Persist a plan for the current week and return its ORM object."""
    workout_plan = WorkoutPlan(
        user_id=user.id,
        plan_data=plan,
        generated_at=datetime.utcnow(),
        week_start_date=_this_monday(),
    )
    db.add(workout_plan)
    db.commit()
    db.refresh(workout_plan)
    return workout_plan


@router.get("/plan")
def get_or_create_plan(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict:
    """Return this week's cached plan or generate and cache one."""
    week_start = _this_monday()
    existing = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id,
        WorkoutPlan.week_start_date == week_start,
    ).first()
    if existing:
        return existing.plan_data
    return _save_plan(_build_plan_for_user(current_user, db), current_user, db).plan_data


@router.post("/plan/refresh")
def refresh_plan(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict:
    """Delete and regenerate this week's cached plan."""
    db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id,
        WorkoutPlan.week_start_date == _this_monday(),
    ).delete(synchronize_session=False)
    db.commit()
    return _save_plan(_build_plan_for_user(current_user, db), current_user, db).plan_data


@router.get("/status")
def get_recommendation_status(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict[str, int | bool]:
    """Return the user's current recommendation phase and AI progress."""
    session_count = db.query(ExerciseSession).filter(ExerciseSession.user_id == current_user.id).count()
    return {
        "session_count": session_count,
        "min_for_ai": MIN_SESSIONS_FOR_AI,
        "phase": 2 if session_count >= MIN_SESSIONS_FOR_AI else 1,
        "sessions_until_ai": max(0, MIN_SESSIONS_FOR_AI - session_count),
        "ai_active": session_count >= MIN_SESSIONS_FOR_AI,
    }
