"""Pose analysis endpoint.

Accepts a JPEG frame and returns angle, state, rep counts and feedback.
"""
from __future__ import annotations

import math

from fastapi import APIRouter, UploadFile, Form, Depends
from pydantic import BaseModel
import numpy as np
import cv2

from ..dependencies import get_current_user
from pose_engine.detector import PoseDetector
from pose_engine.angle_utils import get_landmark_coords, calculate_angle
from pose_engine.state_machine import ExerciseStateMachine
from pose_engine.exercises.squat import Squat
from pose_engine.exercises.bicep_curl import BicepCurl
from pose_engine.exercises.pushup import PushUp
from pose_engine.exercises.dumbbell_fly import DumbbellFly
from pose_engine.exercises.kickback import Kickback

router = APIRouter()


class PoseLandmarkData(BaseModel):
    """Normalized pose point returned for browser-side skeleton rendering."""

    x: float
    y: float
    z: float | None = None
    visibility: float | None = None


class PoseAnalysisResponse(BaseModel):
    """Pose metrics and landmarks returned for one analyzed frame."""

    angle: float
    state: str
    rep_completed: bool
    feedback: str
    rep_count: int
    correct_reps: int
    incorrect_reps: int
    accuracy: int
    landmarks: list[PoseLandmarkData | None]
    pose_detected: bool

# Shared detector instance
_detector = PoseDetector()

_EXERCISE_MAP = {
    "Squat": Squat(),
    "Bicep Curl": BicepCurl(),
    "Push-up": PushUp(),
    "Dumbbell Fly": DumbbellFly(),
    "Dumbbell Kickback": Kickback(),
}

# In-memory per-session state machines
_session_machines: dict[str, ExerciseStateMachine] = {}


def _session_response(
    session_id: str,
    *,
    angle: float = 0.0,
    state: str = ExerciseStateMachine.STATE_REST,
    feedback: str = "",
    rep_completed: bool = False,
    landmarks: list[dict[str, float | None] | None] | None = None,
) -> dict[str, object]:
    """Build a consistent pose response, including persisted session totals.

    Args:
        session_id: Identifier for the active pose session.
        angle: Current joint angle in degrees.
        state: Current exercise state.
        feedback: User-facing form guidance.
        rep_completed: Whether this frame completed a correct rep.
        landmarks: Serialized pose landmarks, when available.

    Returns:
        API payload containing pose data and session rep counts.
    """
    machine = _session_machines.get(session_id)
    correct = machine.correct_count if machine else 0
    incorrect = machine.incorrect_count if machine else 0
    total = correct + incorrect
    landmark_data = landmarks or []
    state_codes = {
        ExerciseStateMachine.STATE_REST: "s1",
        ExerciseStateMachine.STATE_TRANSITION: "s2",
        ExerciseStateMachine.STATE_COMPLETE: "s3",
    }
    return {
        "angle": angle,
        "state": state_codes.get(state, state),
        "rep_completed": rep_completed,
        "feedback": feedback,
        "rep_count": total,
        "correct_reps": correct,
        "incorrect_reps": incorrect,
        "accuracy": int(correct / total * 100) if total else 0,
        "landmarks": landmark_data,
        "pose_detected": len(landmark_data) > 0,
    }


def _serialize_landmarks(landmarks) -> list[dict[str, float | None] | None]:
    """Return normalized coordinates without inventing missing joint data."""
    serialized = []
    for landmark in landmarks:
        x = getattr(landmark, "x", None)
        y = getattr(landmark, "y", None)
        visibility = getattr(landmark, "visibility", None)
        if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in (x, y)):
            serialized.append(None)
            continue

        serialized.append({
            "x": round(float(x), 4),
            "y": round(float(y), 4),
            "z": round(float(landmark.z), 4) if isinstance(getattr(landmark, "z", None), (int, float)) and math.isfinite(landmark.z) else None,
            "visibility": round(float(visibility), 3) if isinstance(visibility, (int, float)) and math.isfinite(visibility) else None,
        })
    return serialized


