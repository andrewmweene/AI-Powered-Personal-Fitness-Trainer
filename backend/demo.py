"""Helpers for creating a ready-to-demo user account in the local database."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from recommendation.plan_matcher import match_plan

from .auth import hash_password
from .database import SessionLocal
from .models import BodyMeasurement, ExerciseSession, User, UserProfile, WorkoutPlan

DEMO_USERNAME = "testuser"
DEMO_EMAIL = "test@example.com"
DEMO_PASSWORD = "FitTrainer123!"


def _this_monday() -> date:
    today = date.today()
    return today - timedelta(days=today.weekday())


def ensure_demo_user() -> dict[str, str | bool]:
    """Create or refresh a demo account for viva presentations.

    The account is intentionally ready to use immediately: it has onboarding data,
    a generated weekly plan, and a few sample workout sessions so the dashboard is
    populated without any manual setup.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == DEMO_USERNAME).first()
        if user is None:
            user = User(
                username=DEMO_USERNAME,
                email=DEMO_EMAIL,
                hashed_password=hash_password(DEMO_PASSWORD),
                age=30,
                fitness_level="beginner",
                goal="weight_loss",
                onboarding_complete=True,
            )
            db.add(user)
            db.flush()

        user.email = DEMO_EMAIL
        user.hashed_password = hash_password(DEMO_PASSWORD)
        user.age = 30
        user.fitness_level = "beginner"
        user.goal = "weight_loss"
        user.onboarding_complete = True

        profile = user.profile
        if profile is None:
            profile = UserProfile(
                user_id=user.id,
                age=30,
                gender="female",
                height_cm=168.0,
                weight_kg=68.0,
                bmi=24.1,
                fitness_level="beginner",
                goal="weight_loss",
                has_equipment=False,
                equipment_list=[],
                days_per_week=3,
                workout_duration_minutes=30,
                preferred_time="Morning (8-11am)",
                onboarding_complete=True,
            )
            db.add(profile)
            db.flush()
        else:
            profile.age = 30
            profile.gender = "female"
            profile.height_cm = 168.0
            profile.weight_kg = 68.0
            profile.bmi = 24.1
            profile.fitness_level = "beginner"
            profile.goal = "weight_loss"
            profile.has_equipment = False
            profile.equipment_list = []
            profile.days_per_week = 3
            profile.workout_duration_minutes = 30
            profile.preferred_time = "Morning (8-11am)"
            profile.onboarding_complete = True

        if db.query(BodyMeasurement).filter(BodyMeasurement.user_id == user.id).count() == 0:
            measurement_dates = [
                (68.0, 24.1, 28),
                (67.4, 23.9, 21),
                (66.8, 23.7, 14),
                (66.2, 23.5, 7),
                (65.8, 23.3, 0),
            ]
            for weight, bmi, offset in measurement_dates:
                db.add(
                    BodyMeasurement(
                        user_id=user.id,
                        height_cm=168.0,
                        weight_kg=weight,
                        bmi=bmi,
                        measured_at=datetime.utcnow() - timedelta(days=offset),
                    )
                )

        if db.query(ExerciseSession).filter(ExerciseSession.user_id == user.id).count() == 0:
            today = datetime.utcnow().replace(hour=18, minute=0, second=0, microsecond=0)
            sample_sessions = [
                ("Squat", 18, 15, 82.0, 0),
                ("Push-up", 12, 10, 76.0, 1),
                ("Bicep Curl", 16, 14, 88.0, 2),
            ]
            for exercise_type, total_reps, correct_reps, accuracy, offset in sample_sessions:
                session = ExerciseSession(
                    user_id=user.id,
                    exercise_type=exercise_type,
                    total_reps=total_reps,
                    correct_reps=correct_reps,
                    incorrect_reps=max(0, total_reps - correct_reps),
                    posture_accuracy=accuracy,
                    duration_seconds=300 + offset * 15,
                    created_at=today - timedelta(days=offset),
                )
                db.add(session)

        week_start = _this_monday()
        existing_plan = (
            db.query(WorkoutPlan)
            .filter(WorkoutPlan.user_id == user.id)
            .filter(WorkoutPlan.week_start_date == week_start)
            .first()
        )
        if existing_plan is None:
            plan_data = match_plan(
                {
                    "fitness_level": "beginner",
                    "goal": "weight_loss",
                    "has_equipment": False,
                    "days_per_week": 3,
                    "workout_duration_minutes": 30,
                }
            )
            db.add(
                WorkoutPlan(
                    user_id=user.id,
                    plan_data=plan_data,
                    generated_at=datetime.utcnow(),
                    week_start_date=week_start,
                )
            )

        db.commit()
        return {"username": DEMO_USERNAME, "password": DEMO_PASSWORD, "onboarding_complete": True}
    finally:
        db.close()
