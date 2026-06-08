"""Workout plan endpoints backed by recommendation logic."""

from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..dependencies import get_current_user, get_db
from recommendation import engine as recommendation_engine
from ..schemas import WorkoutPlanResponse
from ..models import WorkoutPlan, ExerciseSession
from analytics.metrics import build_user_metrics_dict

router = APIRouter()


def _this_monday() -> date:
    today = date.today()
    return today - timedelta(days=today.weekday())


@router.get("/plan", response_model=WorkoutPlanResponse)
def get_or_create_plan(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> WorkoutPlan:
    """Return cached plan for this week or generate a new one."""
    week_start = _this_monday()
    existing = (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == current_user.id)
        .filter(WorkoutPlan.week_start_date == week_start)
        .first()
    )
    if existing:
        return existing

    # build metrics from recent sessions
    sessions = (
        db.query(ExerciseSession)
        .filter(ExerciseSession.user_id == current_user.id)
        .order_by(ExerciseSession.created_at.desc())
        .limit(7)
        .all()
    )
    sessions_serialized = [
        {
            "exercise_type": s.exercise_type,
            "total_reps": s.total_reps,
            "correct_reps": s.correct_reps,
            "posture_accuracy": s.posture_accuracy,
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]
    metrics = build_user_metrics_dict(sessions_serialized)
    user_profile = {
        "user_id": current_user.id,
        "fitness_level": current_user.fitness_level,
        "goal": current_user.goal,
        "week_start_date": week_start.isoformat(),
        **metrics,
    }
    plan_data = recommendation_engine.generate_plan(user_profile=user_profile, difficulty=None)

    workout_plan = WorkoutPlan(
        user_id=current_user.id,
        plan_data=plan_data,
        generated_at=plan_data.get("generated_at"),
        week_start_date=week_start,
    )
    db.add(workout_plan)
    db.commit()
    db.refresh(workout_plan)
    return workout_plan


@router.post("/plan/refresh", response_model=WorkoutPlanResponse)
def refresh_plan(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> WorkoutPlan:
    """Force-generate a new plan for the current week and save it."""
    week_start = _this_monday()
    # delete any existing plan for this week
    db.query(WorkoutPlan).filter(WorkoutPlan.user_id == current_user.id).filter(WorkoutPlan.week_start_date == week_start).delete()
    db.commit()
    # Delegate to GET logic to create and return new one
    return get_or_create_plan(db=db, current_user=current_user)
