/**
 * Live exercise session page using webcam feed and pose analysis.
 */
import React, { useEffect, useMemo, useState } from 'react';
import useWebcam from '../hooks/useWebcam.js';
import usePoseSession from '../hooks/usePoseSession.js';
import MetricCard from '../components/ui/MetricCard.jsx';
import Button from '../components/ui/Button.jsx';
import AlertBanner from '../components/ui/AlertBanner.jsx';
import { saveSession } from '../api/sessions.js';

const exercises = [
  'Squat',
  'Bicep Curl',
  'Push-up',
  'Dumbbell Fly',
  'Dumbbell Kickback',
];

export default function Exercise() {
  const { videoRef, canvasRef, isReady, error } = useWebcam({ width: 640, height: 480 });
  const [exercise, setExercise] = useState(exercises[0]);
  const [sessionId] = useState(() => (window.crypto?.randomUUID ? window.crypto.randomUUID() : `session-${Math.random().toString(36).slice(2)}`));
  const [isRunning, setIsRunning] = useState(false);
  const [startedAt, setStartedAt] = useState(null);
  const [saved, setSaved] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');
  const [saveError, setSaveError] = useState('');
  const [showSummary, setShowSummary] = useState(false);
  const [loading, setLoading] = useState(false);
  const { angle, state, feedback, repCount, correctReps, incorrectReps, accuracy, isAnalysing } = usePoseSession({ exercise, sessionId, isRunning, canvasRef, videoRef });
  const [history, setHistory] = useState([]);

  const duration = useMemo(() => {
    if (!startedAt) return '00:00';
    const seconds = Math.floor((Date.now() - startedAt) / 1000);
    const mins = String(Math.floor(seconds / 60)).padStart(2, '0');
    const secs = String(seconds % 60).padStart(2, '0');
    return `${mins}:${secs}`;
  }, [startedAt, isRunning]);

  const handleStart = () => {
    setSaveError('');
    setSaved(false);
    setShowSummary(false);
    setStartedAt(Date.now());
    setHistory([]);
    setIsRunning(true);
  };

  const handleStop = () => {
    setIsRunning(false);
    setShowSummary(true);
  };

  useEffect(() => {
    if (!feedback || !isRunning) return;
    setHistory((prev) => [feedback, ...prev].slice(0, 5));
  }, [feedback, isRunning]);

  const handleSave = async () => {
    setSaveError('');
    setSaveMessage('');
    try {
      await saveSession({ exercise, rep_count: repCount, correct_reps: correctReps, incorrect_reps: incorrectReps, accuracy, duration_seconds: Math.floor((Date.now() - startedAt) / 1000), session_id: sessionId });
      setSaved(true);
      setSaveMessage('Session saved successfully.');
    } catch (apiError) {
      setSaveError(apiError.response?.data?.detail || 'Unable to save session.');
    }
  };

  const handleDiscard = () => {
    setIsRunning(false);
    setShowSummary(false);
    setStartedAt(null);
    setHistory([]);
  };

  return (
    <div className="grid gap-8 xl:grid-cols-[60%_40%]">
      <div className="rounded-3xl bg-white p-6 shadow-sm">
        {error ? <AlertBanner type="error" message={error} onDismiss={() => {}} /> : null}
        <div className="relative overflow-hidden rounded-3xl border border-slate-200 bg-black">
          <video ref={videoRef} className="aspect-video w-full bg-black object-cover" />
          <canvas className="pointer-events-none absolute inset-0" width="640" height="480" />
        </div>
        <div className="mt-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <label className="block w-full text-sm text-slate-700 sm:w-auto">
            Exercise
            <select value={exercise} onChange={(e) => setExercise(e.target.value)} className="mt-2 block w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 focus:border-primary focus:outline-none sm:w-64">
              {exercises.map((option) => <option key={option} value={option}>{option}</option>)}
            </select>
          </label>
          <div className="flex flex-wrap gap-3">
            <Button variant="primary" onClick={handleStart} disabled={!isReady || isRunning} loading={isAnalysing && isRunning}>Start Session</Button>
            <Button variant="danger" onClick={handleStop} disabled={!isRunning}>Stop Session</Button>
          </div>
        </div>
      </div>

      <div className="space-y-5">
        <MetricCard label="Reps completed" value={repCount} />
        <MetricCard label="Posture accuracy" value={`${accuracy ?? 0}%`} />
        <MetricCard label="Current state" value={state || 'Rest'} />
        <div className="rounded-3xl bg-yellow-50 p-5">
          <h3 className="mb-2 text-sm font-semibold text-slate-900">Feedback</h3>
          <p className="text-sm text-slate-700">{feedback || 'Awaiting pose analysis...'}</p>
        </div>
        <div className="rounded-3xl bg-white p-5 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">Session log</h3>
          <ul className="space-y-3 text-sm text-slate-700">
            {history.length ? history.map((entry, index) => <li key={`${entry}-${index}`} className="rounded-2xl bg-slate-50 p-3">{entry}</li>) : <li>No messages yet.</li>}
          </ul>
        </div>
      </div>

      {showSummary ? (
        <div className="col-span-full rounded-3xl bg-white p-6 shadow-sm">
          <h3 className="mb-4 text-xl font-semibold text-slate-900">Session summary</h3>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard label="Exercise" value={exercise} />
            <MetricCard label="Total reps" value={repCount} />
            <MetricCard label="Correct reps" value={correctReps} colour="success" />
            <MetricCard label="Incorrect reps" value={incorrectReps} colour="danger" />
            <MetricCard label="Accuracy" value={`${accuracy ?? 0}%`} />
            <MetricCard label="Duration" value={duration} />
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <Button onClick={handleSave} loading={loading}>{saved ? 'Saved' : 'Save session'}</Button>
            <Button variant="secondary" onClick={handleDiscard}>Discard</Button>
            {saveMessage ? <p className="text-sm text-emerald-700">{saveMessage}</p> : null}
            {saveError ? <p className="text-sm text-rose-700">{saveError}</p> : null}
          </div>
        </div>
      ) : null}
    </div>
  );
}
