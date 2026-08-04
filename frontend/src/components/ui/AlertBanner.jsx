/**
 * Shows an alert banner for success, error, or info messages.
 */
import React from 'react';
import { XCircle, CheckCircle, Info } from 'lucide-react';

/**
 * @param {{ type: 'success'|'error'|'info', message: string, onDismiss: () => void }} props
 */
export default function AlertBanner({ type, message, onDismiss }) {
  const styles = {
    success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    error: 'bg-rose-50 border-rose-200 text-rose-800',
    info: 'bg-sky-50 border-sky-200 text-sky-800',
  };

  const Icon = type === 'success' ? CheckCircle : type === 'error' ? XCircle : Info;

  return (
    <div className={`mb-4 flex items-start gap-3 rounded-xl border px-4 py-3 ${styles[type]}`}>
      <Icon className="mt-1 h-5 w-5 flex-shrink-0" />
      <div className="flex-1 text-sm leading-6">{message}</div>
      <button type="button" aria-label="Dismiss alert" onClick={onDismiss} className="text-slate-600 hover:text-slate-900">
        ✕
      </button>
    </div>
  );
}
