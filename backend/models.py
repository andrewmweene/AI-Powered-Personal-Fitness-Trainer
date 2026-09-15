"""SQLAlchemy ORM models for users, sessions, workout plans, and feedback logs."""

from __future__ import annotations

import uuid
from datetime import datetime, date

from sqlalchemy import JSON, Boolean, Column, Date, DateTime, Float, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

from .database import Base


def _uuid_str() -> str:
    return str(uuid.uuid4())


class User(Base):
    """Represents a registered user in the AI Personal Trainer system."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    age = Column(Integer, nullable=True)
    fitness_level = Column(String(20), nullable=False, default="beginner")
    goal = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    sessions = relationship("ExerciseSession", back_populates="user", cascade="all, delete-orphan")
    body_measurements = relationship("BodyMeasurement", back_populates="user", cascade="all, delete-orphan")
    workout_plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    onboarding_complete = Column(Boolean, default=False, nullable=False)


class UserProfile(Base):
    """Stores onboarding profile details collected during user setup."""

    __tablename__ = "user_profiles"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=True)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)
    fitness_level = Column(String(20), nullable=False)
    goal = Column(String(50), nullable=False)
    has_equipment = Column(Boolean, nullable=False, default=False)
    equipment_list = Column(JSON, nullable=True, default=list)
    days_per_week = Column(Integer, nullable=False)
    workout_duration_minutes = Column(Integer, nullable=False)
    preferred_time = Column(String(50), nullable=False)
    onboarding_complete = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="profile")


class BodyMeasurement(Base):
    """Stores dated body measurements used for progress reporting."""

    __tablename__ = "body_measurements"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)
    measured_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="body_measurements")


class ExerciseSession(Base):
    """Stores exercise session summaries for user workouts."""

    __tablename__ = "exercise_sessions"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    exercise_type = Column(String(50), nullable=False)
    total_reps = Column(Integer, nullable=False, default=0)
    correct_reps = Column(Integer, nullable=False, default=0)
    incorrect_reps = Column(Integer, nullable=False, default=0)
    posture_accuracy = Column(Float, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="sessions")
    feedback_logs = relationship("PostureFeedbackLog", back_populates="session", cascade="all, delete-orphan")


class WorkoutPlan(Base):
    """Represents a generated workout plan for a user."""

    __tablename__ = "workout_plans"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    plan_data = Column(JSON, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    week_start_date = Column(Date, nullable=False)

    user = relationship("User", back_populates="workout_plans")


class PostureFeedbackLog(Base):
    """Tracks feedback messages produced during an exercise session."""

    __tablename__ = "posture_feedback_logs"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    session_id = Column(String(36), ForeignKey("exercise_sessions.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    feedback_message = Column(String(200), nullable=True)
    joint_angle = Column(Float, nullable=True)

    session = relationship("ExerciseSession", back_populates="feedback_logs")
