"""OpenCV webcam capture manager for live exercise streaming."""

from __future__ import annotations

import cv2
import numpy as np


class CameraManager:
    """Manages webcam capture and frame retrieval for live exercise sessions."""

    def __init__(self, camera_index: int = 0) -> None:
        """Initialize the camera manager with the selected device index.

        Args:
            camera_index: The device index for cv2.VideoCapture.
        """
        self.camera_index = camera_index
        self.capture: cv2.VideoCapture | None = None

    def __enter__(self) -> CameraManager:
        self.capture = cv2.VideoCapture(self.camera_index)
        if not self.capture.isOpened():
            raise RuntimeError(f"Unable to open camera index {self.camera_index}")
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.capture is not None:
            self.capture.release()
            self.capture = None
        cv2.destroyAllWindows()

    def read_frame(self) -> np.ndarray:
        """Read a single RGB frame from the webcam with the selfie mirror effect."""
        if self.capture is None:
            raise RuntimeError("Camera has not been started.")
        success, frame = self.capture.read()
        if not success or frame is None:
            raise RuntimeError("Failed to read frame from camera.")

        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame.flags.writeable = False
        return frame

    def start(self) -> None:
        """Open the video capture device and verify it is available."""
        self.__enter__()

    def stop(self) -> None:
        """Release the webcam resource cleanly."""
        self.__exit__(None, None, None)
