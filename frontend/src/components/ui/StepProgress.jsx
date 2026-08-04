/**
 * Progress indicator for onboarding steps.
 */
import React from 'react';

/**
 * @param {{ currentStep: number, totalSteps: number, stepName: string }} props
 */
export default function StepProgress({ currentStep, totalSteps, stepName }) {
  const progressPercent = totalSteps > 1 ? ((currentStep - 1) / (totalSteps - 1)) * 100 : 0;
  return (
    <div className="mb-6">
      <div className="flex items-center justify-between text-sm text-slate-600">
        <span>Step {currentStep} of {totalSteps}</span>
        <span>{stepName}</span>
      </div>
      <div className="mt-2 h-2 rounded-full bg-slate-200">
        <div className="h-2 rounded-full bg-primary" style={{ width: `${progressPercent}%` }} />
      </div>
    </div>
  );
}
