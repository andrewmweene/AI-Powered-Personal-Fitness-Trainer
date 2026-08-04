/**
 * Displays a single exercise line item.
 */
import React from 'react';

/**
 * @param {{ exercise: string, sets: number, reps: number, notes: string }} props
 */
export default function ExerciseEntry({ exercise, sets, reps, notes }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <p className="font-semibold text-slate-900">{exercise}</p>
      <p className="mt-1 text-sm text-slate-600">{sets} sets × {reps} reps</p>
      <p className="mt-2 text-sm italic text-slate-500">{notes}</p>
    </div>
  );
}
