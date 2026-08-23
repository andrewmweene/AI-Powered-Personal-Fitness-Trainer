"""Tests for the exercise state machine."""

from pose_engine.exercises.bicep_curl import BicepCurl
from pose_engine.exercises.squat import Squat
from pose_engine.state_machine import ExerciseStateMachine


class DummyLandmark:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


def make_landmarks(coords):
    return [DummyLandmark(x, y) for x, y in coords]


def test_state_machine_updates_and_counts_reps() -> None:
    machine = ExerciseStateMachine()
    thresholds = {"rest": 160.0, "transition": 100.0, "complete": 40.0}
    states = []

    states.append(machine.update(170.0, thresholds)[0])
    states.append(machine.update(120.0, thresholds)[0])
    states.append(machine.update(30.0, thresholds)[0])
    states.append(machine.update(120.0, thresholds)[0])
    state, rep_completed = machine.update(170.0, thresholds)

    assert state == machine.REST
    assert rep_completed is True


def test_exercise_angle_landmarks_use_the_correct_joint_triplets() -> None:
    assert Squat().get_angle_landmarks() == [23, 25, 27]
    assert BicepCurl().get_angle_landmarks() == [11, 13, 15]


def test_side_view_validation_rejects_frontal_pose_before_counting() -> None:
    squat = Squat()

    side_view = [
        (0.50, 0.50),
    ] * 11 + [
        (0.35, 0.35),  # 11
        (0.38, 0.35),  # 12
    ] + [(0.50, 0.50)] * 10 + [
        (0.32, 0.62),  # 23
        (0.34, 0.62),  # 24
    ] + [(0.50, 0.50)] * 8 + [
        (0.30, 0.75),  # 27
    ] + [(0.50, 0.50)] * 3

    frontal = [
        (0.50, 0.50),
    ] * 11 + [
        (0.18, 0.35),  # 11
        (0.82, 0.35),  # 12
    ] + [(0.50, 0.50)] * 10 + [
        (0.22, 0.62),  # 23
        (0.78, 0.62),  # 24
    ] + [(0.50, 0.50)] * 8 + [
        (0.25, 0.75),  # 27
    ] + [(0.50, 0.50)] * 3

    side_view_landmarks = make_landmarks(side_view)
    frontal_landmarks = make_landmarks(frontal)

    valid, _ = squat.is_valid_pose(side_view_landmarks, (720, 1280, 3))
    invalid, message = squat.is_valid_pose(frontal_landmarks, (720, 1280, 3))

    assert valid is True
    assert invalid is False
    assert "Turn your body to the side" in message
