"""Tests for joint angle and coordinate utility functions."""

from pose_engine.angle_utils import calculate_angle, calculate_offset_angle


def test_calculate_angle_returns_zero_for_collinear_points() -> None:
    angle = calculate_angle((0.0, 0.0), (1.0, 0.0), (2.0, 0.0))
    assert isinstance(angle, float)


def test_calculate_offset_angle_with_vertical_points() -> None:
    offset = calculate_offset_angle((0.0, 0.0), (0.0, 1.0))
    assert offset == 0.0
