/** Full monthly calendar with workout details for the selected date. */
import React, { useMemo, useState } from 'react';

function dateKey(value) {
  if (!value) return '';
  return typeof value === 'string' ? value.slice(0, 10) : value.toISOString().slice(0, 10);
}

/** @param {{ sessions?: Array<object>, goalValue?: number, goalTarget?: number, expanded?: boolean, onSeeDetails?: () => void }} props */
export default function WeeklySessionsChart({ sessions = [], goalValue = 0, goalTarget = 4, expanded = false, onSeeDetails }) {
  const today = new Date();
  const [visibleMonth, setVisibleMonth] = useState(new Date(today.getFullYear(), today.getMonth(), 1));
  const [selectedDate, setSelectedDate] = useState(dateKey(today));

  const sessionsByDate = useMemo(() => {
    const grouped = new Map();
    sessions.forEach((session) => {
      const key = dateKey(session.created_at || session.date);
      if (!key) return;
      grouped.set(key, [...(grouped.get(key) || []), session]);
    });
    return grouped;
  }, [sessions]);

  const calendarDays = useMemo(() => {
    const firstDay = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth(), 1);
    const daysInMonth = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth() + 1, 0).getDate();
    const days = Array.from({ length: firstDay.getDay() }, () => null);

    for (let dayNumber = 1; dayNumber <= daysInMonth; dayNumber += 1) {
      const date = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth(), dayNumber);
      const key = dateKey(date);
      days.push({ date, key, dayNumber, workouts: sessionsByDate.get(key) || [], isToday: key === dateKey(today) });
    }

    while (days.length % 7 !== 0) days.push(null);
    return days;
  }, [sessionsByDate, today, visibleMonth]);

  const selectedWorkouts = sessionsByDate.get(selectedDate) || [];
  const selectedDateLabel = new Date(`${selectedDate}T12:00:00`).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  const completedGoal = Math.min(goalValue, goalTarget);
  const weeklyDays = Array.from({ length: 7 }, (_, offset) => {
    const date = new Date(today);
    date.setDate(today.getDate() - (6 - offset));
    const key = dateKey(date);
    return { key, label: date.toLocaleDateString('en-US', { weekday: 'short' }), dayNumber: date.getDate(), workouts: sessionsByDate.get(key) || [], isToday: key === dateKey(today) };
  });

  function moveMonth(offset) {
    const nextMonth = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth() + offset, 1);
    setVisibleMonth(nextMonth);
    setSelectedDate(dateKey(nextMonth));
  }

  return (
    <div className="rounded-2xl bg-white p-4 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Training calendar</p>
          <h2 className="mt-1 text-lg font-semibold text-slate-900">{expanded ? visibleMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) : 'Weekly sessions'}</h2>
        </div>
        {expanded ? (
          <div className="flex items-center gap-2">
            <button type="button" onClick={() => moveMonth(-1)} aria-label="Previous month" className="h-10 w-10 rounded-full bg-white text-xl text-slate-700 shadow-sm transition hover:bg-blue-50">‹</button>
            <button type="button" onClick={() => moveMonth(1)} aria-label="Next month" className="h-10 w-10 rounded-full bg-white text-xl text-slate-700 shadow-sm transition hover:bg-blue-50">›</button>
          </div>
        ) : null}
      </div>

      <div className="mt-5 flex items-center justify-between border-b border-slate-200 pb-4">
        <span className="text-sm font-medium text-slate-500">Weekly goal</span>
        <span className="text-2xl font-black text-blue-600">{completedGoal}<span className="font-medium text-slate-400"> / {goalTarget}</span></span>
      </div>

      {!expanded ? (
        <>
          <div className="mt-5 grid grid-cols-7 gap-1 text-center sm:gap-2">
            {weeklyDays.map((day) => (
              <div key={day.key} className="flex min-w-0 flex-col items-center gap-2">
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">{day.label}</span>
                <span className={[
                  'flex h-10 w-10 items-center justify-center rounded-full border text-sm font-semibold',
                  day.isToday ? 'border-2 border-blue-500 bg-blue-50 text-blue-700' : day.workouts.length ? 'border-blue-200 bg-blue-50 text-blue-600' : 'border-slate-200 text-slate-500',
                ].join(' ')}>{day.dayNumber}</span>
                <span className={day.workouts.length ? 'h-1.5 w-1.5 rounded-full bg-blue-600' : 'h-1.5 w-1.5'} />
              </div>
            ))}
          </div>
          <button type="button" onClick={onSeeDetails} className="mt-5 w-full rounded-xl bg-white py-3 text-sm font-semibold text-blue-600 transition hover:bg-blue-50">
            See details
          </button>
        </>
      ) : null}

      {expanded ? (
        <>
      <div className="mt-5 grid grid-cols-7 gap-1 text-center text-xs font-semibold uppercase tracking-wide text-slate-400 sm:gap-2">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((label) => <span key={label}>{label}</span>)}
      </div>

      <div className="mt-2 grid grid-cols-7 gap-1 sm:gap-2">
        {calendarDays.map((day, index) => day ? (
          <button type="button" key={day.key} onClick={() => setSelectedDate(day.key)} className={[
            'relative flex min-h-14 flex-col items-center justify-center rounded-2xl border text-sm transition sm:min-h-20',
            selectedDate === day.key ? 'border-blue-500 bg-blue-50 text-blue-700 shadow-[0_0_0_3px_rgba(59,130,246,0.12)]' : 'border-transparent bg-white/70 text-slate-700 hover:border-blue-200 hover:bg-white',
            day.isToday ? 'font-bold' : '',
          ].join(' ')}>
            <span>{day.dayNumber}</span>
            {day.workouts.length > 0 ? <span className="mt-1 h-2 w-2 rounded-full bg-blue-600" aria-label={`${day.workouts.length} workout${day.workouts.length > 1 ? 's' : ''}`} /> : <span className="mt-1 h-2 w-2" />}
          </button>
        ) : <span key={`empty-${index}`} className="min-h-14 sm:min-h-20" />)}
      </div>

      <div className="mt-6 rounded-2xl bg-white p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="font-bold text-slate-900">{selectedDateLabel}</h3>
          <span className="text-sm text-slate-500">{selectedWorkouts.length} workout{selectedWorkouts.length === 1 ? '' : 's'}</span>
        </div>
        {selectedWorkouts.length > 0 ? (
          <div className="mt-3 grid gap-2 sm:grid-cols-2">
            {selectedWorkouts.map((workout) => (
              <div key={workout.id} className="rounded-xl bg-slate-50 p-3">
                <p className="font-semibold capitalize text-slate-900">{String(workout.exercise_type || 'Workout').replaceAll('_', ' ')}</p>
                <p className="mt-1 text-sm text-slate-500">{workout.total_reps ?? 0} reps · {workout.posture_accuracy ?? 0}% accuracy</p>
              </div>
            ))}
          </div>
        ) : <p className="mt-3 text-sm text-slate-500">No workout logged for this date.</p>}
      </div>
      <button type="button" onClick={onSeeDetails} className="mt-4 text-sm font-semibold text-blue-600 hover:text-blue-700">Hide calendar details</button>
        </>
      ) : null}
    </div>
  );
}
