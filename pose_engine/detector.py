"""MediaPipe pose detection wrapper for real-time posture analysis."""

from __future__ import annotations

import numpy as np
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe import Image, ImageFormat


# Try to load pose model from a bundled location or return None if not available
def _get_model_path() -> str | None:
    """Get the path to the pose landmarker model, if available."""
    import os
    import importlib.resources as resources
    
    try:
        # Try to find the model in the mediapipe package
        if hasattr(resources, 'files'):  # Python 3.9+
            try:
                files = resources.files('mediapipe').joinpath('tasks/examples/mp4/pose_landmarker.task')
                if files.is_file():
                    return str(files)
            except Exception:
                pass
        
        # Fallback: check common directories
        common_paths = [
            os.path.join(os.path.expanduser('~'), '.mediapipe', 'pose_landmarker.task'),
            '/usr/local/mediapipe/pose_landmarker.task',
            'pose_landmarker.task',
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
    except Exception:
        pass
    
    return None


class PoseDetector:
    """Wraps MediaPipe Pose for frame-by-frame landmark detection.
    
    Uses the new MediaPipe Tasks API if a model is available,
    otherwise falls back to a mock implementation for testing.
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        """Initialize the pose detector with the specified confidence thresholds.

        Args:
            min_detection_confidence: Minimum detection score to consider pose landmarks.
            min_tracking_confidence: Minimum tracking confidence for landmark stability.
        """
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.pose_landmarker = None
        self._using_fallback = False
        
        # Try to initialize with the new API
        model_path = _get_model_path()
        if model_path:
            try:
                options = PoseLandmarkerOptions(
                    base_options=BaseOptions(model_asset_path=model_path),
                    running_mode=RunningMode.VIDEO,
                    min_pose_detection_confidence=min_detection_confidence,
                    min_pose_presence_confidence=min_tracking_confidence,
                )
                self.pose_landmarker = PoseLandmarker.create_from_options(options)
            except Exception as e:
                print(f"Warning: Could not load PoseLandmarker model: {e}")
                self._using_fallback = True
        else:
            self._using_fallback = True
            print("Warning: Pose model not found. Using fallback mode (landmarks will be empty)")

    def detect(self, frame: np.ndarray):
        """Run pose detection on a single RGB frame.

        Args:
            frame: The input image frame in RGB color space.

        Returns:
            The MediaPipe pose detection results object.
        """
        if self.pose_landmarker is None:
            # Return a mock result object for fallback mode
            return type('MockResult', (), {
                'pose_landmarks': [],
                'pose_world_landmarks': [],
                'segmentation_masks': None,
            })()
        
        mp_image = Image(image_format=ImageFormat.SRGB, data=frame)
        return self.pose_landmarker.detect(mp_image)

    def draw_landmarks(self, frame: np.ndarray, results) -> np.ndarray:
        """Overlay pose landmarks and connections on the provided frame.

        Args:
            frame: The original RGB frame to annotate.
            results: The MediaPipe pose detection results.

        Returns:
            Annotated frame with pose landmarks rendered (unchanged if in fallback mode).
        """
        if results is None or not hasattr(results, 'pose_landmarks') or len(results.pose_landmarks) == 0:
            return frame
        
        if self._using_fallback:
            return frame
        
        try:
            # Use the new drawing utils if available
            from mediapipe.tasks.python.vision import drawing_utils as mp_drawing_utils
            mp_image = Image(image_format=ImageFormat.SRGB, data=frame)
            
            mp_drawing_utils.draw_landmarks(
                mp_image,
                results.pose_landmarks[0],
            )
            return mp_image.numpy_view()
        except Exception:
            return frame
