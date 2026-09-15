/**
 * Workout plan page showing a full week of scheduled exercises.
 */
import React, { useEffect, useMemo, useState } from 'react';
import { getPlan, refreshPlan } from '../api/recommendations.js';
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

  useEffect(() => {
    async function loadPlan() {
      setError('');
      try {
        const data = await getPlan();
        setPlan(normalizePlan(data));
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

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <div className="rounded-3xl bg-white p-8 shadow-sm"><p className="text-center text-danger">{error}</p></div>;
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
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {plan?.days?.map((day, index) => (
          <DayCard
            key={day.name}
            dayName={weekdays[index] || day.name}
            plan={day}
            isToday={index === todayIndex}
          />
        ))}
      </div>
    </div>
  );
}
