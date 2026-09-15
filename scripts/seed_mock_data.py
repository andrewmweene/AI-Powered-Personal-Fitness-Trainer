"""Create repeatable local accounts and data for exercising the application."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
from pathlib import Path
import sys

from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.auth import hash_password
from backend.database import Base, SessionLocal, engine
from backend.models import ExerciseSession, PostureFeedbackLog, User, UserProfile, WorkoutPlan
from recommendation.plan_matcher import match_plan


PASSWORD = "FitTrainer123!"

MOCK_USERS = (
    {
        "username": "maya_beginner", "email": "maya.beginner@example.com", "age": 28,
        "gender": "female", "height_cm": 165.0, "weight_kg": 72.0,
        "fitness_level": "beginner", "goal": "weight_loss", "has_equipment": False,
        "equipment_list": [], "days_per_week": 3, "workout_duration_minutes": 30,
        "preferred_time": "morning", "accuracy": (72.0, 78.0, 84.0),
    },
    {
        "username": "leo_intermediate", "email": "leo.intermediate@example.com", "age": 34,
        "gender": "male", "height_cm": 180.0, "weight_kg": 82.0,
        "fitness_level": "intermediate", "goal": "muscle_gain", "has_equipment": True,
        "equipment_list": ["dumbbells", "resistance_bands"], "days_per_week": 4,
        "workout_duration_minutes": 45, "preferred_time": "evening",
        "accuracy": (86.0, 88.0, 91.0, 89.0, 93.0, 92.0, 95.0),
    },
    {
        "username": "aria_advanced", "email": "aria.advanced@example.com", "age": 41,
        "gender": "non-binary", "height_cm": 172.0, "weight_kg": 68.0,
        "fitness_level": "advanced", "goal": "strength_training", "has_equipment": True,
        "equipment_list": ["dumbbells", "barbell", "bench"], "days_per_week": 5,
        "workout_duration_minutes": 60, "preferred_time": "afternoon",
        "accuracy": (91.0, 92.0, 94.0, 93.0, 95.0, 96.0, 94.0, 97.0, 96.0, 98.0, 97.0, 99.0),
    },
)


def _profile_data(spec: dict) -> dict:
    bmi = spec["weight_kg"] / (spec["height_cm"] / 100) ** 2
    return {
        "age": spec["age"], "gender": spec["gender"], "height_cm": spec["height_cm"],
        "weight_kg": spec["weight_kg"], "bmi": round(bmi, 2),
        "fitness_level": spec["fitness_level"], "goal": spec["goal"],
        "has_equipment": spec["has_equipment"], "equipment_list": spec["equipment_list"],
        "days_per_week": spec["days_per_week"],
        "workout_duration_minutes": spec["workout_duration_minutes"],
        "preferred_time": spec["preferred_time"], "onboarding_complete": True,
    }


def _create_user(db: Session, spec: dict) -> tuple[User, bool]:
    user = db.query(User).filter(User.username == spec["username"]).first()
    if user is not None:
        return user, False
    user = User(
        username=spec["username"], email=spec["email"], hashed_password=hash_password(PASSWORD),
        age=spec["age"], fitness_level=spec["fitness_level"], goal=spec["goal"],
        onboarding_complete=True,
    )
    user.profile = UserProfile(**_profile_data(spec))
    db.add(user)
    db.flush()
    return user, True


def _create_sessions(db: Session, user: User, spec: dict) -> int:
    if db.query(ExerciseSession).filter(ExerciseSession.user_id == user.id).count() > 0:
        return 0
    created = 0
    today = datetime.utcnow().replace(hour=18, minute=0, second=0, microsecond=0)
    for index, accuracy in enumerate(spec["accuracy"]):
        total_reps = 20 + index * 2
        correct_reps = round(total_reps * accuracy / 100)
        session = ExerciseSession(
            user_id=user.id, exercise_type=("Squat", "Push-up", "Bicep Curl")[index % 3],
            total_reps=total_reps, correct_reps=correct_reps,
            incorrect_reps=total_reps - correct_reps, posture_accuracy=accuracy,
            duration_seconds=420 + index * 30, created_at=today - timedelta(days=index),
        )
        session.feedback_logs.append(PostureFeedbackLog(
            feedback_message="Keep your core engaged and move with control.",
            joint_angle=90.0 + index, timestamp=session.created_at,
        ))
        db.add(session)
        created += 1
    db.flush()
    return created


def _create_plan(db: Session, user: User, spec: dict) -> bool:
    week_start = date.today() - timedelta(days=date.today().weekday())
    exists = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == user.id, WorkoutPlan.week_start_date == week_start,
    ).first()
    if exists is not None:
        return False
    profile = {key: spec[key] for key in (
        "fitness_level", "goal", "has_equipment", "days_per_week", "workout_duration_minutes",
    )}
    db.add(WorkoutPlan(
        user_id=user.id, plan_data=match_plan(profile), generated_at=datetime.utcnow(),
        week_start_date=week_start,
    ))
    return True


def seed(reset: bool = False) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for spec in MOCK_USERS:
            user = db.query(User).filter(User.username == spec["username"]).first()
            if reset and user is not None:
                db.delete(user)
                db.flush()
                user = None
            user, created = _create_user(db, spec)
            sessions_created = _create_sessions(db, user, spec) if created else 0
            plan_created = _create_plan(db, user, spec) if created else False
            db.commit()
            action = "created" if created else "already exists"
            print(f"{spec['username']}: {action}; sessions={sessions_created}; plan={'created' if plan_created else 'kept'}")
        print(f"\nPassword for all mock accounts: {PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="Delete these mock users and recreate their data.")
    seed(reset=parser.parse_args().reset)