@router.post("/analyse-frame", response_model=PoseAnalysisResponse)
async def analyse_frame(
    file: UploadFile,
    exercise: str = Form(..., min_length=1, max_length=40),
    session_id: str = Form(..., min_length=1, max_length=100),
    current_user=Depends(get_current_user),
):
    """Analyse a single video frame for the given exercise and session.

    Returns a small JSON payload consumed by the frontend hook.
    """
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        return _session_response(session_id, feedback="Invalid image")

    # Convert to RGB for detector
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = _detector.detect(frame_rgb)

    # Handle no-detection / fallback
    if not hasattr(results, "pose_landmarks") or not results.pose_landmarks:
        machine = _session_machines.get(session_id)
        state = machine.current_state if machine else ExerciseStateMachine.STATE_REST
        return _session_response(session_id, state=state, feedback="No person detected")

    landmarks = results.pose_landmarks[0]
    serialized_landmarks = _serialize_landmarks(landmarks)

    exercise_obj = _EXERCISE_MAP.get(exercise)
    if exercise_obj is None:
        return _session_response(
            session_id,
            feedback="Unknown exercise",
            landmarks=serialized_landmarks,
        )

    valid_pose, pose_feedback = exercise_obj.is_valid_pose(landmarks, frame.shape)
    if not valid_pose:
        machine = _session_machines.get(session_id)
        state = machine.current_state if machine else ExerciseStateMachine.STATE_REST
        return _session_response(
            session_id,
            state=state,
            feedback=pose_feedback,
            landmarks=serialized_landmarks,
        )

    angle_landmarks = exercise_obj.get_angle_landmarks()
    missing = [idx for idx in angle_landmarks if idx not in range(len(landmarks))]

    if missing:
        return _session_response(
            session_id,
            feedback="Insufficient landmarks",
            landmarks=serialized_landmarks,
        )

    try:
        coords = [get_landmark_coords(landmarks, idx, frame.shape) for idx in angle_landmarks]
    except (IndexError, TypeError, AttributeError):
        return _session_response(
            session_id,
            feedback="Insufficient landmarks",
            landmarks=serialized_landmarks,
        )

    a, b, c = coords[0], coords[1], coords[2]
    angle = float(calculate_angle(a, b, c))

    thresholds = exercise_obj.get_angle_thresholds()

    # get or create state machine
    machine = _session_machines.get(session_id)
    if machine is None:
        machine = ExerciseStateMachine()
        _session_machines[session_id] = machine

    state, rep_completed = machine.update(angle, thresholds)

    feedback = exercise_obj.get_feedback(angle, state)

    return _session_response(
        session_id,
        angle=angle,
        state=state,
        feedback=feedback,
        rep_completed=rep_completed,
        landmarks=serialized_landmarks,
    )


@router.delete("/session/{session_id}")
async def clear_session(
    session_id: str,
    current_user=Depends(get_current_user),
) -> dict[str, str | bool]:
    """Remove a completed session's in-memory state machine.

    Args:
        session_id: Identifier for the pose session to remove.
        current_user: Authenticated user from the request dependency.

    Returns:
        Whether a state machine was removed and the session identifier.
    """
    removed = _session_machines.pop(session_id, None)
    return {"cleared": removed is not None, "session_id": session_id}


@router.get("/session/{session_id}/status")
async def get_session_status(
    session_id: str,
    current_user=Depends(get_current_user),
) -> dict[str, object]:
    """Return the current counts and state without processing a frame.

    Args:
        session_id: Identifier for the pose session to inspect.
        current_user: Authenticated user from the request dependency.

    Returns:
        Current session status and rep totals.
    """
    machine = _session_machines.get(session_id)
    if machine is None:
        return {
            "session_id": session_id,
            "active": False,
            "rep_count": 0,
            "correct_reps": 0,
            "incorrect_reps": 0,
        }
    return {
        "session_id": session_id,
        "active": True,
        "rep_count": machine.correct_count + machine.incorrect_count,
        "correct_reps": machine.correct_count,
        "incorrect_reps": machine.incorrect_count,
        "state": machine.current_state,
    }
