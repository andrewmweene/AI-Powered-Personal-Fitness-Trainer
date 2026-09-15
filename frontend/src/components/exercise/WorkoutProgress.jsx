/**
 * Shows progress through the current workout plan.
 */
import React from 'react';
import { Check, Circle, ArrowRight } from 'lucide-react';

/**
 * @param {{ exercises: Array<{exercise:string, sets:number, reps:number, notes:string}>, currentIndex: number, completedSets: number }} props
 */
export default function WorkoutProgress({ exercises = [], currentIndex = 0, completedSets = 0 }) {
  const currentExercise = exercises[currentIndex] || null;

  return (
    <div className="w-full rounded-3xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
      <div className="flex flex-wrap gap-2">
        {exercises.map((exercise, index) => {
          const isCompleted = index < currentIndex;
          const isCurrent = index === currentIndex;

          return (
            <div
              key={`${exercise.exercise}-${index}`}
              className={`inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm font-medium transition ${
                isCompleted
                  ? 'bg-emerald-100 text-emerald-800'
                  : isCurrent
                    ? 'bg-primary text-white shadow-sm'
                    : 'bg-slate-100 text-slate-500'
              }`}
            >
              {isCompleted ? <Check className="h-4 w-4" /> : isCurrent ? <Circle className="h-3 w-3 fill-current" /> : null}
              <span>{exercise.exercise}</span>
            </div>
          );
        })}
      </div>

      {currentExercise ? (
        <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm text-slate-600">
            <span className="font-semibold text-slate-900">Exercise {currentIndex + 1} of {exercises.length}</span>
            <span className="mx-2 text-slate-400">•</span>
            <span>Set {completedSets + 1} of {currentExercise.sets}</span>
            <span className="mx-2 text-slate-400">•</span>
            <span>{currentExercise.reps} reps target</span>
          </div>

          {completedSets >= currentExercise.sets ? (
            <button type="button" className="inline-flex items-center gap-2 rounded-full bg-primary px-3 py-2 text-sm font-semibold text-white">
              Next exercise <ArrowRight className="h-4 w-4" />
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
