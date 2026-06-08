"""Pydantic schemas for API request and response validation."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    age: int | None = None
    fitness_level: str | None = None
    goal: str | None = None


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
    username: str
    password: str


class SessionCreate(BaseModel):
    exercise_type: str
    total_reps: int
    correct_reps: int
    incorrect_reps: int
    posture_accuracy: float | None = None
    duration_seconds: int | None = None


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
