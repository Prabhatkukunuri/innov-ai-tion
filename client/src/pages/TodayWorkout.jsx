import { useLocation, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { Dumbbell, Flame, Clock, HeartPulse, Loader2 } from 'lucide-react'

const INGREDIENT_OPTIONS = [
    'chicken breast',
    'egg',
    'tofu',
    'paneer',
    'white rice',
    'brown rice',
    'oats',
    'tomato',
    'onion',
    'carrot',
    'spinach',
    'broccoli',
    'olive oil',
    'butter',
    'ghee',
]

const MOCK_MEALS_RESPONSE = {
    date: '25/12/2025',
    nutrition_goal: 'fat_loss',
    meals: {
        breakfast: {
            recipe: {
                recipe_name: 'Vegetable Omelette with Oats',
                ingredients: [
                    { item: 'egg', quantity_g: 120 }, // 2 large eggs
                    { item: 'oats', quantity_g: 55 },
                    { item: 'onion', quantity_g: 40 },
                    { item: 'tomato', quantity_g: 60 },
                    { item: 'spinach', quantity_g: 40 },
                    { item: 'olive oil', quantity_g: 6 },
                ],
                steps: [
                    'Finely chop onion, tomato, and spinach.',
                    'Heat olive oil in a pan and sauté vegetables for 2–3 minutes.',
                    'Beat eggs and pour into the pan. Cook into a soft omelette.',
                    'Cook oats separately with water until soft.',
                    'Serve the omelette alongside oats.',
                ],
            },
            target_macros: {
                calories: 450,
                protein_g: 28,
                carbs_g: 40,
                fats_g: 16,
            },
            actual_macros: {
                calories: 472,
                protein: 29.4,
                carbs: 42.1,
                fats: 17.2,
            },
            status: 'success',
            attempts: 1,
        },

        post_workout: {
            recipe: {
                recipe_name: 'High-Protein Chicken Rice Bowl',
                ingredients: [
                    { item: 'chicken breast', quantity_g: 160 },
                    { item: 'white rice raw', quantity_g: 80 },
                    { item: 'broccoli', quantity_g: 80 },
                    { item: 'carrot', quantity_g: 50 },
                    { item: 'olive oil', quantity_g: 8 },
                    { item: 'onion', quantity_g: 40 },
                ],
                steps: [
                    'Cook rice according to package instructions.',
                    'Sauté onion in olive oil until soft.',
                    'Add chicken and cook until fully done.',
                    'Add vegetables and cook for 2–3 minutes.',
                    'Serve chicken and vegetables over rice.',
                ],
            },
            target_macros: {
                calories: 650,
                protein_g: 45,
                carbs_g: 70,
                fats_g: 18,
            },
            actual_macros: {
                calories: 682,
                protein: 48.6,
                carbs: 67.9,
                fats: 19.1,
            },
            status: 'success',
            attempts: 1,
        },

        lunch: {
            recipe: {
                recipe_name: 'Paneer & Brown Rice Skillet',
                ingredients: [
                    { item: 'paneer', quantity_g: 120 },
                    { item: 'brown rice raw', quantity_g: 70 },
                    { item: 'bell pepper', quantity_g: 60 },
                    { item: 'onion', quantity_g: 50 },
                    { item: 'tomato', quantity_g: 80 },
                    { item: 'olive oil', quantity_g: 7 },
                ],
                steps: [
                    'Cook brown rice until fluffy.',
                    'Sauté onion and bell pepper in olive oil.',
                    'Add paneer cubes and lightly brown.',
                    'Add tomatoes and cook briefly.',
                    'Serve over cooked rice.',
                ],
            },
            target_macros: {
                calories: 550,
                protein_g: 32,
                carbs_g: 55,
                fats_g: 20,
            },
            actual_macros: {
                calories: 588,
                protein: 33.8,
                carbs: 56.4,
                fats: 22.6,
            },
            status: 'success',
            attempts: 1,
        },

        dinner: {
            recipe: {
                recipe_name: 'Tofu Stir-Fry with Vegetables',
                ingredients: [
                    { item: 'tofu', quantity_g: 180 },
                    { item: 'broccoli', quantity_g: 100 },
                    { item: 'spinach', quantity_g: 60 },
                    { item: 'carrot', quantity_g: 50 },
                    { item: 'olive oil', quantity_g: 6 },
                    { item: 'onion', quantity_g: 40 },
                ],
                steps: [
                    'Heat olive oil in a pan.',
                    'Sauté onion until translucent.',
                    'Add tofu cubes and cook until lightly golden.',
                    'Add vegetables and stir-fry for 3–4 minutes.',
                    'Serve hot.',
                ],
            },
            target_macros: {
                calories: 400,
                protein_g: 28,
                carbs_g: 30,
                fats_g: 14,
            },
            actual_macros: {
                calories: 422,
                protein: 30.1,
                carbs: 31.6,
                fats: 15.4,
            },
            status: 'success',
            attempts: 1,
        },
    },
}

function TodayWorkout() {
    const location = useLocation()
    const navigate = useNavigate()

    // 🔑 ENTIRE workout response from GetStarted
    const data = location.state?.workoutData

    const [dietType, setDietType] = useState('non_vegetarian')
    const [cookingSkill, setCookingSkill] = useState('basic')
    const [ingredients, setIngredients] = useState([])
    const [loadingMeals, setLoadingMeals] = useState(false)

    if (!data) {
        return (
            <div className="flex min-h-screen flex-col items-center justify-center bg-slate-900 text-white">
                <p className="mb-4">No workout data found.</p>
                <button
                    onClick={() => navigate('/get-started')}
                    className="rounded bg-violet-500 px-4 py-2"
                >
                    Go Back
                </button>
            </div>
        )
    }

    function toggleIngredient(item) {
        setIngredients((prev) =>
            prev.includes(item)
                ? prev.filter((i) => i !== item)
                : [...prev, item]
        )
    }

    function handleGenerateMeals() {
        const request2Payload = {
            workout_context: data,
            user_food_context: {
                diet_type: dietType,
                cooking_skill: cookingSkill,
                available_ingredients: ingredients,
            },
        }

        console.log('REQUEST 2 (CookingLLM):', request2Payload)

        setLoadingMeals(true)

        // 🔁 simulate CookingLLM backend
        setTimeout(() => {
            setLoadingMeals(false)

            navigate('/today-meals', {
                state: {
                    workoutResponse: data, // 🔑 FULL workout
                    mealsResponse: MOCK_MEALS_RESPONSE, // 🔑 FULL meals
                },
            })
        }, 1500)
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-800 to-slate-900 px-6 py-10 text-white">
            <div className="mx-auto max-w-4xl space-y-10 rounded-2xl bg-slate-900/80 p-8 shadow-2xl">
                {/* ===== HEADER ===== */}
                <div>
                    <h1 className="text-3xl font-extrabold text-violet-400">
                        {data.workout_split.name}
                    </h1>
                    <p className="mt-2 text-slate-400">
                        Goal:{' '}
                        <span className="text-white">{data.user_goal}</span> •
                        Intensity:{' '}
                        <span className="text-white">
                            {data.workout_intensity}
                        </span>
                    </p>
                </div>

                {/* ===== QUICK STATS ===== */}
                <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                    <Stat
                        icon={<Clock />}
                        label="Time"
                        value={`${data.time_required_minutes} min`}
                    />
                    <Stat
                        icon={<Flame />}
                        label="Calories Burnt"
                        value={`${data.calories_burnt} kcal`}
                    />
                    <Stat
                        icon={<Dumbbell />}
                        label="Intensity"
                        value={data.workout_intensity}
                    />
                    <Stat
                        icon={<HeartPulse />}
                        label="Cardio"
                        value={data.workout_split.cardio.type}
                    />
                </div>

                {/* ===== EXERCISES ===== */}
                <div>
                    <h2 className="mb-4 text-xl font-bold text-violet-400">
                        Exercises
                    </h2>
                    <div className="space-y-3">
                        {data.exercises.map((ex, i) => (
                            <div
                                key={i}
                                className="rounded-lg bg-slate-800 p-4 ring-1 ring-slate-700"
                            >
                                <p className="font-semibold text-white">
                                    {ex.name}
                                </p>
                                <p className="text-sm text-slate-400">
                                    {ex.sets} sets × {ex.reps} • ~
                                    {ex.time_minutes} min
                                </p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* ===== CARDIO ===== */}
                <div>
                    <h2 className="mb-2 text-xl font-bold text-violet-400">
                        Cardio
                    </h2>
                    <div className="rounded-lg bg-slate-800 p-4 ring-1 ring-slate-700">
                        <p className="text-slate-300">
                            {data.workout_split.cardio.type} for{' '}
                            {data.workout_split.cardio.duration_minutes} minutes
                            ({data.workout_split.cardio.distance_km} km) at{' '}
                            {data.workout_split.cardio.intensity} intensity
                        </p>
                        <p className="text-sm text-slate-400">
                            Target HR:{' '}
                            {data.workout_split.cardio.target_heart_rate_bpm}{' '}
                            bpm
                        </p>
                    </div>
                </div>

                {/* ===== NUTRITION TARGETS ===== */}
                <div>
                    <h2 className="mb-4 text-xl font-bold text-violet-400">
                        Nutrition Targets
                    </h2>
                    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                        <Macro
                            label="Calories"
                            value={`${data.daily_macros.calories} kcal`}
                        />
                        <Macro
                            label="Protein"
                            value={`${data.daily_macros.protein_g} g`}
                        />
                        <Macro
                            label="Carbs"
                            value={`${data.daily_macros.carbs_g} g`}
                        />
                        <Macro
                            label="Fats"
                            value={`${data.daily_macros.fats_g} g`}
                        />
                    </div>
                </div>

                {/* ===== WORKOUT RATIONALE ===== */}
                <div>
                    <h3 className="mb-2 font-semibold text-violet-400">
                        Workout Rationale
                    </h3>
                    <p className="text-sm leading-relaxed text-slate-300">
                        {data.workout_rationale}
                    </p>
                </div>

                {/* ===== DIET RATIONALE ===== */}
                <div>
                    <h3 className="mb-2 font-semibold text-violet-400">
                        Diet Rationale
                    </h3>
                    <p className="text-sm leading-relaxed text-slate-300">
                        {data.diet_rationale}
                    </p>
                </div>

                {/* ===== REQUEST 2 : COOKING INPUTS ===== */}
                <div className="border-t border-slate-700 pt-8">
                    <h2 className="mb-4 text-xl font-bold text-violet-400">
                        Meal Planning Preferences
                    </h2>

                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <div>
                            <label className="text-sm text-slate-400">
                                Diet Type
                            </label>
                            <select
                                value={dietType}
                                onChange={(e) => setDietType(e.target.value)}
                                className="mt-1 w-full rounded-lg bg-slate-800 px-4 py-3 ring-1 ring-slate-700"
                            >
                                <option value="vegetarian">Vegetarian</option>
                                <option value="non_vegetarian">
                                    Non-Vegetarian
                                </option>
                            </select>
                        </div>

                        <div>
                            <label className="text-sm text-slate-400">
                                Cooking Skill
                            </label>
                            <select
                                value={cookingSkill}
                                onChange={(e) =>
                                    setCookingSkill(e.target.value)
                                }
                                className="mt-1 w-full rounded-lg bg-slate-800 px-4 py-3 ring-1 ring-slate-700"
                            >
                                <option value="basic">Basic</option>
                                <option value="intermediate">
                                    Intermediate
                                </option>
                                <option value="pro">Pro</option>
                            </select>
                        </div>
                    </div>

                    <div className="mt-6">
                        <p className="mb-3 text-sm text-slate-400">
                            Available Ingredients
                        </p>
                        <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
                            {INGREDIENT_OPTIONS.map((item) => (
                                <button
                                    key={item}
                                    type="button"
                                    onClick={() => toggleIngredient(item)}
                                    className={`rounded-lg px-4 py-2 text-sm ring-1 transition ${
                                        ingredients.includes(item)
                                            ? 'bg-violet-500 text-white ring-violet-400'
                                            : 'bg-slate-800 text-slate-300 ring-slate-700 hover:ring-violet-400'
                                    }`}
                                >
                                    {item}
                                </button>
                            ))}
                        </div>
                    </div>

                    <button
                        onClick={handleGenerateMeals}
                        disabled={loadingMeals}
                        className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-violet-500 py-4 font-semibold transition hover:bg-violet-600"
                    >
                        {loadingMeals ? (
                            <>
                                <Loader2 className="animate-spin" />
                                Generating meals...
                            </>
                        ) : (
                            'Generate Meal Plan'
                        )}
                    </button>
                </div>
            </div>
        </div>
    )
}

/* ===== REUSABLE COMPONENTS ===== */

function Stat({ icon, label, value }) {
    return (
        <div className="flex items-center gap-3 rounded-lg bg-slate-800 p-4 ring-1 ring-slate-700">
            <div className="text-violet-400">{icon}</div>
            <div>
                <p className="text-xs text-slate-400">{label}</p>
                <p className="font-semibold text-white">{value}</p>
            </div>
        </div>
    )
}

function Macro({ label, value }) {
    return (
        <div className="rounded-lg bg-slate-800 p-4 ring-1 ring-slate-700">
            <p className="text-xs text-slate-400">{label}</p>
            <p className="text-lg font-semibold text-white">{value}</p>
        </div>
    )
}

export default TodayWorkout
