/**
 * Displays a day card for the workout plan grid.
 */
import React from 'react';
import ExerciseEntry from './ExerciseEntry.jsx';

/**
 * @param {{ dayName: string, plan: { is_rest: boolean, exercises?: Array<{ exercise: string, sets: number, reps: number, notes: string }> }, isToday?: boolean }} props
 */
export default function DayCard({ dayName, plan, isToday = false }) {
  return (
    <div className={`rounded-3xl border p-5 ${isToday ? 'border-primary shadow-lg' : 'border-slate-200'} ${plan?.is_rest ? 'bg-slate-50' : 'bg-white'}`}>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900">{dayName}</h3>
        <span className="text-sm text-slate-500">{plan?.is_rest ? 'Rest day' : 'Workout'}</span>
      </div>
      {plan?.is_rest ? (
        <p className="rounded-2xl bg-slate-100 p-4 text-sm text-slate-600">Rest & recover</p>
      ) : (
        <div className="space-y-3">
          {plan?.exercises?.map((item) => (
            <ExerciseEntry key={item.exercise} exercise={item.exercise} sets={item.sets} reps={item.reps} notes={item.notes} />
          ))}
        </div>
      )}
    </div>
  );
}
