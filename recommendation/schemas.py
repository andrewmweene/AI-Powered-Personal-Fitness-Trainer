"""Pydantic models for workout plan and exercise recommendation data."""

from __future__ import annotations

from pydantic import BaseModel


class ExerciseEntry(BaseModel):
    exercise: str
    sets: int
    reps: int
    notes: str = ""


class DayPlan(BaseModel):
    is_rest: bool = False
    exercises: list[ExerciseEntry] = []


class WeeklyPlan(BaseModel):
    monday: DayPlan
    tuesday: DayPlan
    wednesday: DayPlan
    thursday: DayPlan
    friday: DayPlan
    saturday: DayPlan
    sunday: DayPlan
    difficulty: str
    generated_by: str
    notes: str = ""
