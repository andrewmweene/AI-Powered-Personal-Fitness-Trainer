/**
 * Displays a summary metric with optional delta and colour coding.
 */
import React from 'react';

/**
 * @param {{ label: string, value: string|number, delta?: string, colour?: 'success'|'warning'|'danger'|'default' }} props
 */
export default function MetricCard({ label, value, delta, colour = 'default' }) {
  // Support both semantic and literal colour names from onboarding (e.g. 'blue','green','orange','red')
  const deltaClasses = {
    // semantic
    success: 'text-emerald-600',
    warning: 'text-orange-600',
    danger: 'text-rose-600',
    default: 'text-slate-500',
    // literal colours used by BMI category
    blue: 'text-sky-600',
    green: 'text-emerald-600',
    orange: 'text-orange-600',
    red: 'text-rose-600',
  };

  const deltaClass = deltaClasses[colour] || deltaClasses.default;

  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-slate-900">{value}</p>
      {delta ? <p className={`mt-2 text-sm ${deltaClass}`}>{delta}</p> : null}
    </div>
  );
}
