"""Utility functions for calculating joint angles and view orientation."""

from __future__ import annotations

import math
from typing import Iterable, Tuple

import numpy as np


def calculate_angle(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    """Calculate the angle between three points at point b.

    Args:
        a: First point as an (x, y) tuple.
        b: Vertex point as an (x, y) tuple.
        c: Third point as an (x, y) tuple.

    Returns:
        Angle in degrees between the vectors ba and bc.
    """
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return float(angle)


def get_landmark_coords(
    landmarks: Iterable,
    landmark_id: int,
    frame_shape: tuple[int, int, int],
) -> tuple[int, int]:
    """Convert normalized MediaPipe landmark coordinates to pixel positions.

    Args:
        landmarks: The landmarks collection from MediaPipe results.
        landmark_id: The landmark index to retrieve.
        frame_shape: The shape of the image frame as (height, width, channels).

    Returns:
        Pixel coordinates (x, y) for the specified landmark.
    """
    height, width, _ = frame_shape
    landmark = landmarks[landmark_id]
    x = int(landmark.x * width)
    y = int(landmark.y * height)
    return x, y


def calculate_offset_angle(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Compute the angle of the line p1->p2 relative to the vertical axis.

    Args:
        p1: First point as an (x, y) tuple.
        p2: Second point as an (x, y) tuple.

    Returns:
        Offset angle in degrees relative to the vertical axis.
    """
    offset = np.abs(np.degrees(np.arctan((p2[0] - p1[0]) / (p2[1] - p1[1] + 1e-6))))
    return float(offset)
