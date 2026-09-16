/**
 * Displays a day card for the workout plan grid.
 */
import React from 'react';
import { Check } from 'lucide-react';
import ExerciseEntry from './ExerciseEntry.jsx';

/**
 * @param {{ dayName: string, plan: { is_rest: boolean, exercises?: Array<{ exercise: string, sets: number, reps: number, notes: string }> }, isToday?: boolean }} props
 */
export default function DayCard({ dayName, plan, isToday = false, completed = false }) {
  return (
    <div className={`self-start rounded-3xl border p-4 ${isToday ? 'border-primary shadow-lg' : 'border-slate-200'} ${plan?.is_rest ? 'bg-slate-50' : 'bg-white'}`}>
      <div className="mb-3 flex items-center justify-between gap-2 xl:flex-col xl:items-start">
        <h3 className="text-base font-semibold leading-tight text-slate-900">{dayName}</h3>
        <span className={`inline-flex shrink-0 whitespace-nowrap items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold ${plan?.is_rest ? 'bg-slate-200 text-slate-600' : completed ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'}`}>
          {completed ? <Check className="h-3 w-3" /> : null}{plan?.is_rest ? 'Rest day' : completed ? 'Completed' : 'Workout'}
        </span>
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
