"""Tests for joint angle and coordinate utility functions."""

from pose_engine.angle_utils import calculate_angle, calculate_offset_angle


def test_calculate_angle_collinear_is_180() -> None:
    angle = calculate_angle((0.0, 0.0), (0.0, 100.0), (0.0, 200.0))
    assert isinstance(angle, float)
    assert abs(angle - 180.0) < 1.0, f"Expected ~180 degrees, got {angle}"


def test_calculate_angle_right_angle_is_90() -> None:
    angle = calculate_angle((0.0, 0.0), (0.0, 100.0), (100.0, 100.0))
    assert isinstance(angle, float)
    assert abs(angle - 90.0) < 1.0, f"Expected ~90 degrees, got {angle}"


def test_calculate_offset_angle_with_vertical_points() -> None:
    offset = calculate_offset_angle((0.0, 0.0), (0.0, 1.0))
    assert offset == 0.0
