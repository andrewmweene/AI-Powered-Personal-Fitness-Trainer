# Feature guide: pose engine (`pose_engine/`)

> Open this file alongside the relevant source file in VS Code.  
> Each section maps directly to a file. Read the section, then ask Copilot  
> to implement the function described using `Ctrl+I` (inline chat) or  
> highlight the stub and press `Ctrl+Shift+I`.

---

## Overview

The pose engine is the core computer-vision layer. It owns everything from raw
webcam frames to joint angles, exercise state tracking, and corrective feedback
text. Nothing outside this package should ever call MediaPipe or OpenCV directly.

**Data flow:**

```
webcam frame (BGR np.ndarray)
    ↓  camera.py
RGB frame
    ↓  detector.py
33 MediaPipe landmarks
    ↓  angle_utils.py
joint angles (degrees)
    ↓  exercises/<name>.py  +  state_machine.py
(state, rep_completed, feedback_text)
    ↓  feedback.py
annotated frame + overlay text
```

---

## `camera.py` — webcam capture manager

### What to implement

A context-manager class `CameraManager` that wraps `cv2.VideoCapture`.

```python
# Copilot prompt to use (paste into inline chat on the stub):
# Implement CameraManager as a Python context manager.
# __enter__ should call cv2.VideoCapture(0), set frame width to 1280 and
# height to 720, and return self.
# __exit__ should release the capture and destroy all OpenCV windows.
# read_frame() should call cap.read(), raise a RuntimeError if ret is False,
# flip the frame horizontally (selfie mirror effect using cv2.flip with code 1),
# convert BGR to RGB using cv2.cvtColor, set frame.flags.writeable = False,
# and return the RGB frame.
```

### Key details

- Always flip horizontally (`cv2.flip(frame, 1)`) so the image acts like a mirror.
  Without this, the user's left arm appears on the right side of the screen,
  which is deeply confusing during exercise.
- Set `frame.flags.writeable = False` before passing to MediaPipe. This avoids
  a memory copy and measurably improves FPS on low-end machines.
- After MediaPipe processing, set `frame.flags.writeable = True` before drawing
  overlays — OpenCV draw functions need a writeable buffer.

---

## `detector.py` — MediaPipe pose detection wrapper

### What to implement

Class `PoseDetector` with a single responsibility: run BlazePose on a frame.

```python
# Copilot prompt:
# Implement PoseDetector.__init__ to initialise mp.solutions.pose.Pose with
# static_image_mode=False, model_complexity=1, smooth_landmarks=True,
# min_detection_confidence and min_tracking_confidence from constructor args.
# Store the pose object as self.pose.
#
# Implement detect(frame: np.ndarray) to call self.pose.process(frame) and
# return the results object (which may have .pose_landmarks as None if no
# person detected).
#
# Implement draw_landmarks(frame, results) to call
# mp.solutions.drawing_utils.draw_landmarks with POSE_CONNECTIONS and custom
# DrawingSpec: landmark color (0,255,0) thickness 2 radius 2,
# connection color (0,0,255) thickness 2. Return the annotated frame.
```

### Key details

- Use `model_complexity=1` (the balanced model). `model_complexity=2` is more
  accurate but too slow for real-time use on a standard laptop CPU.
- Always check `if results.pose_landmarks is None` before extracting coordinates.
  MediaPipe returns `None` when no person is visible in the frame.
- The `draw_landmarks` method should only draw when landmarks are not None.

---

## `angle_utils.py` — joint angle mathematics

### What to implement

Three pure functions with no side effects. These are the most important functions
in the entire project — every exercise depends on them being correct.

### `calculate_angle(a, b, c) -> float`

```python
# Copilot prompt:
# Implement calculate_angle using numpy.
# a, b, c are each (x, y) tuples representing pixel coordinates.
# b is the vertex (the joint whose angle we are measuring).
# Use np.arctan2 to compute the angle at b:
#   radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
# Convert to degrees: angle = np.abs(radians * 180.0 / np.pi)
# If angle > 180, set angle = 360 - angle.
# Return the angle as a float.
```

**Example angles for reference during testing:**

| Exercise | Landmarks (a, b, c) | Correct range |
|---|---|---|
| Bicep curl (rest) | shoulder, elbow, wrist | 145–200° |
| Bicep curl (contracted) | shoulder, elbow, wrist | 35–84° |
| Squat (standing) | hip, knee, ankle | 160–180° |
| Squat (deep) | hip, knee, ankle | 70–100° |
| Push-up (up) | shoulder, elbow, wrist | 150–180° |
| Push-up (down) | shoulder, elbow, wrist | 60–90° |

### `get_landmark_coords(landmarks, landmark_id, frame_shape) -> tuple[int, int]`

```python
# Copilot prompt:
# Implement get_landmark_coords.
# landmarks is the results.pose_landmarks.landmark list from MediaPipe.
# landmark_id is an integer index (0-32).
# frame_shape is the (height, width, channels) tuple from frame.shape.
# MediaPipe returns normalised coordinates in range [0.0, 1.0].
# Convert to pixel coordinates:
#   x = int(landmarks[landmark_id].x * frame_shape[1])
#   y = int(landmarks[landmark_id].y * frame_shape[0])
# Return (x, y).
```

### `calculate_offset_angle(p1, p2) -> float`

