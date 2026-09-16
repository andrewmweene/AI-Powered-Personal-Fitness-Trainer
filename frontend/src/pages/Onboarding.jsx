/**
 * Onboarding wizard with body profile, goal, equipment, and availability steps.
 */
import React, { useEffect, useMemo, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useLocation, useNavigate } from 'react-router-dom';
import { completeOnboarding, getProfile, getStatus } from '../api/onboarding.js';
import AlertBanner from '../components/ui/AlertBanner.jsx';
import Button from '../components/ui/Button.jsx';
import MetricCard from '../components/ui/MetricCard.jsx';
import StepProgress from '../components/ui/StepProgress.jsx';

const goalOptions = [
  { value: 'weight_loss', label: 'Weight loss', description: 'Burns calories through varied intensity circuits' },
  { value: 'muscle_gain', label: 'Muscle gain', description: 'Progressive overload with compound movements' },
  { value: 'strength_training', label: 'Strength training', description: 'Low rep, high resistance to build raw strength' },
  { value: 'endurance', label: 'Endurance', description: 'High rep, lower rest to improve stamina' },
  { value: 'general_fitness', label: 'General fitness', description: 'Balanced mix of strength and cardio' },
  { value: 'flexibility', label: 'Flexibility', description: 'Range of motion and joint mobility focus' },
  { value: 'sports_specific', label: 'Sports specific', description: 'Explosive power for athletic performance' },
];

const equipmentItems = ['Dumbbells', 'Resistance bands', 'Pull-up bar', 'Kettlebell', 'Barbell + rack', 'Bench', 'Cables/machine', 'Full gym access'];

