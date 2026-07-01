"""Onboarding router for user profile collection and static plan assignment."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..dependencies import get_current_user, get_db
from ..models import UserProfile, WorkoutPlan
from ..schemas import WorkoutPlanResponse
from ..schemas_onboarding import OnboardingComplete, UserProfileResponse
from recommendation.plan_matcher import match_plan

router = APIRouter()


def _this_monday() -> date:
    today = date.today()
    return today - timedelta(days=today.weekday())


@router.post("/complete")
def complete_onboarding(
    payload: OnboardingComplete,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict[str, object]:
    """Create or update the user's onboarding profile and assign a weekly plan."""
    bmi = round(payload.weight_kg / ((payload.height_cm / 100) ** 2), 1)
    profile = current_user.profile
    if profile is None:
        profile = UserProfile(user_id=current_user.id)

    profile.age = payload.age
    profile.gender = payload.gender
    profile.height_cm = payload.height_cm
    profile.weight_kg = payload.weight_kg
    profile.bmi = bmi
    profile.fitness_level = payload.fitness_level
    profile.goal = payload.goal
    profile.has_equipment = payload.has_equipment
    profile.equipment_list = payload.equipment_list or []
    profile.days_per_week = payload.days_per_week
    profile.workout_duration_minutes = payload.workout_duration_minutes
    profile.preferred_time = payload.preferred_time
    profile.onboarding_complete = True
    current_user.onboarding_complete = True

    db.add(profile)
    db.add(current_user)
    db.commit()
    db.refresh(profile)

    plan_input = {
        "fitness_level": payload.fitness_level,
        "goal": payload.goal,
        "has_equipment": payload.has_equipment,
        "days_per_week": payload.days_per_week,
        "workout_duration_minutes": payload.workout_duration_minutes,
    }
    plan_data = match_plan(plan_input)

    week_start = _this_monday()
    db.query(WorkoutPlan).filter(WorkoutPlan.user_id == current_user.id).filter(WorkoutPlan.week_start_date == week_start).delete()
    db.commit()

    workout_plan = WorkoutPlan(
        user_id=current_user.id,
        plan_data=plan_data,
        generated_at=datetime.utcnow(),
        week_start_date=week_start,
    )
    db.add(workout_plan)
    db.commit()
    db.refresh(workout_plan)

    profile_response = UserProfileResponse.model_validate(profile).model_dump()
    plan_response = WorkoutPlanResponse.model_validate(workout_plan).model_dump()
    return {"profile": profile_response, "plan": plan_response}


@router.get("/status")
def onboarding_status(current_user=Depends(get_current_user)) -> dict[str, bool]:
    """Return whether the current user has completed onboarding."""
    return {"onboarding_complete": bool(current_user.onboarding_complete)}


@router.get("/profile", response_model=UserProfileResponse)
def onboarding_profile(current_user=Depends(get_current_user)) -> UserProfileResponse:
    """Return the current user's onboarding profile."""
    profile = current_user.profile
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found.")
    return profile
