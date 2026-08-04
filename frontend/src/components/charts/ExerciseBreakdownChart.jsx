/**
 * Horizontal bar chart for exercise breakdown by count and average accuracy.
 */
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LabelList } from 'recharts';

function getColor(avgAccuracy) {
  if (avgAccuracy >= 80) return '#16a34a';
  if (avgAccuracy >= 60) return '#f59e0b';
  return '#ef4444';
}

/**
 * @param {{ data: Array<{ exercise: string, count: number, avg_accuracy: number }> }} props
 */
export default function ExerciseBreakdownChart({ data }) {
  return (
    <div className="rounded-2xl bg-white p-4 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-slate-900">Exercise Breakdown</h2>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart layout="vertical" data={data} margin={{ left: 0, right: 20 }}>
          <XAxis type="number" tick={{ fontSize: 12 }} />
          <YAxis dataKey="exercise" type="category" width={120} tick={{ fontSize: 12 }} />
          <Tooltip formatter={(value) => [`${value}`, 'Count']} />
          <Bar dataKey="count" radius={[0, 8, 8, 0]}> 
            {data.map((entry) => (
              <Cell key={entry.exercise} fill={getColor(entry.avg_accuracy)} />
            ))}
            <LabelList dataKey="avg_accuracy" position="right" formatter={(value) => `Avg: ${value}%`} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
