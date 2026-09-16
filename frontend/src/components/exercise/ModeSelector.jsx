/**
 * Workout mode selection prompt.
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { CalendarDays, Dumbbell, LoaderCircle } from 'lucide-react';

/**
 * @param {{ onSelectSingle: () => void, onSelectFullWorkout: () => void, todaysPlan: object | null, isLoading: boolean }} props
 */
export default function ModeSelector({ onSelectSingle, onSelectFullWorkout, todaysPlan, isLoading }) {
  const isRestDay = !todaysPlan || todaysPlan.is_rest || !todaysPlan.exercises?.length;
  const preview = todaysPlan?.exercises?.map((exercise) => exercise.exercise).slice(0, 3) || [];

  return (
    <div className="flex min-h-[70vh] items-center justify-center px-3 py-8">
      <div className="w-full max-w-3xl rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="text-center">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">Workout mode</p>
          <h2 className="mt-3 text-3xl font-semibold text-slate-900">How would you like to train today?</h2>
          <p className="mt-2 text-base text-slate-600">Choose your workout mode</p>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-2">
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-2xl bg-primary/10 text-primary">
              <Dumbbell className="h-5 w-5" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900">Single exercise</h3>
            <p className="mt-2 text-sm text-slate-600">Pick one exercise and do it at your own pace</p>
            <button
              type="button"
              onClick={onSelectSingle}
              className="mt-6 inline-flex w-full items-center justify-center rounded-full bg-primary px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-600"
            >
              Choose exercise →
            </button>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-2xl bg-primary/10 text-primary">
              <CalendarDays className="h-5 w-5" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900">Full workout session</h3>
            <p className="mt-2 text-sm text-slate-600">Follow today&apos;s plan from start to finish</p>

            {isLoading ? (
              <div className="mt-4 flex items-center gap-2 text-sm text-slate-500">
                <LoaderCircle className="h-4 w-4 animate-spin" />
                Loading plan...
              </div>
            ) : null}

            {!isLoading && isRestDay ? (
              <p className="mt-4 text-sm text-slate-500">Today is a rest day in your plan</p>
            ) : null}

            {!isLoading && !isRestDay && preview.length ? (
              <div className="mt-4 flex flex-wrap gap-2">
                {preview.map((item, index) => (
                  <span key={`${item}-${index}`} className="rounded-full bg-white px-2.5 py-1 text-xs font-medium text-slate-700 ring-1 ring-slate-200">
                    {item}
                  </span>
                ))}
              </div>
            ) : null}

            <button
              type="button"
              onClick={onSelectFullWorkout}
              disabled={isLoading || isRestDay}
              className={`mt-6 inline-flex w-full items-center justify-center rounded-full px-4 py-3 text-sm font-semibold transition ${
                isLoading || isRestDay
                  ? 'cursor-not-allowed border border-slate-300 bg-slate-300 text-slate-600'
                  : 'bg-primary text-white hover:bg-blue-600'
              }`}
            >
              Start full workout →
            </button>
          </div>
        </div>

        <div className="mt-8 text-center">
          <Link to="/plan" className="inline-flex items-center rounded-full bg-blue-50 px-5 py-2.5 text-sm font-semibold text-primary transition hover:bg-blue-100 hover:text-blue-700">
            Set up my plan →
          </Link>
        </div>
      </div>
    </div>
  );
}
