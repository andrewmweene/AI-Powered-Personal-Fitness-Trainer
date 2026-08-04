/**
 * Centered loading spinner.
 */
import React from 'react';

export default function LoadingSpinner() {
  return (
    <div className="flex min-h-[220px] items-center justify-center">
      <div className="inline-flex h-12 w-12 animate-spin items-center justify-center rounded-full border-4 border-slate-200 border-t-primary"></div>
    </div>
  );
}
