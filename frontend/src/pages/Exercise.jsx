/**
 * Live exercise session page using webcam feed and pose analysis.
 */
import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { HelpCircle, Play, Square, TimerReset } from 'lucide-react';
import useWebcam from '../hooks/useWebcam.js';
import usePoseSession from '../hooks/usePoseSession.js';
import Button from '../components/ui/Button.jsx';
import AlertBanner from '../components/ui/AlertBanner.jsx';
import { getPlan } from '../api/recommendations.js';
import { saveSession } from '../api/sessions.js';
import ModeSelector from '../components/exercise/ModeSelector.jsx';
import WorkoutProgress from '../components/exercise/WorkoutProgress.jsx';
import FeedbackPanel from '../components/exercise/FeedbackPanel.jsx';
import ExerciseInstructions from './ExerciseInstructions.jsx';

const exercises = ['Squat', 'Bicep Curl', 'Push-up', 'Dumbbell Fly', 'Dumbbell Kickback'];

export default function Exercise() {
  const navigate = useNavigate();
  const [mode, setMode] = useState(null);
  const [exercise, setExercise] = useState(exercises[0]);
  const [todaysPlan, setTodaysPlan] = useState(null);
  const [planLoading, setPlanLoading] = useState(false);
  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [completedSets, setCompletedSets] = useState(0);
  const [sessionSummaries, setSessionSummaries] = useState([]);
  const [activeTab, setActiveTab] = useState('exercise');
  const [targetReps, setTargetReps] = useState(null);
  const [restSeconds, setRestSeconds] = useState(0);
  const [isResting, setIsResting] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [doneScreen, setDoneScreen] = useState(false);
  const [saveError, setSaveError] = useState('');
  const [saveMessage, setSaveMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const { videoRef, canvasRef, isReady, error } = useWebcam({ width: 640, height: 480, enabled: mode !== null });
  const [sessionId] = useState(() => (window.crypto?.randomUUID ? window.crypto.randomUUID() : `session-${Math.random().toString(36).slice(2)}`));
  const [isRunning, setIsRunning] = useState(false);
  const [startedAt, setStartedAt] = useState(null);
  const { state, feedback, repCount, correctReps, incorrectReps, accuracy, isAnalysing, reset } = usePoseSession({
    exercise: mode === 'workout' ? (todaysPlan?.exercises?.[currentExerciseIndex]?.exercise || exercise) : exercise,
    sessionId,
    isRunning,
    canvasRef,
    videoRef,
  });

  const currentWorkoutExercise = mode === 'workout' ? todaysPlan?.exercises?.[currentExerciseIndex] : null;
  const workoutReady = mode === 'workout' && todaysPlan?.exercises?.length;

  useEffect(() => {
    async function loadTodaysPlan() {
      setPlanLoading(true);
      try {
        const response = await getPlan();
        const planData = response?.plan_data || response || {};
        const todayKey = new Date().toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase();
        const todayPlan = planData[todayKey];
        setTodaysPlan(todayPlan && !todayPlan.is_rest && todayPlan.exercises?.length ? todayPlan : null);
      } catch (apiError) {
        setTodaysPlan(null);
      } finally {
        setPlanLoading(false);
      }
    }

    loadTodaysPlan();
  }, []);

  useEffect(() => {
    if (mode === 'single') {
      setTargetReps(null);
      setCurrentExerciseIndex(0);
      setCompletedSets(0);
      setIsResting(false);
      setRestSeconds(0);
      return;
    }

    if (mode === 'workout' && todaysPlan?.exercises?.length) {
      const nextExercise = todaysPlan.exercises[currentExerciseIndex];
      setTargetReps(nextExercise?.reps ?? null);
      return;
    }

    if (mode === 'workout') {
      setTargetReps(null);
    }
  }, [mode, currentExerciseIndex, todaysPlan]);

  useEffect(() => {
    if (mode !== 'workout' || !isRunning || targetReps === null) {
      return undefined;
    }

    if (repCount >= targetReps) {
      const saveSummary = async () => {
        const exerciseName = todaysPlan?.exercises?.[currentExerciseIndex]?.exercise || exercise;
        const timeSpent = startedAt ? Math.max(1, Math.floor((Date.now() - startedAt) / 1000)) : 1;
        const nextSummary = {
          exercise: exerciseName,
          reps: targetReps,
          accuracy: Number(accuracy || 0),
          duration_seconds: timeSpent,
        };

        setIsRunning(false);
        setIsResting(true);
        setRestSeconds(60);
        setSessionSummaries((prev) => [...prev, nextSummary]);
        setCompletedSets((prev) => prev + 1);

        setTimeout(() => {
          saveSession({
            exercise_type: exerciseName,
            total_reps: targetReps,
            correct_reps: targetReps,
            incorrect_reps: 0,
            posture_accuracy: Number(accuracy || 0),
            duration_seconds: timeSpent,
          }).catch(() => {
            setSaveError('Unable to save the completed set.');
          });
        }, 2000);
      };

      saveSummary();
    }

    return undefined;
  }, [accuracy, currentExerciseIndex, exercise, isRunning, mode, repCount, startedAt, targetReps, todaysPlan]);

  useEffect(() => {
    if (!isResting || restSeconds <= 0) {
      return undefined;
    }

    const timer = window.setTimeout(() => {
      setRestSeconds((prev) => Math.max(0, prev - 1));
    }, 1000);

    return () => {
      window.clearTimeout(timer);
    };
  }, [isResting, restSeconds]);

  useEffect(() => {
    if (!isResting || restSeconds > 0) {
      return;
    }

    if (mode !== 'workout' || !todaysPlan?.exercises?.length) {
      return;
    }

    const exerciseCount = todaysPlan.exercises.length;
    const currentExercise = todaysPlan.exercises[currentExerciseIndex];
    if (!currentExercise) {
      return;
    }

    if (completedSets >= currentExercise.sets) {
      if (currentExerciseIndex + 1 < exerciseCount) {
        const nextIndex = currentExerciseIndex + 1;
        setCurrentExerciseIndex(nextIndex);
        setCompletedSets(0);
        setIsResting(false);
        setRestSeconds(0);
        setTargetReps(todaysPlan.exercises[nextIndex].reps);
        reset();
        setIsRunning(true);
      } else {
        setIsRunning(false);
        setIsResting(false);
        setRestSeconds(0);
        setDoneScreen(true);
      }
      return;
    }

    setIsResting(false);
    setRestSeconds(0);
    reset();
    setIsRunning(true);
  }, [completedSets, currentExerciseIndex, isResting, mode, restSeconds, reset, todaysPlan]);

  const duration = useMemo(() => {
    if (!startedAt) return '00:00';
    const seconds = Math.floor((Date.now() - startedAt) / 1000);
    const mins = String(Math.floor(seconds / 60)).padStart(2, '0');
    const secs = String(seconds % 60).padStart(2, '0');
    return `${mins}:${secs}`;
  }, [startedAt, isRunning]);

  const totalWorkoutReps = useMemo(
    () => sessionSummaries.reduce((sum, item) => sum + Number(item.reps || 0), 0),
    [sessionSummaries],
  );

  const averageAccuracy = useMemo(() => {
    if (!sessionSummaries.length) return 0;
    const total = sessionSummaries.reduce((sum, item) => sum + Number(item.accuracy || 0), 0);
    return Math.round(total / sessionSummaries.length);
  }, [sessionSummaries]);

  const handleStart = () => {
    setSaveError('');
    setSaveMessage('');
    setShowSummary(false);
    setStartedAt(Date.now());
    setIsRunning(true);
    setIsResting(false);
    setRestSeconds(0);
    reset();
  };

  const handleStop = () => {
    setIsRunning(false);
    setIsResting(false);
    setRestSeconds(0);
    if (mode === 'single') {
      setShowSummary(true);
    }
  };

  const handleSaveSingleSession = async () => {
    setSaveError('');
    setSaveMessage('');
    setLoading(true);
    try {
      await saveSession({
        exercise_type: exercise,
        total_reps: repCount,
        correct_reps: correctReps,
        incorrect_reps: incorrectReps,
        posture_accuracy: Number(accuracy || 0),
        duration_seconds: startedAt ? Math.max(1, Math.floor((Date.now() - startedAt) / 1000)) : 0,
      });
      setSaveMessage('Session saved successfully.');
    } catch (apiError) {
      setSaveError(apiError.response?.data?.detail || 'Unable to save session.');
    } finally {
      setLoading(false);
    }
  };

  const handleDiscard = () => {
    setIsRunning(false);
    setIsResting(false);
    setRestSeconds(0);
    setShowSummary(false);
    setStartedAt(null);
    setDoneScreen(false);
    reset();
  };

  const handleSkipRest = () => {
    if (!isResting) {
      return;
    }
    setIsResting(false);
    setRestSeconds(0);
  };

  if (mode === null) {
    return (
      <ModeSelector
        onSelectSingle={() => {
          setMode('single');
          setShowSummary(false);
          setDoneScreen(false);
        }}
        onSelectFullWorkout={() => {
          if (!todaysPlan?.exercises?.length) {
            return;
          }
          setMode('workout');
          setCurrentExerciseIndex(0);
          setCompletedSets(0);
          setSessionSummaries([]);
          setDoneScreen(false);
          setShowSummary(false);
        }}
        todaysPlan={todaysPlan}
        isLoading={planLoading}
      />
    );
  }

  const tabButtonBase = 'flex items-center justify-center gap-2 rounded-2xl px-4 py-3 text-sm font-semibold transition md:px-6';

  return (
    <div className="mx-auto w-full max-w-5xl space-y-5 pb-10">
      {error ? <AlertBanner type="error" message={error} onDismiss={() => {}} /> : null}

      {mode === 'workout' && workoutReady ? (
        <WorkoutProgress exercises={todaysPlan.exercises} currentIndex={currentExerciseIndex} completedSets={completedSets} />
      ) : null}

      <div className="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-sm">
        <div className="relative overflow-hidden bg-black">
          {mode !== null ? (
            <>
              <video
                ref={videoRef}
                autoPlay
                muted
                playsInline
                className="aspect-video w-full bg-black object-cover"
              />
              <canvas className="pointer-events-none absolute inset-0 hidden" width="640" height="480" />
            </>
          ) : null}
        </div>

        <div className="border-t border-slate-200 bg-slate-50">
          <FeedbackPanel
            feedback={feedback || 'Looking good! Keep it up.'}
            state={state || 'REST'}
            repCount={mode === 'workout' ? repCount : repCount}
            targetReps={targetReps}
            accuracy={Number(accuracy || 0)}
          />
        </div>

        <div className="grid gap-3 border-t border-slate-200 bg-white p-3 md:grid-cols-2">
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'exercise'}
            className={`${tabButtonBase} ${activeTab === 'exercise' ? 'bg-primary text-white' : 'border border-slate-200 bg-white text-slate-700'}`}
            onClick={() => setActiveTab('exercise')}
          >
            <Play className="h-4 w-4" />
            Start exercise
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'instructions'}
            className={`${tabButtonBase} ${activeTab === 'instructions' ? 'bg-primary text-white' : 'border border-slate-200 bg-white text-slate-700'}`}
            onClick={() => setActiveTab('instructions')}
          >
            <HelpCircle className="h-4 w-4" />
            How to do it
          </button>
        </div>

        {activeTab === 'exercise' ? (
          <div className="space-y-5 bg-slate-50 p-4 sm:p-5">
            {mode === 'single' ? (
              <label className="block text-sm font-medium text-slate-700">
                Exercise
                <select
                  value={exercise}
                  onChange={(e) => setExercise(e.target.value)}
                  disabled={isRunning}
                  className="mt-2 block w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-slate-900 outline-none focus:border-primary"
                >
                  {exercises.map((option) => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </label>
            ) : null}

            <div className="flex flex-wrap gap-3">
              <Button variant="primary" onClick={handleStart} disabled={!isReady || isRunning || (mode === 'workout' && isResting)}>
                {mode === 'workout' ? 'Start set' : 'Start session'}
              </Button>
              <Button variant="danger" onClick={handleStop} disabled={!isRunning && !isResting}>
                {mode === 'workout' ? 'Pause workout' : 'Stop session'}
              </Button>
              {mode === 'workout' && isResting ? (
                <Button variant="secondary" onClick={handleSkipRest} className="gap-2">
                  <TimerReset className="h-4 w-4" />
                  Skip rest
                </Button>
              ) : null}
            </div>

            {isResting ? (
              <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-800">
                Rest: {restSeconds}s
              </div>
            ) : null}

            {showSummary ? (
              <div className="rounded-3xl bg-white p-4 shadow-sm">
                <h3 className="text-lg font-semibold text-slate-900">Session summary</h3>
                <div className="mt-4 grid gap-3 sm:grid-cols-3">
                  <div className="rounded-2xl bg-slate-50 p-3">
                    <div className="text-xs uppercase tracking-[0.15em] text-slate-500">Exercise</div>
                    <div className="mt-2 font-semibold text-slate-900">{exercise}</div>
                  </div>
                  <div className="rounded-2xl bg-slate-50 p-3">
                    <div className="text-xs uppercase tracking-[0.15em] text-slate-500">Total reps</div>
                    <div className="mt-2 font-semibold text-slate-900">{repCount}</div>
                  </div>
                  <div className="rounded-2xl bg-slate-50 p-3">
                    <div className="text-xs uppercase tracking-[0.15em] text-slate-500">Accuracy</div>
                    <div className="mt-2 font-semibold text-slate-900">{Math.round(Number(accuracy || 0))}%</div>
                  </div>
                </div>
                <div className="mt-5 flex flex-wrap gap-3">
                  <Button onClick={handleSaveSingleSession} loading={loading}>Save session</Button>
                  <Button variant="secondary" onClick={handleDiscard}>Discard</Button>
                  {saveMessage ? <p className="text-sm text-emerald-700">{saveMessage}</p> : null}
                  {saveError ? <p className="text-sm text-rose-700">{saveError}</p> : null}
                </div>
              </div>
            ) : null}

            {doneScreen ? (
              <div className="rounded-3xl bg-white p-5 shadow-sm">
                <h3 className="text-2xl font-semibold text-slate-900">Workout complete! 🎉</h3>
                <div className="mt-4 overflow-hidden rounded-2xl border border-slate-200">
                  <table className="min-w-full text-left text-sm text-slate-700">
                    <thead className="bg-slate-100 text-slate-800">
                      <tr>
                        <th className="px-4 py-3 font-semibold">Exercise</th>
                        <th className="px-4 py-3 font-semibold">Reps</th>
                        <th className="px-4 py-3 font-semibold">Accuracy</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sessionSummaries.map((item) => (
                        <tr key={`${item.exercise}-${item.reps}-${item.accuracy}`} className="border-t border-slate-200">
                          <td className="px-4 py-3">{item.exercise}</td>
                          <td className="px-4 py-3">{item.reps}</td>
                          <td className="px-4 py-3">{Math.round(Number(item.accuracy || 0))}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-slate-600">
                  <span>Total reps: <strong className="text-slate-900">{totalWorkoutReps}</strong></span>
                  <span>Avg accuracy: <strong className="text-slate-900">{averageAccuracy}%</strong></span>
                </div>
                <div className="mt-5 flex gap-3">
                  <Button onClick={() => navigate('/dashboard')}>View dashboard</Button>
                  <Button variant="secondary" onClick={handleDiscard}>Restart</Button>
                </div>
              </div>
            ) : null}
          </div>
        ) : null}

        {activeTab === 'instructions' ? (
          <div className="bg-slate-50 p-4 sm:p-5">
            <ExerciseInstructions exercise={mode === 'workout' ? currentWorkoutExercise?.exercise || exercise : exercise} />
          </div>
        ) : null}
      </div>
    </div>
  );
}
