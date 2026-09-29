/**
 * Hook for running a pose analysis session using a webcam canvas.
 */
import { useEffect, useState } from 'react';
import { analyseFrame } from '../api/pose.js';

const FRAME_INTERVAL_MS = 250;
const INITIAL_BACKOFF_MS = 1000;
const MAX_BACKOFF_MS = 8000;

function wait(ms, signal) {
  return new Promise((resolve) => {
    const timeoutId = window.setTimeout(resolve, ms);
    signal.addEventListener('abort', () => {
      window.clearTimeout(timeoutId);
      resolve();
    }, { once: true });
  });
}

function canvasToBlob(canvas) {
  return new Promise((resolve) => {
    canvas.toBlob(resolve, 'image/jpeg');
  });
}

export default function usePoseSession({ exercise, sessionId, isRunning, canvasRef, videoRef, streamVersion = 0 }) {
  const [angle, setAngle] = useState(null);
  const [state, setState] = useState('Rest');
  const [feedback, setFeedback] = useState('');
  const [repCount, setRepCount] = useState(0);
  const [correctReps, setCorrectReps] = useState(0);
  const [incorrectReps, setIncorrectReps] = useState(0);
  const [accuracy, setAccuracy] = useState(0);
  const [landmarks, setLandmarks] = useState([]);
  const [isAnalysing, setIsAnalysing] = useState(false);

  const reset = () => {
    setAngle(null);
    setState('Rest');
    setFeedback('');
    setRepCount(0);
    setCorrectReps(0);
    setIncorrectReps(0);
    setAccuracy(0);
    setLandmarks([]);
    setIsAnalysing(false);
  };

  useEffect(() => {
    if (!isRunning || !canvasRef?.current) {
      return undefined;
    }

    let isStopped = false;
    const controller = new AbortController();

    async function processFrames() {
      let backoffMs = INITIAL_BACKOFF_MS;

      while (!isStopped) {
        const canvas = canvasRef.current;
        const context = canvas?.getContext('2d');
        const video = videoRef?.current;

        if (!canvas || !context || !video) {
          await wait(FRAME_INTERVAL_MS, controller.signal);
          continue;
        }

        try {
          context.drawImage(video, 0, 0, canvas.width, canvas.height);
          const blob = await canvasToBlob(canvas);
          if (!blob) {
            throw new Error('Unable to capture a video frame.');
          }

          setIsAnalysing(true);
          const response = await analyseFrame(blob, exercise, sessionId, controller.signal);
          if (isStopped) {
            return;
          }
          setAngle(response.angle ?? null);
          setState(response.state ?? 'Rest');
          setFeedback(response.feedback || 'Waiting for results...');
          setRepCount(response.rep_count ?? 0);
          setCorrectReps(response.correct_reps ?? 0);
          setIncorrectReps(response.incorrect_reps ?? 0);
          setAccuracy(response.accuracy ?? 0);
          setLandmarks(Array.isArray(response.landmarks) ? response.landmarks : []);
          backoffMs = INITIAL_BACKOFF_MS;
        } catch (error) {
          if (isStopped) {
            return;
          }

          const status = error?.response?.status;
          if (status === 429) {
            setFeedback(`Pose analysis is rate limited. Retrying in ${Math.ceil(backoffMs / 1000)}s.`);
          } else {
            setFeedback('Pose analysis failed. Retrying shortly.');
          }
          await wait(backoffMs, controller.signal);
          backoffMs = Math.min(backoffMs * 2, MAX_BACKOFF_MS);
        } finally {
          if (!isStopped) {
            setIsAnalysing(false);
          }
        }

        if (!isStopped) {
          await wait(FRAME_INTERVAL_MS, controller.signal);
        }
      }
    }

    processFrames();

    return () => {
      isStopped = true;
      controller.abort();
      setLandmarks([]);
      setIsAnalysing(false);
    };
  }, [canvasRef, exercise, isRunning, sessionId, streamVersion, videoRef]);

  return { angle, state, feedback, repCount, correctReps, incorrectReps, accuracy, landmarks, isAnalysing, reset };
}
