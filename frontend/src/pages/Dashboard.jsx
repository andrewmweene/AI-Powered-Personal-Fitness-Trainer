/**
 * Dashboard page displaying analytics and recent sessions.
 */
import React, { useEffect, useState } from 'react';
import { getSummary, getWeekly, getByExercise, getTrend } from '../api/analytics.js';
import { getSessions } from '../api/sessions.js';
import LoadingSpinner from '../components/ui/LoadingSpinner.jsx';
import MetricCard from '../components/ui/MetricCard.jsx';
import AccuracyTrendChart from '../components/charts/AccuracyTrendChart.jsx';
import WeeklySessionsChart from '../components/charts/WeeklySessionsChart.jsx';
import ExerciseBreakdownChart from '../components/charts/ExerciseBreakdownChart.jsx';
import AccuracyGauge from '../components/charts/AccuracyGauge.jsx';

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [weekly, setWeekly] = useState([]);
  const [byExercise, setByExercise] = useState([]);
  const [trend, setTrend] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadData() {
      setError('');
      setLoading(true);
      try {
        const [summaryData, weeklyData, exerciseData, trendData, sessionData] = await Promise.all([
          getSummary(),
          getWeekly(),
          getByExercise(),
          getTrend(),
          getSessions(),
        ]);
        setSummary(summaryData);
        setWeekly(weeklyData);
        setByExercise(exerciseData);
        setTrend(trendData);
        setSessions(sessionData.slice(0, 10));
      } catch (apiError) {
        setError(apiError.response?.data?.detail || 'Failed to load analytics data.');
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <div className="rounded-3xl bg-white p-8 shadow-sm"><p className="text-center text-danger">{error}</p></div>;
  }

  return (
    <div className="space-y-8">
      <div className="grid gap-4 md:grid-cols-4">
        <MetricCard label="Total sessions" value={summary?.total_sessions ?? 0} />
        <MetricCard label="Total reps" value={summary?.total_reps ?? 0} />
        <MetricCard label="Avg accuracy" value={`${summary?.avg_accuracy ?? 0}%`} />
        <MetricCard label="Current streak" value={`${summary?.current_streak_days ?? 0} days`} />
      </div>
      <div className="grid gap-4 xl:grid-cols-2">
        <AccuracyTrendChart data={trend || []} />
        <WeeklySessionsChart data={weekly || []} />
      </div>
      <ExerciseBreakdownChart data={byExercise || []} />
      <div className="grid gap-4 xl:grid-cols-2">
        <AccuracyGauge value={summary?.avg_accuracy ?? 0} />
        <div className="rounded-3xl bg-white p-4 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-slate-900">Recent sessions</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full border-separate border-spacing-y-2 text-left text-sm">
              <thead className="bg-slate-100 text-slate-700">
                <tr>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Exercise</th>
                  <th className="px-4 py-3">Reps</th>
                  <th className="px-4 py-3">Correct</th>
                  <th className="px-4 py-3">Accuracy</th>
                  <th className="px-4 py-3">Duration</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((session, index) => (
                  <tr key={`${session.id}-${index}`} className={index % 2 === 0 ? 'bg-slate-50' : ''}>
                    <td className="px-4 py-3">{new Date(session.created_at || session.date || Date.now()).toLocaleDateString()}</td>
                    <td className="px-4 py-3">{session.exercise_type}</td>
                    <td className="px-4 py-3">{session.total_reps}</td>
                    <td className="px-4 py-3">{session.correct_reps}</td>
                    <td className="px-4 py-3">{session.posture_accuracy ?? 0}%</td>
                    <td className="px-4 py-3">{session.duration_seconds ? `${Math.floor(session.duration_seconds / 60)}m ${session.duration_seconds % 60}s` : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
