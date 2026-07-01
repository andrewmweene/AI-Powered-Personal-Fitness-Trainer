"""Pydantic schemas for user onboarding profile creation and responses."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class BodyProfileCreate(BaseModel):
    age: int = Field(ge=13, le=100)
    gender: Optional[str] = None
    height_cm: float = Field(ge=50, le=300)
    weight_kg: float = Field(ge=20, le=300)
    fitness_level: Literal["beginner", "intermediate", "advanced"]


class GoalCreate(BaseModel):
    goal: Literal[
        "weight_loss",
        "muscle_gain",
        "strength_training",
        "endurance",
        "general_fitness",
        "flexibility",
        "sports_specific",
    ]


class EquipmentCreate(BaseModel):
    has_equipment: bool
    equipment_list: list[str] = []


class AvailabilityCreate(BaseModel):
    days_per_week: int = Field(ge=1, le=7)
    workout_duration_minutes: Literal[15, 20, 30, 45, 60, 75, 90]
    preferred_time: str


class OnboardingComplete(BaseModel):
    age: int = Field(ge=13, le=100)
    gender: Optional[str] = None
    height_cm: float = Field(ge=50, le=300)
    weight_kg: float = Field(ge=20, le=300)
    fitness_level: Literal["beginner", "intermediate", "advanced"]
    goal: Literal[
        "weight_loss",
        "muscle_gain",
        "strength_training",
        "endurance",
        "general_fitness",
        "flexibility",
        "sports_specific",
    ]
    has_equipment: bool
    equipment_list: list[str] = []
    days_per_week: int = Field(ge=1, le=7)
    workout_duration_minutes: Literal[15, 20, 30, 45, 60, 75, 90]
    preferred_time: str


class UserProfileResponse(BaseModel):
    id: str
    user_id: str
    age: int
    gender: Optional[str] = None
    height_cm: float
    weight_kg: float
    bmi: float
    fitness_level: str
    goal: str
    has_equipment: bool
    equipment_list: list[str] | None = None
    days_per_week: int
    workout_duration_minutes: int
    preferred_time: str
    onboarding_complete: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
