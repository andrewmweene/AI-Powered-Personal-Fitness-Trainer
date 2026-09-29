# Pose video regression harness

`scripts/pose_video_harness.py` exercises the same FastAPI endpoint used by the frontend, but reads frames from recorded videos. The repository is Python/FastAPI, so the harness uses Python, OpenCV, and `httpx`.

## Setup

Install the project dependencies and start the backend:

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

The pose endpoint requires authentication. You can provide an existing access token or log in with a local account:

```bash
python scripts/pose_video_harness.py squat.mp4 squat \
  --username maya_beginner --password "FitTrainer123!"
```

The script samples one frame every 250 ms, matching the live frontend's approximately 4 fps request cadence. Requests are sent sequentially using the endpoint's multipart fields:

- `file`: JPEG frame
- `exercise`: backend exercise name
- `session_id`: one stable ID per clip, so rep-counting state is preserved

## Single clip

```bash
python scripts/pose_video_harness.py recordings/squat.mp4 squat \
  --token "$POSE_TOKEN" \
  --frames-report out/squat-frames.csv \
  --report out/squat-summary.csv \
  --annotated-dir out/annotated
```

Accepted exercise aliases include `squat`, `push-up`, `pushup`, `bicep-curl`, `dumbbell-fly`, and `dumbbell-kickback`.

The per-frame CSV records timestamp, frame number, reps, state, accuracy, detected key-joint count, low-confidence status, and zero-coordinate warnings. The summary CSV also records rep decreases, suspicious `rest -> up` transitions, API errors, and pass/fail status.

## Batch clips and expected reps

Pass a folder instead of a file. For batch mode, put exercise and expected rep metadata in a JSON object keyed by filename:

```json
{
  "squat_beginner_01.mp4": {
    "exercise": "squat",
    "expected_reps": 8
  },
  "pushup_intermediate_01.mp4": {
    "exercise": "push-up",
    "expected_reps": 12
  },
  "curl_side_view.mp4": {
    "exercise": "bicep-curl"
  }
}
```

Run the folder:

```bash
python scripts/pose_video_harness.py recordings/ \
  --metadata pose-cases.json \
  --username maya_beginner --password "FitTrainer123!" \
  --report out/batch-summary.csv \
  --frames-report out/batch-frames.csv \
  --annotated-dir out/annotated
```

A row passes when `expected_reps` is supplied and the final detected count matches it. Clips without expected reps are reported with an empty pass value rather than being treated as failures. The process exits with status `1` if any expected count fails and status `2` for command, authentication, or input errors.

## Useful options

- `--base-url http://localhost:8000` or `POSE_API_URL` to target another backend.
- `--token` or `POSE_TOKEN` for a bearer token.
- `--username`/`--password` or `POSE_USERNAME`/`POSE_PASSWORD` for login.
- `--sample-ms 300` to reduce sampling to about 3.3 fps.
- `--annotated-dir out/annotated` to save MP4s with the skeleton, reps, state, and accuracy drawn over the source frames.

The harness warns when the API returns a literal `(0, 0)` landmark, counts frames with fewer than four visible key joints, and continues processing later frames where possible.
