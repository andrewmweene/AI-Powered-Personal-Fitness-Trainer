"""Body measurement history endpoints for progress reports."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..dependencies import get_current_user, get_db
from ..models import BodyMeasurement

router = APIRouter()


class MeasurementCreate(BaseModel):
    height_cm: float = Field(ge=50, le=300)
    weight_kg: float = Field(ge=20, le=300)
    measured_at: datetime | None = None


def _serialize(measurement: BodyMeasurement) -> dict[str, object]:
    return {
        "id": measurement.id,
        "height_cm": measurement.height_cm,
        "weight_kg": measurement.weight_kg,
        "bmi": measurement.bmi,
        "measured_at": measurement.measured_at.isoformat(),
    }


@router.get("/")
def list_measurements(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[dict[str, object]]:
    measurements = (
        db.query(BodyMeasurement)
        .filter(BodyMeasurement.user_id == current_user.id)
        .order_by(BodyMeasurement.measured_at.asc())
        .all()
    )
    return [_serialize(measurement) for measurement in measurements]


@router.post("/")
def create_measurement(
    payload: MeasurementCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict[str, object]:
    bmi = round(payload.weight_kg / ((payload.height_cm / 100) ** 2), 1)
    measurement = BodyMeasurement(
        user_id=current_user.id,
        height_cm=payload.height_cm,
        weight_kg=payload.weight_kg,
        bmi=bmi,
        measured_at=payload.measured_at or datetime.utcnow(),
    )
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    return _serialize(measurement)