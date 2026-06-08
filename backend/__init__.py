"""Backend package for the AI Personal Trainer application."""

from .database import engine, SessionLocal
from .auth import hash_password, verify_password, create_access_token, decode_access_token
from .models import User, ExerciseSession, WorkoutPlan, PostureFeedbackLog
from .schemas import (
    UserCreate,
    UserResponse as UserRead,
    Token,
    SessionCreate as ExerciseSessionCreate,
    SessionResponse as ExerciseSessionRead,
    WorkoutPlanResponse as WorkoutPlanRead,
)

__all__ = [
    "engine",
    "SessionLocal",
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "User",
    "ExerciseSession",
    "WorkoutPlan",
    "PostureFeedbackLog",
]