```python
# Copilot prompt:
# Implement calculate_offset_angle.
# p1 and p2 are (x, y) pixel coordinate tuples.
# Compute the angle of the line p1->p2 relative to the vertical axis.
# offset = np.abs(np.degrees(np.arctan((p2[0]-p1[0]) / (p2[1]-p1[1]+1e-6))))
# This is used to check whether the user is standing in the correct
# orientation for a given exercise. Return the offset in degrees.
# A value < 35 degrees means side view; > 65 degrees means frontal view.
```

---

## `state_machine.py` — exercise state machine

### What to implement

Class `ExerciseStateMachine` — the logic that decides when a rep has been
completed correctly.

```python
# Copilot prompt:
# Implement ExerciseStateMachine with the following state constants as class
# attributes: STATE_REST = "s1", STATE_TRANSITION = "s2", STATE_COMPLETE = "s3"
#
# __init__ should set:
#   self.current_state = STATE_REST
#   self.correct_count = 0
#   self.incorrect_count = 0
#   self.last_activity_time = time.time()
#   self.inactive_threshold = 10.0  (seconds before reset)
#
# update(angle, thresholds) method:
#   thresholds is a dict with keys "rest_min", "rest_max",
#   "transition_min", "transition_max", "complete_min", "complete_max".
#   Check inactivity: if time.time() - last_activity_time > inactive_threshold,
#   call reset() and return (STATE_REST, False).
#   Determine the new state from the angle vs thresholds.
#   Valid transitions: REST->TRANSITION, TRANSITION->COMPLETE,
#   COMPLETE->TRANSITION, TRANSITION->REST.
#   Only increment correct_count when completing the full cycle back to REST.
#   If an invalid transition occurs (e.g. REST->COMPLETE, skipping TRANSITION),
#   increment incorrect_count.
#   Update last_activity_time = time.time().
#   Return (current_state, rep_completed: bool).
#
# reset() sets current_state back to STATE_REST and resets the timer.
```

### Thresholds for each exercise

These values go into each exercise's `get_angle_thresholds()` method:

| Exercise | Angle joint | REST | TRANSITION | COMPLETE |
|---|---|---|---|---|
| Bicep curl | elbow | 145–200° | 85–144° | 35–84° |
| Squat | knee | 160–180° | 110–159° | 70–109° |
| Push-up | elbow | 150–180° | 90–149° | 60–89° |
| Dumbbell fly | elbow | 150–180° | 110–149° | 70–109° |
| Kickback | elbow | 145–180° | 90–144° | 35–89° |

---

## `exercises/base_exercise.py` — abstract base class

```python
# Copilot prompt:
# Implement BaseExercise as an abstract base class using Python's abc module.
# Abstract methods:
#   get_required_landmarks() -> list[int]
#     Return the list of MediaPipe landmark IDs needed for this exercise.
#   get_angle_thresholds() -> dict
#     Return the threshold dict for the state machine.
#   get_feedback(angle: float, state: str) -> str
#     Return a corrective feedback string based on current angle and state.
#   requires_side_view() -> bool
#     Return True if the camera must be positioned to the user's side.
# Concrete method:
#   get_display_name() -> str  (return self.__class__.__name__ by default)
```

---

## `exercises/squat.py` — squat implementation

```python
# Copilot prompt:
# Implement Squat(BaseExercise).
# Required landmarks: LEFT_HIP (23), LEFT_KNEE (25), LEFT_ANKLE (27),
#   LEFT_SHOULDER (11), NOSE (0).
# requires_side_view() returns True.
# get_angle_thresholds() returns the squat thresholds from the table above.
# get_feedback(angle, state):
#   If state is COMPLETE and angle < 70: return "Good depth! Drive through heels"
#   If state is TRANSITION and angle > 100: return "Go lower — aim for 90 degrees"
#   If state is REST and angle < 155: return "Fully extend knees at the top"
#   Otherwise: return ""
```

Implement `bicep_curl.py`, `pushup.py`, `dumbbell_fly.py`, and `kickback.py`
following exactly the same pattern as `squat.py` but with their respective
landmark IDs and thresholds.

---

## `feedback.py` — overlay rendering

```python
# Copilot prompt:
# Implement draw_feedback_overlay(frame, rep_count, accuracy_pct,
#   feedback_text, state) -> np.ndarray.
# Use cv2.putText to draw on the frame:
#   Top-left: "Reps: {rep_count}" in white, font scale 1.5, thickness 3
#   Top-right: "Accuracy: {accuracy_pct:.0f}%" — green if >= 80, red if < 80
#   Bottom-centre: feedback_text in yellow if non-empty, font scale 1.0
#   Bottom-left: state indicator ("REST" / "MOVING" / "COMPLETE") in cyan
# Use cv2.rectangle to draw a semi-transparent black bar at the top and bottom
# of the frame as a background for text (use addWeighted for transparency).
# Return the annotated frame.
```

---

## Testing the pose engine

Run with:
```bash
pytest tests/test_angle_utils.py -v
pytest tests/test_state_machine.py -v
```

Quick manual test (run from project root):
```bash
python -c "
from pose_engine.camera import CameraManager
from pose_engine.detector import PoseDetector
from pose_engine.exercises.squat import Squat
import cv2

exercise = Squat()
detector = PoseDetector()

with CameraManager() as cam:
    while True:
        frame = cam.read_frame()
        results = detector.detect(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
"
```
