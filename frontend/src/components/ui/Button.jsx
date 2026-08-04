/**
 * Button component with variant and loading states.
 */
import React from 'react';

/**
 * @param {{ variant?: 'primary'|'secondary'|'danger', children: React.ReactNode, onClick?: () => void, disabled?: boolean, loading?: boolean }} props
 */
export default function Button({ variant = 'primary', type = 'button', children, onClick, disabled, loading, className = '' }) {
  const base = 'inline-flex items-center justify-center rounded-full px-5 py-2.5 text-sm font-semibold transition';
  const variants = {
    primary: 'bg-primary text-white hover:bg-blue-600',
    secondary: 'bg-slate-100 text-slate-900 hover:bg-slate-200',
    danger: 'bg-danger text-white hover:bg-rose-600',
  };

  return (
    <button
      type={type}
      className={`${base} ${variants[variant]} ${disabled ? 'cursor-not-allowed opacity-60' : ''} ${className}`}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading ? <span className="inline-flex h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" /> : null}
      <span className={loading ? 'ml-2' : ''}>{children}</span>
    </button>
  );
}
