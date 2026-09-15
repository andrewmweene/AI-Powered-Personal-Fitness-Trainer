/**
 * Static exercise instructions for the exercise tab.
 */
import React from 'react';
import { AlertCircle, Dumbbell, Play, Target } from 'lucide-react';

const exerciseContent = {
  Squat: {
    description: 'A fundamental lower-body exercise that targets the quadriceps, hamstrings, and glutes. Essential for building leg strength and improving mobility.',
    startingPosition: [
      'Stand with feet shoulder-width apart, toes pointing slightly outward',
      'Keep your chest up and spine neutral',
      'Arms extended forward for balance or crossed at chest',
      'Weight evenly distributed through both feet',
    ],
    movement: [
      'Brace your core and take a deep breath',
      'Push your hips back and bend your knees simultaneously',
      'Lower until thighs are parallel to the floor (or as deep as comfortable)',
      'Drive through your heels to return to standing',
      'Exhale at the top and squeeze glutes',
    ],
    mistakes: [
      'Knees caving inward — push them out in line with toes',
      'Heels rising off the floor — improve ankle mobility or elevate heels slightly',
      'Rounding the lower back — engage core throughout and keep chest up',
    ],
    muscles: 'Quadriceps, Hamstrings, Glutes, Core, Calves',
  },
  'Bicep Curl': {
    description: 'An isolation exercise targeting the biceps brachii. Builds arm strength and size when performed with controlled movement.',
    startingPosition: [
      'Stand with feet hip-width apart',
      'Hold dumbbells at your sides with palms facing forward',
      'Keep elbows pinned close to your torso',
      'Shoulders relaxed and down',
    ],
    movement: [
      'Keeping upper arms stationary, exhale and curl weights toward shoulders',
      'Supinate (rotate) your wrists at the top so pinkies point toward ceiling',
      'Squeeze biceps hard at peak contraction',
      'Slowly lower weights back to starting position (3 seconds down)',
      'Fully extend arms at the bottom — do not lock elbows',
    ],
    mistakes: [
      'Swinging the torso to lift the weight — reduce weight and control the movement',
      'Not fully extending at the bottom — limits range of motion and growth',
      'Elbows drifting forward — keep them pinned to your sides throughout',
    ],
    muscles: 'Biceps brachii, Brachialis, Forearms',
  },
  'Push-up': {
    description: 'A classic bodyweight exercise that builds upper body and core strength. Highly versatile and requires no equipment.',
    startingPosition: [
      'Place hands slightly wider than shoulder-width',
      'Arms fully extended, body forms a straight line from head to heels',
      'Feet together or hip-width apart',
      'Core tight, glutes engaged, neck neutral',
    ],
    movement: [
      'Take a breath and brace your core',
      'Lower your chest to the floor by bending elbows at 45 degrees to your body',
      'Keep elbows from flaring out wide',
      'Lower until chest is 2-3cm from the floor',
      'Press through palms to return to start — exhale on the way up',
    ],
    mistakes: [
      'Hips sagging — engage core throughout the entire movement',
      'Elbows flaring out at 90 degrees — keep them at 45 degrees',
      'Partial range of motion — chest should nearly touch the floor each rep',
    ],
    muscles: 'Pectorals, Triceps, Anterior deltoids, Core',
  },
  'Dumbbell Fly': {
    description: 'A chest isolation exercise that stretches and contracts the pectoral muscles through a wide arc of motion.',
    startingPosition: [
      'Lie flat on a bench or floor with a dumbbell in each hand',
      'Arms extended directly above chest, palms facing each other',
      'Maintain a slight bend in the elbows throughout',
      'Shoulder blades retracted and pressed into the bench',
    ],
    movement: [
      'Take a breath and lower arms in a wide arc to your sides',
      'Keep the slight elbow bend — do not let them straighten',
      'Lower until you feel a good stretch in your chest (upper arms parallel to floor)',
      'Squeeze chest muscles to bring arms back up through the same arc',
      'Dumbbells should not touch at the top — stop when hands are above shoulders',
    ],
    mistakes: [
      'Straightening arms completely — turns it into a press and strains elbows',
      'Going too heavy — reduces control and increases injury risk',
      'Not feeling the stretch at the bottom — focus on the chest contraction, not the weight',
    ],
    muscles: 'Pectoralis major, Anterior deltoids, Biceps (stabiliser)',
  },
  'Dumbbell Kickback': {
    description: 'A tricep isolation exercise performed bent over. Highly effective for building the back of the upper arm.',
    startingPosition: [
      'Hinge forward at the hips until torso is nearly parallel to the floor',
      'Hold a dumbbell in each hand with upper arms parallel to the floor',
      'Elbows bent at 90 degrees, hugged close to your sides',
      'Core engaged, spine neutral',
    ],
    movement: [
      'Keeping upper arm completely still, exhale and extend the forearm back',
      'Straighten arm until fully extended — pause for 1 second',
      'Squeeze tricep hard at full extension',
      'Slowly lower the forearm back to 90 degrees (2-3 seconds)',
      'Do not swing or use momentum',
    ],
    mistakes: [
      'Upper arm dropping — it must stay parallel to the floor throughout',
      'Using momentum to swing the weight — slow and controlled',
      'Not reaching full extension — the lockout is where the tricep contracts most',
    ],
    muscles: 'Triceps brachii (all three heads), Posterior deltoids',
  },
};

const sectionConfig = [
  { key: 'startingPosition', title: 'Starting position', icon: Target },
  { key: 'movement', title: 'Movement', icon: Play },
  { key: 'mistakes', title: 'Common mistakes', icon: AlertCircle },
  { key: 'muscles', title: 'Muscles worked', icon: Dumbbell },
];

/**
 * @param {{ exercise: string }} props
 */
export default function ExerciseInstructions({ exercise = 'Squat' }) {
  const content = exerciseContent[exercise] || exerciseContent.Squat;

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="text-2xl font-semibold text-slate-900">{exercise}</h3>
      <p className="mt-2 text-sm text-slate-600">{content.description}</p>

      <div className="mt-5 space-y-4">
        {sectionConfig.map(({ key, title, icon: Icon }) => (
          <div key={title} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div className="mb-3 flex items-center gap-2 text-base font-semibold text-slate-800">
              <Icon className="h-4 w-4 text-primary" />
              <span>{title}</span>
            </div>

            {key === 'muscles' ? (
              <p className="text-sm text-slate-700">{content[key]}</p>
            ) : (
              <ul className="space-y-2 text-sm text-slate-700">
                {(content[key] || []).map((item, index) => (
                  <li key={`${title}-${index}`} className="flex gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