export default function Onboarding() {
  const navigate = useNavigate();
  const location = useLocation();
  const isEditing = new URLSearchParams(location.search).get('edit') === '1';
  const [currentStep, setCurrentStep] = useState(2);
  const [error, setError] = useState('');

  useEffect(() => {
    const redirectIfComplete = async () => {
      try {
        const statusData = await getStatus();
        if (statusData.onboarding_complete && !isEditing) {
          navigate('/dashboard', { replace: true });
        }
      } catch (error) {
        // Ignore and allow user to continue onboarding if the status check fails.
      }
    };

    redirectIfComplete();
  }, [isEditing, navigate]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
    height_cm: '',
    weight_kg: '',
    fitness_level: 'Beginner',
    goal: 'weight_loss',
    equipment_type: 'bodyweight',
    equipment_list: [],
    days_per_week: 3,
    workout_duration_minutes: 30,
    preferred_time: 'Morning (8-11am)',
  });

  const form = useForm({ defaultValues: formData });
  const { register, handleSubmit, watch, reset, formState: { errors } } = form;

  useEffect(() => {
    if (!isEditing) return;

    async function loadProfile() {
      try {
        const profile = await getProfile();
        const existing = {
          age: profile.age,
          gender: profile.gender || '',
          height_cm: profile.height_cm,
          weight_kg: profile.weight_kg,
          fitness_level: profile.fitness_level.charAt(0).toUpperCase() + profile.fitness_level.slice(1),
          goal: profile.goal,
          equipment_type: profile.has_equipment ? 'equipment' : 'bodyweight',
          equipment_list: profile.equipment_list || [],
          days_per_week: profile.days_per_week,
          workout_duration_minutes: profile.workout_duration_minutes,
          preferred_time: profile.preferred_time,
        };
        setFormData(existing);
        reset(existing);
      } catch (profileError) {
        setError('Unable to load your profile for editing.');
      }
    }

    loadProfile();
  }, [isEditing, reset]);
  const watchedHeight = Number(watch('height_cm') || formData.height_cm);
  const watchedWeight = Number(watch('weight_kg') || formData.weight_kg);
  const watchedGoal = watch('goal') || formData.goal;
  const watchedEquipmentType = watch('equipment_type') || formData.equipment_type;
  const watchedDays = watch('days_per_week') || formData.days_per_week;
  const watchedDuration = watch('workout_duration_minutes') || formData.workout_duration_minutes;
  const watchedPreferredTime = watch('preferred_time') || formData.preferred_time;

  const hasValidBodyMeasurements = watchedHeight >= 50 && watchedHeight <= 300 && watchedWeight >= 20 && watchedWeight <= 300;
  const bmi = useMemo(() => {
    if (!hasValidBodyMeasurements) return null;
    return Number((watchedWeight / ((watchedHeight / 100) ** 2)).toFixed(1));
  }, [hasValidBodyMeasurements, watchedHeight, watchedWeight]);

  const bmiCategory = useMemo(() => {
    if (bmi === null) return { label: 'Enter height and weight', colour: 'default' };
    if (bmi < 18.5) return { label: 'Underweight', colour: 'blue' };
    if (bmi < 25) return { label: 'Normal weight', colour: 'green' };
    if (bmi < 30) return { label: 'Overweight', colour: 'orange' };
    return { label: 'Obese', colour: 'red' };
  }, [bmi]);

  const updateFormData = (newValues) => {
    setFormData({ ...formData, ...newValues });
  };

  const onNext = async (values) => {
    setError('');
    const merged = { ...formData, ...values };
    if (currentStep === 4 && merged.equipment_type === 'equipment' && merged.equipment_list.length === 0) {
      setError('Please select at least one equipment item.');
      return;
    }
    updateFormData(merged);
    setCurrentStep((prev) => Math.min(prev + 1, 5));
  };

  const onBack = () => {
    setError('');
    setCurrentStep((prev) => Math.max(prev - 1, 2));
  };

  const onSubmit = async (values) => {
    setError('');
    setLoading(true);
    const submitted = { ...formData, ...values };
    const payload = {
      age: Number(submitted.age),
      gender: submitted.gender || null,
      height_cm: Number(submitted.height_cm),
      weight_kg: Number(submitted.weight_kg),
      fitness_level: String(submitted.fitness_level).toLowerCase(),
      goal: submitted.goal,
      has_equipment: submitted.equipment_type === 'equipment',
      equipment_list: submitted.equipment_list || [],
      days_per_week: Number(submitted.days_per_week),
      workout_duration_minutes: Number(submitted.workout_duration_minutes),
      preferred_time: submitted.preferred_time,
    };
    try {
      await completeOnboarding(payload);
      navigate('/plan');
    } catch (apiError) {
      const detail = apiError.response?.data?.detail;
      const message = Array.isArray(detail)
        ? detail.map((item) => item.msg || 'Invalid field').join(' ')
        : detail;
      setError(message || 'Unable to submit onboarding details.');
    } finally {
      setLoading(false);
    }
  };

  const commonStepProps = {
    register,
    errors,
    formData,
    updateFormData,
    watchedHeight,
    watchedWeight,
    bmi,
    bmiCategory,
    watchedGoal,
    watchedEquipmentType,
    watchedDays,
    watchedDuration,
    watchedPreferredTime,
    equipmentItems,
  };

  return (
    <div className="mx-auto max-w-4xl rounded-3xl bg-white p-8 shadow-lg sm:p-10">
      <div className="mb-6 rounded-2xl border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-blue-900">
        Set up your profile so the app can generate a weekly plan that matches your goals.
      </div>
      <div className="mb-6 flex items-center gap-2 overflow-x-auto pb-1">
        {['Profile', 'Goals', 'Equipment', 'Availability'].map((stepName, index) => {
          const stepNumber = index + 2;
          const active = currentStep === stepNumber;
          const complete = currentStep > stepNumber;
          return (
            <React.Fragment key={stepName}>
              <div className="flex min-w-fit items-center gap-2">
                <span className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold ${active || complete ? 'bg-primary text-white' : 'bg-slate-100 text-slate-500'}`}>
                  {complete ? '✓' : index + 1}
                </span>
                <span className={`text-sm font-medium ${active ? 'text-slate-900' : 'text-slate-500'}`}>{stepName}</span>
              </div>
              {index < 3 ? <span className="h-px min-w-5 flex-1 bg-slate-200" /> : null}
            </React.Fragment>
          );
        })}
      </div>
      <StepProgress currentStep={currentStep - 1} totalSteps={4} stepName={['Profile', 'Goals', 'Equipment', 'Availability'][Math.max(0, currentStep - 2)]} />
      {error ? <AlertBanner type="error" message={error} onDismiss={() => setError('')} /> : null}
      <form onSubmit={handleSubmit(currentStep === 5 ? onSubmit : onNext)} className="space-y-8">
        {currentStep === 2 && (
          <div className="grid gap-6 lg:grid-cols-2">
            <div>
              <label htmlFor="age" className="block text-sm font-medium text-slate-700">Age</label>
              <input id="age" type="number" {...register('age', { required: 'Age is required.', valueAsNumber: true, min: { value: 13, message: 'Age must be between 13 and 100.' }, max: { value: 100, message: 'Age must be between 13 and 100.' } })} defaultValue={formData.age} className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 focus:border-primary focus:outline-none" />
              {errors.age && <p className="mt-2 text-sm text-danger">Age must be between 13 and 100.</p>}
            </div>
            <div>
              <label htmlFor="gender" className="block text-sm font-medium text-slate-700">Gender</label>
              <select id="gender" {...register('gender')} defaultValue={formData.gender} className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 focus:border-primary focus:outline-none">
                <option value="">Prefer not to say</option>
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="nonbinary">Non-binary</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label htmlFor="height_cm" className="block text-sm font-medium text-slate-700">Height (cm)</label>
              <input id="height_cm" type="number" {...register('height_cm', { required: 'Height is required.', valueAsNumber: true, min: { value: 50, message: 'Height should be between 50 and 300 cm.' }, max: { value: 300, message: 'Height should be between 50 and 300 cm.' } })} defaultValue={formData.height_cm} className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 focus:border-primary focus:outline-none" />
              {errors.height_cm && <p className="mt-2 text-sm text-danger">Height should be between 50 and 300 cm.</p>}
            </div>
            <div>
              <label htmlFor="weight_kg" className="block text-sm font-medium text-slate-700">Weight (kg)</label>
              <input id="weight_kg" type="number" {...register('weight_kg', { required: 'Weight is required.', valueAsNumber: true, min: { value: 20, message: 'Weight should be between 20 and 300 kg.' }, max: { value: 300, message: 'Weight should be between 20 and 300 kg.' } })} defaultValue={formData.weight_kg} className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 focus:border-primary focus:outline-none" />
              {errors.weight_kg && <p className="mt-2 text-sm text-danger">Weight should be between 20 and 300 kg.</p>}
            </div>
            <div className="lg:col-span-2">
              <p className="mb-3 text-sm font-medium text-slate-700">Fitness level</p>
              <div className="grid gap-3 sm:grid-cols-3">
                {['Beginner', 'Intermediate', 'Advanced'].map((level) => (
                  <label key={level} className="flex cursor-pointer items-center gap-3 rounded-2xl border border-slate-300 bg-slate-50 px-3 py-2">
                    <input type="radio" value={level} {...register('fitness_level', { required: true })} defaultChecked={formData.fitness_level === level} />
                    <span>{level}</span>
                  </label>
                ))}
              </div>
            </div>
            <div className="lg:col-span-2">
              {bmi === null ? (
                <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">Enter height and weight to see your BMI.</div>
              ) : <MetricCard label="BMI" value={bmi} delta={bmiCategory.label} colour={bmiCategory.colour} />}
              <p className="mt-2 text-sm text-slate-500">BMI is for reference only and does not affect your workout plan.</p>
            </div>
          </div>
        )}

        {currentStep === 3 && (
          <div className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {goalOptions.map((goal) => (
                <label key={goal.value} className={`cursor-pointer rounded-3xl border p-5 ${watchedGoal === goal.value ? 'border-primary bg-blue-50' : 'border-slate-200 bg-slate-50'}`}>
                  <input type="radio" value={goal.value} {...register('goal', { required: true })} defaultChecked={formData.goal === goal.value} className="sr-only" />
                  <div className="text-lg font-semibold text-slate-900">{goal.label}</div>
                  <p className="mt-2 text-sm text-slate-600">{goal.description}</p>
                </label>
              ))}
            </div>
            <div className="rounded-3xl bg-blue-50 p-5 text-slate-900">
              <p className="text-sm font-semibold">Selected focus</p>
              <p className="mt-2 text-base">{goalOptions.find((item) => item.value === watchedGoal)?.description}</p>
            </div>
          </div>
        )}

        {currentStep === 4 && (
          <div className="space-y-6">
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <p className="text-sm font-medium text-slate-700">Equipment preference</p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {[
                  { value: 'equipment', label: 'I have equipment' },
                  { value: 'bodyweight', label: 'Bodyweight only' },
                ].map((option) => (
                  <label key={option.value} className={`cursor-pointer rounded-3xl border px-4 py-4 ${watchedEquipmentType === option.value ? 'border-primary bg-white' : 'border-slate-200 bg-slate-50'}`}>
                    <input type="radio" value={option.value} {...register('equipment_type', { required: true })} defaultChecked={formData.equipment_type === option.value} className="sr-only" />
                    <div className="text-base font-semibold text-slate-900">{option.label}</div>
                  </label>
                ))}
              </div>
            </div>
            {watchedEquipmentType === 'equipment' && (
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {equipmentItems.map((item) => (
                  <label key={item} className="flex cursor-pointer items-center gap-3 rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3">
                    <input type="checkbox" value={item} {...register('equipment_list')} defaultChecked={formData.equipment_list.includes(item)} />
                    <span className="text-sm text-slate-700">{item}</span>
                  </label>
                ))}
              </div>
            )}
          </div>
        )}

        {currentStep === 5 && (
          <div className="space-y-6">
            <div className="grid gap-6 lg:grid-cols-3">
              <div>
                <label htmlFor="days_per_week" className="block text-sm font-medium text-slate-700">Days per week</label>
                <input id="days_per_week" type="range" min="1" max="7" {...register('days_per_week', { valueAsNumber: true })} defaultValue={formData.days_per_week} className="mt-4 w-full" />
                <p className="mt-2 text-sm text-slate-700">{watchedDays} days per week</p>
              </div>
              <div>
                <label htmlFor="workout_duration_minutes" className="block text-sm font-medium text-slate-700">Workout duration</label>
                <select id="workout_duration_minutes" {...register('workout_duration_minutes', { valueAsNumber: true })} defaultValue={formData.workout_duration_minutes} className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 focus:border-primary focus:outline-none">
                  {[15, 20, 30, 45, 60, 75, 90].map((minutes) => (
                    <option key={minutes} value={minutes}>{minutes} minutes</option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="preferred_time" className="block text-sm font-medium text-slate-700">Preferred time</label>
                <select id="preferred_time" {...register('preferred_time')} defaultValue={formData.preferred_time} className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 focus:border-primary focus:outline-none">
                  {['Early morning (5-8am)', 'Morning (8-11am)', 'Midday (11am-2pm)', 'Afternoon (2-5pm)', 'Evening (5-8pm)', 'Late evening (8-11pm)'].map((option) => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="rounded-3xl bg-slate-50 p-6">
              <h3 className="text-lg font-semibold text-slate-900">Profile summary</h3>
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <MetricCard label="Age" value={formData.age || 'N/A'} />
                <MetricCard label="Goal" value={watchedGoal} />
                <MetricCard label="Days per week" value={`${watchedDays} days`} />
                <MetricCard label="Duration" value={`${watchedDuration} min`} />
                <MetricCard label="Preferred time" value={watchedPreferredTime} />
                <MetricCard label="Equipment" value={watchedEquipmentType === 'equipment' ? 'Has equipment' : 'Bodyweight only'} />
              </div>
            </div>
          </div>
        )}

        <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
          {currentStep > 2 ? (
            <Button type="button" variant="secondary" onClick={onBack}>← Back</Button>
          ) : <div />}
          <Button type="submit" loading={loading}>{currentStep === 5 ? 'Build my plan →' : 'Continue →'}</Button>
        </div>
      </form>
    </div>
  );
}
