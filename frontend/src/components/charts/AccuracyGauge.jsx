/**
 * Radial gauge chart for average accuracy.
 */
import React from 'react';
import { RadialBarChart, RadialBar, ResponsiveContainer } from 'recharts';

function getGaugeColor(value) {
  if (value >= 80) return '#16a34a';
  if (value >= 60) return '#f59e0b';
  return '#ef4444';
}

/**
 * @param {{ value: number }} props
 */
export default function AccuracyGauge({ value }) {
  const gaugeColor = getGaugeColor(value);
  return (
    <div className="rounded-2xl bg-white p-4 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-slate-900">Avg Accuracy</h2>
      <div className="relative h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart innerRadius="80%" outerRadius="100%" data={[{ name: 'accuracy', value }]} startAngle={180} endAngle={0}>
            <RadialBar minAngle={15} background={false} clockWise dataKey="value" cornerRadius={20} fill={gaugeColor} />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="absolute inset-x-0 top-1/2 flex -translate-y-1/2 flex-col items-center justify-center">
          <span className="text-4xl font-bold text-slate-900">{value ?? 0}%</span>
          <span className="text-sm text-slate-500">Average accuracy</span>
        </div>
      </div>
    </div>
  );
}
