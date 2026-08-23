from pose_engine import detector


def test_get_model_path_uses_project_model_dir(tmp_path, monkeypatch):
    project_dir = tmp_path / "project"
    model_dir = project_dir / ".models"
    model_dir.mkdir(parents=True)
    model_file = model_dir / "pose_landmarker_lite.task"
    model_file.write_bytes(b"fake-model")

    monkeypatch.setattr(detector, "PROJECT_ROOT", project_dir)
    monkeypatch.setattr(detector, "_download_pose_model", lambda *args, **kwargs: None)

    assert detector._get_model_path() == str(model_file)


def test_pose_detector_uses_image_mode(monkeypatch):
    captured = {}

    class FakeLandmarker:
        @staticmethod
        def create_from_options(options):
            captured["running_mode"] = options.running_mode
            return FakeLandmarker()

        def detect(self, image):
            return {"pose_landmarks": []}

    monkeypatch.setattr(detector, "_get_model_path", lambda: "mock_model.task")
    monkeypatch.setattr(detector, "PoseLandmarker", FakeLandmarker)

    pose_detector = detector.PoseDetector()

    assert pose_detector.pose_landmarker is not None
    assert captured["running_mode"] == detector.RunningMode.IMAGE
