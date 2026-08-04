/**
 * Displays a summary metric with optional delta and colour coding.
 */
import React from 'react';

/**
 * @param {{ label: string, value: string|number, delta?: string, colour?: 'success'|'warning'|'danger'|'default' }} props
 */
export default function MetricCard({ label, value, delta, colour = 'default' }) {
  const deltaClasses = {
    success: 'text-emerald-600',
    warning: 'text-orange-600',
    danger: 'text-rose-600',
    default: 'text-slate-500',
  };

  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-slate-900">{value}</p>
      {delta ? <p className={`mt-2 text-sm ${deltaClasses[colour]}`}>{delta}</p> : null}
    </div>
  );
}
