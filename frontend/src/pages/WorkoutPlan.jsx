/**
 * Workout plan page showing a full week of scheduled exercises.
 */
import React, { useEffect, useMemo, useState } from 'react';
import { getPlan, refreshPlan } from '../api/recommendations.js';
import { getSessions } from '../api/sessions.js';
import LoadingSpinner from '../components/ui/LoadingSpinner.jsx';
import Button from '../components/ui/Button.jsx';
import DayCard from '../components/workout/DayCard.jsx';

const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

function normalizePlan(response) {
  const planData = response?.plan_data || response || {};
  const days = weekdays.map((name) => ({
    name,
    ...(planData[name.toLowerCase()] || { is_rest: true, exercises: [] }),
  }));
  return { ...planData, days, week_start_date: response?.week_start_date || planData.week_start_date };
}

function formatWeekStart(value) {
  if (!value) return 'this week';
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? 'this week' : parsed.toLocaleDateString();
}

export default function WorkoutPlan() {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    async function loadPlan() {
      setError('');
      try {
        const [data, sessionData] = await Promise.all([getPlan(), getSessions()]);
        setPlan(normalizePlan(data));
        setSessions(sessionData);
      } catch (apiError) {
        setError(apiError.response?.data?.detail || 'Unable to load workout plan.');
      } finally {
        setLoading(false);
      }
    }

    loadPlan();
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    setError('');
    try {
      const refreshed = await refreshPlan();
      setPlan(normalizePlan(refreshed));
    } catch (apiError) {
      setError(apiError.response?.data?.detail || 'Unable to refresh plan.');
    } finally {
      setRefreshing(false);
    }
  };

  const todayIndex = useMemo(() => (new Date().getDay() + 6) % 7, []);
  const completedDays = useMemo(() => {
    const start = plan?.week_start_date ? new Date(`${plan.week_start_date}T12:00:00`) : null;
    return new Set((sessions || []).filter((session) => {
      if (!start || !session.created_at) return false;
      const date = new Date(session.created_at);
      const offset = Math.floor((date - start) / 86400000);
      return offset >= 0 && offset < 7;
    }).map((session) => {
      const date = new Date(session.created_at);
      return Math.floor((date - start) / 86400000);
    }));
  }, [plan, sessions]);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <div className="rounded-3xl bg-white p-8 shadow-sm"><p className="text-center text-danger">{error}</p></div>;
  }

  if (!plan?.days?.length) {
    return (
      <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-10 text-center shadow-sm">
        <h2 className="text-2xl font-semibold text-slate-900">No plan available yet</h2>
        <p className="mt-3 text-slate-600">Generate your weekly workout plan after onboarding or refresh once your profile is complete.</p>
        <div className="mt-6 flex justify-center">
          <Button variant="primary" onClick={handleRefresh} loading={refreshing}>Generate plan</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">Your workout plan — week of {formatWeekStart(plan?.week_start_date)}</h1>
          <p className="mt-2 text-sm text-slate-600">{plan?.generated_by === 'static_library' ? 'Matched to your onboarding profile' : 'AI-generated based on your performance'}</p>
        </div>
        <Button variant="primary" onClick={handleRefresh} loading={refreshing}>Refresh plan</Button>
      </div>
      <div className="grid items-start gap-3 sm:grid-cols-2 md:grid-cols-4 xl:grid-cols-7">
        {plan?.days?.map((day, index) => (
          <DayCard
            key={day.name}
            dayName={weekdays[index] || day.name}
            plan={day}
            isToday={index === todayIndex}
            completed={!day.is_rest && completedDays.has(index)}
          />
        ))}
      </div>
    </div>
  );
}
