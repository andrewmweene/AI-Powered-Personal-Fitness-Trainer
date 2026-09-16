"""Pydantic schemas for API request and response validation."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    age: int | None = Field(default=None, ge=13, le=100)
    fitness_level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    goal: Literal["weight_loss", "muscle_gain", "strength_training", "endurance", "general_fitness", "flexibility", "sports_specific"] | None = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    age: int | None = None
    fitness_level: str | None = None
    goal: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class SessionCreate(BaseModel):
    exercise_type: Literal["Squat", "Bicep Curl", "Push-up", "Dumbbell Fly", "Dumbbell Kickback"]
    total_reps: int = Field(ge=0, le=1000)
    correct_reps: int = Field(ge=0, le=1000)
    incorrect_reps: int = Field(ge=0, le=1000)
    posture_accuracy: float | None = Field(default=None, ge=0, le=100)
    duration_seconds: int | None = Field(default=None, ge=0, le=86400)


class SessionResponse(SessionCreate):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkoutPlanResponse(BaseModel):
    id: str
    plan_data: dict[str, Any]
    generated_at: datetime
    week_start_date: date

    model_config = {"from_attributes": True}


class AnalyticsSummary(BaseModel):
    total_sessions: int
    total_reps: int
    avg_accuracy: float
    current_streak_days: int
    best_streak_days: int
    sessions_this_week: int

    model_config = {"from_attributes": True}
