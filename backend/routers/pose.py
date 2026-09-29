"""Pose analysis endpoint.

Accepts a JPEG frame and returns angle, state, rep counts and feedback.
"""
from __future__ import annotations

import math

from fastapi import APIRouter, UploadFile, Form, Depends
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

# Shared detector instance
detector = PoseDetector()

EXERCISES = {
    "Squat": Squat(),
    "Bicep Curl": BicepCurl(),
    "Push-up": PushUp(),
    "Dumbbell Fly": DumbbellFly(),
    "Dumbbell Kickback": Kickback(),
}

# In-memory per-session state machines
_session_machines: dict[str, ExerciseStateMachine] = {}


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
            "x": float(x),
            "y": float(y),
            "z": float(landmark.z) if isinstance(getattr(landmark, "z", None), (int, float)) else None,
            "visibility": float(visibility) if isinstance(visibility, (int, float)) and math.isfinite(visibility) else None,
        })
    return serialized


@router.post("/analyse-frame")
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
        return {
            "angle": 0,
            "state": "REST",
            "feedback": "Invalid image",
            "rep_count": 0,
            "correct_reps": 0,
            "incorrect_reps": 0,
            "accuracy": 0,
            "landmarks": [],
        }

    # Convert to RGB for detector
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = detector.detect(frame_rgb)

    # Handle no-detection / fallback
    if not hasattr(results, "pose_landmarks") or not results.pose_landmarks:
        return {
            "angle": 0,
            "state": "REST",
            "feedback": "No person detected",
            "rep_count": 0,
            "correct_reps": 0,
            "incorrect_reps": 0,
            "accuracy": 0,
            "landmarks": [],
        }

    landmarks = results.pose_landmarks[0]
    serialized_landmarks = _serialize_landmarks(landmarks)

    exercise_obj = EXERCISES.get(exercise)
    if exercise_obj is None:
        return {
            "angle": 0,
            "state": "REST",
            "feedback": "Unknown exercise",
            "rep_count": 0,
            "correct_reps": 0,
            "incorrect_reps": 0,
            "accuracy": 0,
            "landmarks": serialized_landmarks,
        }

    valid_pose, pose_feedback = exercise_obj.is_valid_pose(landmarks, frame.shape)
    if not valid_pose:
        return {
            "angle": 0,
            "state": "REST",
            "feedback": pose_feedback,
            "rep_count": 0,
            "correct_reps": 0,
            "incorrect_reps": 0,
            "accuracy": 0,
            "landmarks": serialized_landmarks,
        }

    angle_landmarks = exercise_obj.get_angle_landmarks()
    missing = [idx for idx in angle_landmarks if idx not in range(len(landmarks))]

    if missing:
        return {
            "angle": 0,
            "state": "REST",
            "feedback": "Insufficient landmarks",
            "rep_count": 0,
            "correct_reps": 0,
            "incorrect_reps": 0,
            "accuracy": 0,
            "landmarks": serialized_landmarks,
        }

    try:
        coords = [get_landmark_coords(landmarks, idx, frame.shape) for idx in angle_landmarks]
    except Exception:
        return {
            "angle": 0,
            "state": "REST",
            "feedback": "Insufficient landmarks",
            "rep_count": 0,
            "correct_reps": 0,
            "incorrect_reps": 0,
            "accuracy": 0,
        }

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

    correct = machine.correct_count
    incorrect = machine.incorrect_count
    total = correct + incorrect
    accuracy = int((correct / total) * 100) if total > 0 else 0

    return {
        "angle": angle,
        "state": state,
        "feedback": feedback,
        "rep_count": correct + incorrect,
        "correct_reps": correct,
        "incorrect_reps": incorrect,
        "accuracy": accuracy,
        "landmarks": serialized_landmarks,
    }
