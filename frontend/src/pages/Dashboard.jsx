/**
 * Dashboard page displaying analytics and recent sessions.
 */
import React, { useEffect, useState } from 'react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { getSummary, getWeekly, getByExercise, getTrend } from '../api/analytics.js';
import { getProfile } from '../api/onboarding.js';
import { getMeasurements } from '../api/measurements.js';
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
  const [profile, setProfile] = useState(null);
  const [measurements, setMeasurements] = useState([]);
  const [showCalendarDetails, setShowCalendarDetails] = useState(false);
  const [showBmiLog, setShowBmiLog] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const bmiCategory = profile?.bmi !== undefined && profile?.bmi !== null
    ? profile.bmi < 18.5
      ? { label: 'Underweight', color: '#60a5fa' }
      : profile.bmi < 25
        ? { label: 'Healthy weight', color: '#2dd4bf' }
        : profile.bmi < 30
          ? { label: 'Overweight', color: '#fbbf24' }
          : { label: 'Obese', color: '#f87171' }
    : { label: 'No data', color: '#cbd5e1' };

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

        let profileData = null;
        let measurementData = [];
        try {
          [profileData, measurementData] = await Promise.all([getProfile(), getMeasurements()]);
        } catch (profileError) {
          profileData = null;
          measurementData = [];
        }

        setSummary(summaryData);
        setWeekly(weeklyData);
        setByExercise(exerciseData);
        setTrend(trendData);
        setSessions(sessionData);
        setProfile(profileData);
        setMeasurements(measurementData);
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

  const hasAnalytics = !!summary || sessions.length > 0 || trend.length > 0 || weekly.length > 0 || byExercise.length > 0;

  const currentWeight = profile?.weight_kg ?? 0;
  const currentBmi = profile?.bmi ?? 0;
  const goalCount = summary?.sessions_this_week ?? 0;
  const recentSessions = sessions.slice(0, 10);
  const bmiHistory = measurements.length > 0
    ? measurements.map((measurement) => ({
      date: new Date(measurement.measured_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      bmi: Number(measurement.bmi),
    }))
    : currentBmi ? [{ date: 'Current', bmi: Number(currentBmi) }] : [];

  return (
    <div className="space-y-8">
      {!hasAnalytics ? (
        <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-10 text-center shadow-sm">
          <h2 className="text-2xl font-semibold text-slate-900">No workout data yet</h2>
          <p className="mt-3 text-slate-600">Your dashboard will populate after your first exercise session. Start with a quick workout to unlock performance tracking.</p>
        </div>
      ) : (
        <>
          <WeeklySessionsChart
            sessions={sessions}
            goalValue={goalCount}
            goalTarget={4}
            expanded={showCalendarDetails}
            onSeeDetails={() => setShowCalendarDetails((visible) => !visible)}
          />

          <div className="rounded-2xl bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-slate-900">Report</h2>
              <button type="button" onClick={() => setShowBmiLog((visible) => !visible)} className="rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-600">
                {showBmiLog ? 'Hide log' : 'Log'}
              </button>
            </div>

            <div className="mt-4 space-y-5">
              <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
                <div>
                  <p className="text-sm text-slate-500">Current weight</p>
                  <p className="mt-2 text-3xl font-semibold text-slate-900">{currentWeight ? `${currentWeight.toFixed(0)} kg` : '—'}</p>
                </div>

                <div className="space-y-1 text-right text-base text-slate-600">
                  <p>Heaviest <span className="font-semibold text-slate-900">{currentWeight ? `${currentWeight.toFixed(0)} kg` : '—'}</span></p>
                  <p>Lightest <span className="font-semibold text-slate-900">{currentWeight ? `${currentWeight.toFixed(0)} kg` : '—'}</span></p>
                </div>
              </div>

              {showBmiLog ? <div className="h-64 w-full">
                {bmiHistory.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={bmiHistory} margin={{ top: 12, right: 8, left: -20, bottom: 4 }}>
                      <XAxis dataKey="date" tick={{ fontSize: 12, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                      <YAxis domain={['dataMin - 1', 'dataMax + 1']} tick={{ fontSize: 12, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                      <Tooltip formatter={(value) => [`${value}`, 'BMI']} />
                      <Line type="monotone" dataKey="bmi" stroke="#2563eb" strokeWidth={3} dot={{ r: 4, fill: '#2563eb', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 6 }} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : <div className="flex h-full items-center justify-center rounded-2xl bg-slate-50 text-sm text-slate-500">Log a measurement to see BMI change over time.</div>}
              </div> : null}

              <div className="flex items-center justify-between gap-3">
                <h3 className="text-lg font-semibold text-slate-900">BMI</h3>
                <span className="text-3xl font-semibold text-slate-900">{currentBmi ? currentBmi.toFixed(1) : '0.0'}</span>
              </div>

              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3 rounded-full bg-slate-100 px-4 py-2 text-lg font-medium text-slate-700">
                  <span className="h-4 w-4 rounded-full" style={{ backgroundColor: bmiCategory.color }} />
                  {bmiCategory.label}
                </div>
              </div>

              {showBmiLog ? <div className="mt-4 grid grid-cols-5 gap-2 overflow-hidden rounded-full">
                {[18.5, 25, 30, 35, 40].map((threshold, index) => (
                  <div
                    key={threshold}
                    className={[
                      'h-4',
                      index === 0 ? 'rounded-l-full bg-blue-500' : '',
                      index === 1 ? 'bg-cyan-400' : '',
                      index === 2 ? 'bg-amber-300' : '',
                      index === 3 ? 'bg-orange-400' : '',
                      index === 4 ? 'rounded-r-full bg-rose-500' : '',
                    ].join(' ')}
                  />
                ))}
              </div> : null}

              {showBmiLog ? <div className="flex items-center justify-between text-sm text-slate-500">
                <span>15</span>
                <span>18.5</span>
                <span>25</span>
                <span>30</span>
                <span>35</span>
                <span>40</span>
              </div> : null}

              {profile?.height_cm ? (
                <div className="flex items-center justify-between text-2xl font-semibold text-slate-800">
                  <span>Height</span>
                  <span>{profile.height_cm.toFixed(0)} cm</span>
                </div>
              ) : null}
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-4">
            <MetricCard label="Total sessions" value={summary?.total_sessions ?? 0} />
            <MetricCard label="Total reps" value={summary?.total_reps ?? 0} />
            <MetricCard label="Avg accuracy" value={`${summary?.avg_accuracy ?? 0}%`} />
            <MetricCard label="Current streak" value={`${summary?.current_streak_days ?? 0} days`} />
          </div>
          <div className="grid gap-4 xl:grid-cols-2">
            <AccuracyTrendChart data={trend || []} />
            <div className="rounded-2xl bg-white p-4 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-slate-900">Performance summary</h2>
              <div className="space-y-4">
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-sm text-slate-500">Best streak</p>
                  <p className="mt-2 text-3xl font-bold text-slate-900">{summary?.best_streak_days ?? 0} days</p>
                </div>
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-sm text-slate-500">Goal progress</p>
                  <p className="mt-2 text-3xl font-bold text-slate-900">{goalCount}/4</p>
                </div>
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-sm text-slate-500">BMI category</p>
                  <p className="mt-2 text-2xl font-bold text-slate-900">{bmiCategory.label}</p>
                </div>
              </div>
            </div>
          </div>
          <ExerciseBreakdownChart data={byExercise || []} />
          <div className="grid gap-4 xl:grid-cols-2">
            <AccuracyGauge value={summary?.avg_accuracy ?? 0} />
            <div className="rounded-3xl bg-white p-4 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-slate-900">Recent sessions</h2>
              {recentSessions.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-600">
                  No session history yet. Your most recent workouts will appear here.
                </div>
              ) : (
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
                      {recentSessions.map((session, index) => (
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
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
