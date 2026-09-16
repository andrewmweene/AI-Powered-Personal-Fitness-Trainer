/**
 * Line chart for session accuracy trend.
 */
import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

/**
 * @param {{ data: Array<{ session_num: number, accuracy: number }> }} props
 */
export default function AccuracyTrendChart({ data }) {
  return (
    <div className="rounded-2xl bg-white p-4 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-slate-900">Accuracy Trend</h2>
      <ResponsiveContainer width="100%" height={330}>
        <LineChart data={data} margin={{ top: 10, right: 20, left: 5, bottom: 24 }}>
          <XAxis dataKey="session_num" tick={{ fontSize: 12 }} label={{ value: 'Session', position: 'insideBottom', dy: 20 }} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} label={{ value: 'Accuracy (%)', angle: -90, position: 'insideLeft', dx: -10 }} />
          <Tooltip formatter={(value) => `${value}%`} labelFormatter={(label) => `Session ${label}`} />
          <ReferenceLine y={80} stroke="#1976D2" strokeDasharray="4 4" label={{ value: 'Target', position: 'insideTopRight', fill: '#1976D2' }} />
          <Line dataKey="accuracy" stroke="#1976D2" dot={false} strokeWidth={3} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
