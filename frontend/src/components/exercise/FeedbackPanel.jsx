/**
 * Exercise feedback and progress summary panel.
 */
import React from 'react';

/**
 * @param {{ feedback: string, state: string, repCount: number, targetReps: number | null, accuracy: number }} props
 */
export default function FeedbackPanel({ feedback = '', state = 'REST', repCount = 0, targetReps = null, accuracy = 0 }) {
  const stateClassMap = {
    REST: 'bg-slate-200 text-slate-700',
    TRANSITION: 'bg-amber-100 text-amber-800',
    COMPLETE: 'bg-emerald-100 text-emerald-800',
  };

  const accuracyClass = accuracy >= 80 ? 'text-emerald-600' : accuracy >= 60 ? 'text-amber-600' : 'text-rose-600';
  const progressPercent = targetReps ? Math.min((repCount / targetReps) * 100, 100) : 0;
  const targetReached = targetReps !== null && repCount >= targetReps;

  return (
    <div className="w-full rounded-3xl border border-slate-200 bg-slate-50 p-4 shadow-sm sm:p-5">
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-2xl bg-white px-3 py-2">
          <div className="text-[11px] font-medium uppercase tracking-[0.15em] text-slate-500">Reps</div>
          <div className={`mt-1 text-lg font-semibold ${targetReached && targetReps !== null ? 'text-emerald-600' : 'text-slate-900'}`}>
            {targetReps !== null ? `${repCount} / ${targetReps}` : String(repCount)}
          </div>
        </div>

        <div className="rounded-2xl bg-white px-3 py-2">
          <div className="text-[11px] font-medium uppercase tracking-[0.15em] text-slate-500">State</div>
          <div className={`mt-1 inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${stateClassMap[state] || 'bg-slate-200 text-slate-700'}`}>
            {state}
          </div>
        </div>

        <div className="rounded-2xl bg-white px-3 py-2">
          <div className="text-[11px] font-medium uppercase tracking-[0.15em] text-slate-500">Accuracy</div>
          <div className={`mt-1 text-lg font-semibold ${accuracyClass}`}>{accuracy}%</div>
        </div>
      </div>

      <div className={`mt-4 rounded-2xl px-4 py-3 text-center text-sm italic ${feedback ? 'bg-amber-50 text-slate-700' : 'bg-slate-100 text-slate-600'}`}>
        {feedback || 'Looking good! Keep it up.'}
      </div>

      {targetReps !== null ? (
        <div className="mt-4">
          <div className="mb-2 flex items-center justify-between text-xs font-medium text-slate-600">
            <span>Progress</span>
            {targetReached ? <span className="text-emerald-700">Target reached!</span> : null}
          </div>

          <div className="h-3 overflow-hidden rounded-full bg-slate-200">
            <div
              className={`h-full rounded-full transition-all duration-300 ${targetReached ? 'bg-emerald-500' : 'bg-emerald-400'}`}
              style={{ width: `${progressPercent}%` }}
            />
          </div>

          <div className="mt-2 text-right text-xs font-medium text-slate-600">
            {repCount} / {targetReps}
          </div>
        </div>
      ) : null}
    </div>
  );
}
