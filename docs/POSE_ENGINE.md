# Pose Engine

This document describes the pose engine design for real-time posture analysis, exercise state tracking, and feedback generation.

- `pose_engine/detector.py`: wraps MediaPipe Pose detection and landmark rendering.
- `pose_engine/angle_utils.py`: computes joint angles and camera orientation.
- `pose_engine/state_machine.py`: tracks exercise phases and counts reps.
- `pose_engine/feedback.py`: generates corrective feedback messages.
- `pose_engine/camera.py`: manages webcam capture.
- `pose_engine/exercises/`: contains exercise-specific logic and thresholds.
