/**
 * Clear exercise summary showing session volume separately from posture accuracy.
 */
import React from 'react';

function getAccuracyStyle(avgAccuracy) {
  if (avgAccuracy >= 80) return { label: 'Good form', bar: 'bg-emerald-500', text: 'text-emerald-700' };
  if (avgAccuracy >= 60) return { label: 'Keep improving', bar: 'bg-amber-400', text: 'text-amber-700' };
  return { label: 'Needs attention', bar: 'bg-rose-500', text: 'text-rose-700' };
}

/**
 * @param {{ data: Array<{ exercise: string, count: number, avg_accuracy: number }> }} props
 */
export default function ExerciseBreakdownChart({ data }) {
  const maxCount = Math.max(...data.map((entry) => entry.count || 0), 1);

  return (
    <div className="rounded-2xl bg-white p-4 shadow-sm">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Exercise breakdown</h2>
          <p className="mt-1 text-sm text-slate-500">How often you train and how accurate your form is.</p>
        </div>
        <div className="hidden text-right text-xs text-slate-400 sm:block">
          <p>Sessions</p>
          <p className="mt-3">Accuracy</p>
        </div>
      </div>

      {data.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center text-sm text-slate-500">
          Exercise performance will appear after your first workout.
        </div>
      ) : (
        <div className="space-y-5">
          {data.map((entry) => {
            const accuracy = Math.round(Number(entry.avg_accuracy) || 0);
            const style = getAccuracyStyle(accuracy);
            const count = Number(entry.count) || 0;

            return (
              <div key={entry.exercise} className="grid gap-2 sm:grid-cols-[150px_1fr_90px] sm:items-center">
                <div className="flex items-center justify-between gap-3 sm:block">
                  <p className="font-semibold capitalize text-slate-900">{String(entry.exercise).replaceAll('_', ' ')}</p>
                  <span className="text-sm text-slate-500 sm:hidden">{count} {count === 1 ? 'session' : 'sessions'}</span>
                </div>

                <div className="space-y-2">
                  <div className="h-2 overflow-hidden rounded-full bg-slate-100" aria-label={`${count} sessions`}>
                    <div className="h-full rounded-full bg-blue-500" style={{ width: `${(count / maxCount) * 100}%` }} />
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100" aria-label={`${accuracy}% posture accuracy`}>
                      <div className={`h-full rounded-full ${style.bar}`} style={{ width: `${Math.min(accuracy, 100)}%` }} />
                    </div>
                    <span className={`w-10 text-right text-sm font-semibold ${style.text}`}>{accuracy}%</span>
                  </div>
                </div>

                <div className="hidden text-right sm:block">
                  <p className="font-semibold text-slate-900">{count}</p>
                  <p className={`mt-2 text-xs font-medium ${style.text}`}>{style.label}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <div className="mt-5 flex flex-wrap gap-4 border-t border-slate-100 pt-4 text-xs text-slate-500">
        <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-blue-500" /> Sessions completed</span>
        <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-emerald-500" /> 80%+ accuracy</span>
      </div>
    </div>
  );
}
