"""Exercise session recording endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..dependencies import get_current_user, get_db
from ..models import ExerciseSession
from ..schemas import SessionCreate, SessionResponse

router = APIRouter()


@router.post("/", response_model=SessionResponse)
def record_session(
    session_in: SessionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ExerciseSession:
    """Record a completed exercise session for the authenticated user."""
    posture_accuracy = session_in.posture_accuracy
    if posture_accuracy is None and session_in.total_reps > 0:
        posture_accuracy = float(session_in.correct_reps) / session_in.total_reps * 100.0

    session = ExerciseSession(
        user_id=current_user.id,
        exercise_type=session_in.exercise_type,
        total_reps=session_in.total_reps,
        correct_reps=session_in.correct_reps,
        incorrect_reps=session_in.incorrect_reps,
        posture_accuracy=posture_accuracy,
        duration_seconds=session_in.duration_seconds,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/", response_model=list[SessionResponse])
def list_sessions(
    skip: int = 0,
    limit: int = 50,
    exercise_type: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[ExerciseSession]:
    """List sessions for the current user with optional filtering and pagination."""
    query = db.query(ExerciseSession).filter(ExerciseSession.user_id == current_user.id)
    if exercise_type:
        query = query.filter(ExerciseSession.exercise_type == exercise_type)
    sessions = query.order_by(ExerciseSession.created_at.desc()).offset(skip).limit(limit).all()
    return sessions


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> ExerciseSession:
    """Retrieve a single session by id for the current user."""
    session = (
        db.query(ExerciseSession)
        .filter(ExerciseSession.id == session_id)
        .filter(ExerciseSession.user_id == current_user.id)
        .first()
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.get("/recent/{n}", response_model=list[SessionResponse])
def recent_sessions(n: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[ExerciseSession]:
    """Return the last `n` sessions for the current user ordered by created_at desc."""
    n = max(1, min(n, 100))
    sessions = (
        db.query(ExerciseSession)
        .filter(ExerciseSession.user_id == current_user.id)
        .order_by(ExerciseSession.created_at.desc())
        .limit(n)
        .all()
    )
    return sessions
