import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { User, Scale, Target, Zap, Loader2 } from 'lucide-react'

/**
 * 🔁 Simulated backend workout response
 */
const MOCK_WORKOUT_RESPONSE = {
    date: '28/12/25',
    user_goal: 'fat_loss',
    daily_macros: {
        calories: 1600,
        protein_g: 150,
        carbs_g: 115,
        fats_g: 60,
    },
    workout_split: {
        name: 'Full Body - Beginner Foundation',
        primary_muscles: ['legs', 'chest', 'back', 'shoulders'],
        secondary_muscles: ['core'],
        style: 'motor_learning',
        cardio: {
            type: 'Walking',
            duration_minutes: 20,
            distance_km: 2.0,
            intensity: 'moderate',
            target_heart_rate_bpm: '120-140',
        },
    },
    exercises: [
        { name: 'Goblet Squat', sets: 3, reps: '10-15', time_minutes: 8 },
        {
            name: 'Dumbbell Bench Press',
            sets: 3,
            reps: '10-15',
            time_minutes: 8,
        },
        { name: 'Lat Pulldown', sets: 3, reps: '10-15', time_minutes: 8 },
        {
            name: 'Dumbbell Shoulder Press',
            sets: 2,
            reps: '10-15',
            time_minutes: 6,
        },
        { name: 'Plank', sets: 2, reps: '30-45 sec hold', time_minutes: 3 },
    ],
    time_required_minutes: 63,
    diet_rationale:
        'The provided nutrition targets of 1600 calories, 150g protein, 115g carbs, and 60g fat are specifically designed to support fat loss while preserving muscle.',
    workout_rationale:
        'This full-body workout focuses on motor learning, compound lifts, and moderate intensity for beginners.',
    current_weight: 65.0,
    workout_intensity: 'moderate',
    calories_burnt: 350,
}

function GetStarted() {
    const navigate = useNavigate()

    // 🔁 THIS WILL COME FROM BACKEND LATER
    const isNewUser = false // change to false to test existing user flow

    const [loading, setLoading] = useState(false)

    const [formData, setFormData] = useState({
        name: '',
        weight: '',
        nutrition_goal: 'fat_loss',
        experience: 'beginner',
    })

    function handleChange(e) {
        const { name, value } = e.target
        setFormData((prev) => ({ ...prev, [name]: value }))
    }

    function simulateBackendAndNavigate() {
        setLoading(true)

        setTimeout(() => {
            navigate('/today-workout', {
                state: {
                    workoutData: MOCK_WORKOUT_RESPONSE,
                },
            })
        }, 1500)
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-800 to-slate-900 px-6 text-white">
            <div className="w-full max-w-2xl rounded-2xl bg-slate-900/80 p-8 shadow-2xl">
                {/* ===== HEADER ===== */}
                <h1 className="mb-6 text-3xl font-extrabold text-violet-400">
                    {isNewUser ? 'Get Started' : 'Welcome Back'}
                </h1>

                {/* ===== EXISTING USER ===== */}
                {!isNewUser && (
                    <button
                        onClick={simulateBackendAndNavigate}
                        disabled={loading}
                        className="flex w-full items-center justify-center gap-2 rounded-lg bg-violet-500 py-4 text-lg font-semibold transition hover:bg-violet-600"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="animate-spin" />
                                Fetching today’s workout...
                            </>
                        ) : (
                            'Show Today’s Workout'
                        )}
                    </button>
                )}

                {/* ===== NEW USER ===== */}
                {isNewUser && (
                    <form
                        onSubmit={(e) => {
                            e.preventDefault()
                            simulateBackendAndNavigate()
                        }}
                        className="space-y-6"
                    >
                        <div>
                            <label className="mb-2 flex items-center gap-2 text-sm text-slate-300">
                                <User size={16} /> Name
                            </label>
                            <input
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                required
                                className="w-full rounded-lg bg-slate-800 px-4 py-3 ring-1 ring-slate-700"
                            />
                        </div>

                        <div>
                            <label className="mb-2 flex items-center gap-2 text-sm text-slate-300">
                                <Scale size={16} /> Weight (kg)
                            </label>
                            <input
                                type="number"
                                name="weight"
                                value={formData.weight}
                                onChange={handleChange}
                                required
                                className="w-full rounded-lg bg-slate-800 px-4 py-3 ring-1 ring-slate-700"
                            />
                        </div>

                        <div>
                            <label className="mb-2 flex items-center gap-2 text-sm text-slate-300">
                                <Target size={16} /> Goal
                            </label>
                            <select
                                name="nutrition_goal"
                                value={formData.nutrition_goal}
                                onChange={handleChange}
                                className="w-full rounded-lg bg-slate-800 px-4 py-3 ring-1 ring-slate-700"
                            >
                                <option value="fat_loss">Fat Loss</option>
                                <option value="muscle_gain">Muscle Gain</option>
                            </select>
                        </div>

                        <div>
                            <label className="mb-2 flex items-center gap-2 text-sm text-slate-300">
                                <Zap size={16} /> Experience
                            </label>
                            <select
                                name="experience"
                                value={formData.experience}
                                onChange={handleChange}
                                className="w-full rounded-lg bg-slate-800 px-4 py-3 ring-1 ring-slate-700"
                            >
                                <option value="beginner">Beginner</option>
                                <option value="intermediate">
                                    Intermediate
                                </option>
                                <option value="pro">Pro</option>
                            </select>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="flex w-full items-center justify-center gap-2 rounded-lg bg-violet-500 py-4 font-semibold transition hover:bg-violet-600"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="animate-spin" />
                                    Generating workout...
                                </>
                            ) : (
                                'Build My Plan'
                            )}
                        </button>
                    </form>
                )}
            </div>
        </div>
    )
}

export default GetStarted
