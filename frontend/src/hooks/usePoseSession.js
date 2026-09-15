/**
 * Hook for running a pose analysis session using a webcam canvas.
 */
import { useEffect, useRef, useState } from 'react';
import { analyseFrame } from '../api/pose.js';

export default function usePoseSession({ exercise, sessionId, isRunning, canvasRef, videoRef }) {
  const intervalRef = useRef(null);
  const [angle, setAngle] = useState(null);
  const [state, setState] = useState('Rest');
  const [feedback, setFeedback] = useState('');
  const [repCount, setRepCount] = useState(0);
  const [correctReps, setCorrectReps] = useState(0);
  const [incorrectReps, setIncorrectReps] = useState(0);
  const [accuracy, setAccuracy] = useState(0);
  const [isAnalysing, setIsAnalysing] = useState(false);

  const reset = () => {
    setAngle(null);
    setState('Rest');
    setFeedback('');
    setRepCount(0);
    setCorrectReps(0);
    setIncorrectReps(0);
    setAccuracy(0);
    setIsAnalysing(false);
  };

  useEffect(() => {
    if (!isRunning || !canvasRef?.current) {
      return undefined;
    }

    async function processFrame() {
      if (!canvasRef.current) {
        return;
      }
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      const video = videoRef?.current;
      if (!context || !video) {
        return;
      }
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      setIsAnalysing(true);
      canvas.toBlob(async (blob) => {
        if (!blob) {
          setIsAnalysing(false);
          return;
        }

        try {
          const response = await analyseFrame(blob, exercise, sessionId);
          setAngle(response.angle ?? null);
          setState(response.state ?? 'Rest');
          setFeedback(response.feedback || 'Waiting for results...');
          setRepCount(response.rep_count ?? 0);
          setCorrectReps(response.correct_reps ?? 0);
          setIncorrectReps(response.incorrect_reps ?? 0);
          setAccuracy(response.accuracy ?? 0);
        } catch (error) {
          setFeedback('Pose analysis failed. Please try again.');
        } finally {
          setIsAnalysing(false);
        }
      }, 'image/jpeg');
    }

    intervalRef.current = window.setInterval(processFrame, 100);

    return () => {
      if (intervalRef.current) {
        window.clearInterval(intervalRef.current);
      }
    };
  }, [canvasRef, exercise, isRunning, sessionId, videoRef]);

  return { angle, state, feedback, repCount, correctReps, incorrectReps, accuracy, isAnalysing, reset };
}
