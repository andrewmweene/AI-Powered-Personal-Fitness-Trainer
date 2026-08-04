/**
 * Workout plan page showing a full week of scheduled exercises.
 */
import React, { useEffect, useMemo, useState } from 'react';
import { getPlan, refreshPlan } from '../api/recommendations.js';
import LoadingSpinner from '../components/ui/LoadingSpinner.jsx';
import Button from '../components/ui/Button.jsx';
import DayCard from '../components/workout/DayCard.jsx';

const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

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
        setPlan(data);
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
      setPlan(refreshed);
    } catch (apiError) {
      setError(apiError.response?.data?.detail || 'Unable to refresh plan.');
    } finally {
      setRefreshing(false);
    }
  };

  const todayIndex = useMemo(() => new Date().getDay() - 1, []);

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
          <h1 className="text-3xl font-semibold text-slate-900">Your workout plan — week of {new Date(plan?.week_start_date).toLocaleDateString()}</h1>
          <p className="mt-2 text-sm text-slate-600">{plan?.generated_by ? 'Matched to your profile' : 'AI-generated plan'}</p>
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
