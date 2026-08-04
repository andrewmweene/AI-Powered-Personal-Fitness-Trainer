/**
 * Bar chart for weekly session counts.
 */
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

function getBarColor(avgAccuracy) {
  if (avgAccuracy >= 80) return '#16a34a';
  if (avgAccuracy >= 60) return '#f59e0b';
  return '#ef4444';
}

/**
 * @param {{ data: Array<{ date: string, session_count: number, avg_accuracy: number }> }} props
 */
export default function WeeklySessionsChart({ data }) {
  return (
    <div className="rounded-2xl bg-white p-4 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-slate-900">Weekly Sessions</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip formatter={(value) => [`${value}`, 'Sessions']} />
          <Bar dataKey="session_count" radius={[8, 8, 0, 0]}>
            {data.map((entry) => (
              <Cell key={entry.date} fill={getBarColor(entry.avg_accuracy)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
