"""Regression harness for the FastAPI pose-analysis endpoint.

Examples:
    python scripts/pose_video_harness.py clip.mp4 squat --username maya_beginner --password "FitTrainer123!"
    python scripts/pose_video_harness.py clips/ --metadata pose_cases.json --token "$POSE_TOKEN"
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
import httpx

ROOT = Path(__file__).resolve().parents[1]

FRAME_INTERVAL_MS = 250
VISIBILITY_THRESHOLD = 0.5
MIN_KEY_JOINTS = 4
KEY_JOINTS = (11, 12, 23, 24, 25, 26, 27, 28)
VIDEO_EXTENSIONS = {".avi", ".m4v", ".mov", ".mp4", ".webm", ".mkv"}
EXERCISE_NAMES = {
    "squat": "Squat",
    "push-up": "Push-up",
    "pushup": "Push-up",
    "bicep-curl": "Bicep Curl",
    "bicep_curl": "Bicep Curl",
    "dumbbell-fly": "Dumbbell Fly",
    "dumbbell-kickback": "Dumbbell Kickback",
}
POSE_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10), (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (11, 23), (12, 24),
    (23, 24), (23, 25), (25, 27), (27, 29), (27, 31), (24, 26), (26, 28),
    (28, 30), (28, 32), (29, 31), (30, 32),
)


@dataclass
class ClipResult:
    video: str
    exercise: str
    expected_reps: int | None
    final_reps: int = 0
    average_accuracy: float = 0.0
    sampled_frames: int = 0
    low_confidence_frames: int = 0
    zero_coordinate_frames: int = 0
    rep_decreases: list[int] = field(default_factory=list)
    invalid_transitions: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool | None:
        if self.expected_reps is None:
            return None
        return self.final_reps == self.expected_reps and not self.errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path, help="Video file or folder of video clips")
    parser.add_argument("exercise", nargs="?", help="Exercise, e.g. squat or push-up; optional for folders with metadata")
    parser.add_argument("--base-url", default=os.getenv("POSE_API_URL", "http://localhost:8000"))
    parser.add_argument("--token", default=os.getenv("POSE_TOKEN"), help="Existing bearer token")
    parser.add_argument("--username", default=os.getenv("POSE_USERNAME"))
    parser.add_argument("--password", default=os.getenv("POSE_PASSWORD"))
    parser.add_argument("--metadata", type=Path, help="JSON metadata mapping clip names to exercise/expected_reps")
    parser.add_argument("--report", type=Path, default=Path("pose-harness-summary.csv"))
    parser.add_argument("--frames-report", type=Path, help="Optional per-frame CSV output")
    parser.add_argument("--annotated-dir", type=Path, help="Optional directory for annotated MP4 outputs")
    parser.add_argument("--sample-ms", type=int, default=FRAME_INTERVAL_MS, help="Sample interval in milliseconds (default: 250)")
    return parser.parse_args()


def canonical_exercise(value: str) -> str:
    normalized = value.strip().lower().replace(" ", "-")
    if normalized not in EXERCISE_NAMES:
        valid = ", ".join(sorted(EXERCISE_NAMES))
        raise ValueError(f"Unknown exercise '{value}'. Use one of: {valid}")
    return EXERCISE_NAMES[normalized]


def load_metadata(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    with path.open(encoding="utf-8") as metadata_file:
        raw = json.load(metadata_file)
    if not isinstance(raw, dict):
        raise ValueError("Metadata must be a JSON object keyed by video filename.")
    return {str(key): value for key, value in raw.items() if isinstance(value, dict)}


def authenticate(client: httpx.Client, args: argparse.Namespace) -> str:
    if args.token:
        return args.token
    if not args.username or not args.password:
        raise ValueError("Provide --token or both --username and --password.")
    response = client.post("/auth/login", json={"username": args.username, "password": args.password})
    response.raise_for_status()
    return response.json()["access_token"]


def point_for(landmark: dict[str, Any] | None, width: int, height: int) -> tuple[int, int] | None:
    if not landmark:
        return None
    confidence = landmark.get("visibility", landmark.get("confidence"))
    if confidence is not None:
        try:
            if float(confidence) < VISIBILITY_THRESHOLD:
                return None
        except (TypeError, ValueError):
            return None
    try:
        x = float(landmark["x"])
        y = float(landmark["y"])
    except (KeyError, TypeError, ValueError):
        return None
    if not (x == x and y == y):
        return None
    if 0 <= x <= 1 and 0 <= y <= 1:
        x *= width
        y *= height
    return round(x), round(y)


def draw_overlay(frame, landmarks: list[dict[str, Any] | None], rep_count: int, state: str, accuracy: float) -> None:
    height, width = frame.shape[:2]
    points = [point_for(landmark, width, height) for landmark in landmarks]
    detected = sum(1 for index in KEY_JOINTS if index < len(points) and points[index] is not None)
    if detected < MIN_KEY_JOINTS:
        cv2.putText(frame, "Low-confidence pose", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
        return

    color = (235, 145, 56)
    for start_index, end_index in POSE_CONNECTIONS:
        if start_index >= len(points) or end_index >= len(points):
            continue
        start, end = points[start_index], points[end_index]
        if start is not None and end is not None:
            cv2.line(frame, start, end, color, 2, cv2.LINE_AA)
    for point in points:
        if point is not None:
            cv2.circle(frame, point, max(3, width // 160), (248, 250, 252), -1, cv2.LINE_AA)
            cv2.circle(frame, point, max(3, width // 160), (3, 132, 199), 1, cv2.LINE_AA)
    cv2.rectangle(frame, (10, 10), (250, 82), (15, 23, 42), -1)
    cv2.putText(frame, f"Reps: {rep_count}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"{state}  {accuracy:.0f}%", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 230, 240), 2)


def landmarks_quality(landmarks: Any) -> tuple[int, bool]:
    if not isinstance(landmarks, list):
        return 0, False
    zero_coordinates = False
    for item in landmarks:
        if not isinstance(item, dict):
            continue
        try:
            if float(item.get("x", 1)) == 0 and float(item.get("y", 1)) == 0:
                zero_coordinates = True
                break
        except (TypeError, ValueError):
            continue
    detected = sum(1 for index in KEY_JOINTS if index < len(landmarks) and point_for(landmarks[index], 1, 1) is not None)
    return detected, zero_coordinates


def transitions_are_valid(previous: str | None, current: str) -> bool:
    previous_normalized = (previous or "").lower()
    current_normalized = current.lower()
    return not (previous_normalized in {"rest", "idle"} and current_normalized == "up")


def process_clip(client: httpx.Client, token: str, path: Path, exercise: str, expected_reps: int | None, args: argparse.Namespace, frame_writer=None, frame_csv=None) -> ClipResult:
    result = ClipResult(path.name, exercise, expected_reps)
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        result.errors.append("Unable to open video")
        return result

    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    next_sample_ms = 0.0
    frame_number = 0
    previous_reps = 0
    previous_state = None
    accuracies: list[float] = []
    latest = {"rep_count": 0, "state": "REST", "accuracy": 0, "landmarks": []}
    session_id = f"harness-{uuid.uuid4()}"

    while True:
        ok, frame = capture.read()
        if not ok:
            break
        timestamp_ms = (frame_number / fps) * 1000
        if timestamp_ms >= next_sample_ms:
            ok_jpeg, encoded = cv2.imencode(".jpg", frame)
            if not ok_jpeg:
                result.errors.append(f"Frame {frame_number}: JPEG encoding failed")
            else:
                try:
                    response = client.post(
                        "/pose/analyse-frame",
                        headers={"Authorization": f"Bearer {token}"},
                        files={"file": ("frame.jpg", encoded.tobytes(), "image/jpeg")},
                        data={"exercise": exercise, "session_id": session_id},
                    )
                    response.raise_for_status()
                    latest = response.json()
                    reps = int(latest.get("rep_count", 0))
                    state = str(latest.get("state", "REST"))
                    accuracy = float(latest.get("accuracy", 0))
                    landmarks = latest.get("landmarks", [])
                    detected, has_zero = landmarks_quality(landmarks)
                    if detected < MIN_KEY_JOINTS:
                        result.low_confidence_frames += 1
                    if has_zero:
                        result.zero_coordinate_frames += 1
                        print(f"WARNING {path.name} frame {frame_number}: landmark contains (0,0)", file=sys.stderr)
                    if reps < previous_reps:
                        result.rep_decreases.append(frame_number)
                    if not transitions_are_valid(previous_state, state):
                        result.invalid_transitions.append(f"frame {frame_number}: {previous_state}->{state}")
                    previous_reps, previous_state = reps, state
                    accuracies.append(accuracy)
                    result.sampled_frames += 1
                    if frame_csv is not None:
                        frame_csv.writerow({"video": path.name, "frame": frame_number, "timestamp_ms": round(timestamp_ms, 1), "rep_count": reps, "state": state, "accuracy": accuracy, "key_joints": detected, "low_confidence": detected < MIN_KEY_JOINTS, "zero_coordinate": has_zero})
                except (httpx.HTTPError, ValueError, KeyError) as error:
                    result.errors.append(f"Frame {frame_number}: {error}")
            next_sample_ms += args.sample_ms
        if frame_writer is not None:
            annotated = frame.copy()
            draw_overlay(annotated, latest.get("landmarks", []), int(latest.get("rep_count", 0)), str(latest.get("state", "REST")), float(latest.get("accuracy", 0)))
            frame_writer.write(annotated)
        frame_number += 1

    capture.release()
    result.final_reps = int(latest.get("rep_count", 0))
    result.average_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.0
    return result


def video_inputs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        return sorted(path for path in input_path.iterdir() if path.suffix.lower() in VIDEO_EXTENSIONS)
    raise FileNotFoundError(input_path)


def main() -> int:
    args = parse_args()
    try:
        metadata = load_metadata(args.metadata)
        videos = video_inputs(args.input)
        if not videos:
            raise ValueError(f"No supported videos found in {args.input}")
        if args.input.is_file() and not args.exercise:
            raise ValueError("An exercise argument is required for a single video")
        client = httpx.Client(base_url=args.base_url.rstrip("/"), timeout=30.0)
        token = authenticate(client, args)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        frame_file = args.frames_report.open("w", newline="", encoding="utf-8") if args.frames_report else None
        frame_csv = csv.DictWriter(frame_file, fieldnames=["video", "frame", "timestamp_ms", "rep_count", "state", "accuracy", "key_joints", "low_confidence", "zero_coordinate"]) if frame_file else None
        if frame_csv:
            frame_csv.writeheader()
        results = []
        for video in videos:
            spec = metadata.get(video.name, {})
            exercise = canonical_exercise(spec.get("exercise", args.exercise or ""))
            expected = spec.get("expected_reps")
            expected = int(expected) if expected is not None else None
            writer = None
            if args.annotated_dir:
                args.annotated_dir.mkdir(parents=True, exist_ok=True)
                capture = cv2.VideoCapture(str(video))
                width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
                height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
                fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
                capture.release()
                writer = cv2.VideoWriter(str(args.annotated_dir / f"{video.stem}_annotated.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
            result = process_clip(client, token, video, exercise, expected, args, writer, frame_csv)
            if writer:
                writer.release()
            results.append(result)
            print(f"{video.name}: reps={result.final_reps}, avg_accuracy={result.average_accuracy:.1f}%, low_confidence={result.low_confidence_frames}, pass={result.passed}")
        if frame_file:
            frame_file.close()
        with args.report.open("w", newline="", encoding="utf-8") as report_file:
            writer = csv.DictWriter(report_file, fieldnames=["video", "exercise", "expected_reps", "actual_reps", "average_accuracy", "sampled_frames", "low_confidence_frames", "zero_coordinate_frames", "rep_decreases", "invalid_transitions", "errors", "pass"])
            writer.writeheader()
            for item in results:
                writer.writerow({"video": item.video, "exercise": item.exercise, "expected_reps": item.expected_reps, "actual_reps": item.final_reps, "average_accuracy": round(item.average_accuracy, 2), "sampled_frames": item.sampled_frames, "low_confidence_frames": item.low_confidence_frames, "zero_coordinate_frames": item.zero_coordinate_frames, "rep_decreases": ";".join(map(str, item.rep_decreases)), "invalid_transitions": ";".join(item.invalid_transitions), "errors": ";".join(item.errors), "pass": item.passed})
        client.close()
        return 1 if any(item.passed is False for item in results) else 0
    except (FileNotFoundError, ValueError, httpx.HTTPError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
