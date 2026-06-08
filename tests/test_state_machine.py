"""Tests for the exercise state machine."""

from pose_engine.state_machine import ExerciseStateMachine


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
