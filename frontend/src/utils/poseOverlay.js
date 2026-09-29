const VISIBILITY_THRESHOLD = 0.5;
const MIN_KEY_JOINTS = 4;
const KEY_JOINTS = [11, 12, 23, 24, 25, 26, 27, 28];
const POSE_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 7], [0, 4], [4, 5], [5, 6], [6, 8],
  [9, 10], [11, 12], [11, 13], [13, 15], [15, 17], [15, 19], [15, 21],
  [12, 14], [14, 16], [16, 18], [16, 20], [16, 22], [11, 23], [12, 24],
  [23, 24], [23, 25], [25, 27], [27, 29], [27, 31], [24, 26], [26, 28],
  [28, 30], [28, 32], [29, 31], [30, 32],
];

function getPoint(landmark, width, height) {
  if (!landmark) {
    return null;
  }

  const confidence = landmark.visibility ?? landmark.confidence;
  if (confidence !== undefined && confidence !== null && Number(confidence) < VISIBILITY_THRESHOLD) {
    return null;
  }
  if (confidence !== undefined && confidence !== null && !Number.isFinite(Number(confidence))) {
    return null;
  }

  const x = Number(landmark?.x);
  const y = Number(landmark?.y);
  if (!Number.isFinite(x) || !Number.isFinite(y)) {
    return null;
  }

  const isNormalized = x >= 0 && x <= 1 && y >= 0 && y <= 1;
  return {
    x: isNormalized ? x * width : x,
    y: isNormalized ? y * height : y,
  };
}

export function drawPoseOverlay(canvas, landmarks) {
  if (!canvas) {
    return;
  }

  const context = canvas.getContext('2d');
  if (!context) {
    return;
  }

  context.clearRect(0, 0, canvas.width, canvas.height);
  if (!Array.isArray(landmarks) || landmarks.length === 0) {
    return;
  }

  const points = landmarks.map((landmark) => getPoint(landmark, canvas.width, canvas.height));
  const detectedKeyJoints = KEY_JOINTS.reduce(
    (count, index) => count + (points[index] ? 1 : 0),
    0,
  );
  if (detectedKeyJoints < MIN_KEY_JOINTS) {
    return;
  }

  context.globalAlpha = detectedKeyJoints === KEY_JOINTS.length ? 1 : 0.65;
  context.strokeStyle = '#38bdf8';
  context.lineWidth = Math.max(2, canvas.width / 320);
  context.lineCap = 'round';

  POSE_CONNECTIONS.forEach(([startIndex, endIndex]) => {
    const start = points[startIndex];
    const end = points[endIndex];
    if (!start || !end) {
      return;
    }
    context.beginPath();
    context.moveTo(start.x, start.y);
    context.lineTo(end.x, end.y);
    context.stroke();
  });

  context.fillStyle = '#f8fafc';
  context.strokeStyle = '#0284c7';
  context.lineWidth = 1;
  points.forEach((point) => {
    if (!point) {
      return;
    }
    context.beginPath();
    context.arc(point.x, point.y, Math.max(3, canvas.width / 160), 0, Math.PI * 2);
    context.fill();
    context.stroke();
  });
  context.globalAlpha = 1;
}

export function resizePoseOverlay(canvas, landmarks) {
  if (!canvas) {
    return;
  }

  const bounds = canvas.getBoundingClientRect();
  const pixelRatio = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.round(bounds.width * pixelRatio));
  canvas.height = Math.max(1, Math.round(bounds.height * pixelRatio));
  drawPoseOverlay(canvas, landmarks);
}