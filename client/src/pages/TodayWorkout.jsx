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
                recipe_name: 'Cheesy Chicken & Rice Scramble',
                ingredients: [
                    {
                        item: 'chicken breast',
                        quantity_g: 125,
                    },
                    {
                        item: 'white rice raw',
                        quantity_g: 65,
                    },
                    {
                        item: 'tomato',
                        quantity_g: 50,
                    },
                    {
                        item: 'olive oil',
                        quantity_g: 6,
                    },
                    {
                        item: 'onion',
                        quantity_g: 50,
                    },
                    {
                        item: 'cheese',
                        quantity_g: 10,
                    },
                ],
                steps: [
                    'Cook the white rice according to package instructions.',
                    'While the rice cooks, dice the chicken breast into small, bite-sized pieces.',
                    'Dice the onion and tomato.',
                    'Heat the olive oil in a non-stick pan over medium heat. Add the diced chicken and cook until browned and cooked through, about 5-7 minutes.',
                    'Add the diced onion to the pan and saut\u00e9 until softened, about 3-4 minutes.',
                    'Stir in the diced tomato and cook for another 2-3 minutes.',
                    'Add the cooked rice to the pan with the chicken and vegetables. Mix well.',
                    'Stir in the cheese until melted and combined. Serve immediately.',
                ],
            },
            target_macros: {
                calories: 525.0,
                protein_g: 37.5,
                carbs_g: 55.0,
                fats_g: 16.25,
            },
            actual_macros: {
                calories: 617.0699999999999,
                protein: 42.725500000000004,
                carbs: 47.4195,
                fats: 28.968499999999995,
            },
            status: 'success',
            attempts: 1,
        },
        post_workout: {
            recipe: {
                recipe_name: 'Savory Chicken & Tomato Rice',
                ingredients: [
                    {
                        item: 'chicken breast',
                        quantity_g: 150,
                    },
                    {
                        item: 'white rice raw',
                        quantity_g: 83,
                    },
                    {
                        item: 'tomato',
                        quantity_g: 100,
                    },
                    {
                        item: 'onion',
                        quantity_g: 50,
                    },
                    {
                        item: 'olive oil',
                        quantity_g: 10,
                    },
                ],
                steps: [
                    'Cook the white rice according to package instructions. Once cooked, set aside.',
                    'While the rice cooks, dice the chicken breast into bite-sized pieces. Chop the onion and tomato.',
                    'Heat the olive oil in a non-stick pan or skillet over medium heat.',
                    'Add the chopped onion to the pan and saut\u00e9 until it becomes translucent and softened, about 3-5 minutes.',
                    'Add the diced chicken breast to the pan and cook, stirring occasionally, until it is browned and cooked through, about 5-7 minutes.',
                    'Stir in the chopped tomato and cook for another 2-3 minutes until the tomato slightly softens.',
                    'Add the cooked white rice to the pan with the chicken and vegetables. Stir everything together thoroughly to combine all ingredients.',
                    'Serve immediately and enjoy your post-workout meal.',
                ],
            },
            target_macros: {
                calories: 630.0,
                protein_g: 45.0,
                carbs_g: 66.0,
                fats_g: 19.5,
            },
            actual_macros: {
                calories: 744.48,
                protein: 50.8681,
                carbs: 61.8869,
                fats: 32.140699999999995,
            },
            status: 'success',
            attempts: 1,
        },
        lunch: {
            recipe: {
                recipe_name: 'Mediterranean Chicken & Rice Skillet',
                ingredients: [
                    {
                        item: 'chicken breast',
                        quantity_g: 125,
                    },
                    {
                        item: 'white rice raw',
                        quantity_g: 68,
                    },
                    {
                        item: 'tomato',
                        quantity_g: 120,
                    },
                    {
                        item: 'onion',
                        quantity_g: 30,
                    },
                    {
                        item: 'olive oil',
                        quantity_g: 10,
                    },
                ],
                steps: [
                    'Rinse 68g of white rice. In a small pot, combine the rice with 136ml of water. Bring to a boil, then reduce heat to low, cover, and simmer for 15-20 minutes until water is absorbed. Let stand for 5 minutes, then fluff with a fork.',
                    'Dice 125g of chicken breast into bite-sized pieces. Chop 30g of onion and 120g of tomato.',
                    'Heat 5g of olive oil in a non-stick skillet over medium-high heat. Add the diced chicken and cook for 5-7 minutes, stirring occasionally, until browned and cooked through. Remove chicken from the skillet and set aside.',
                    'Add the remaining 5g of olive oil to the same skillet. Add the chopped onion and cook for 3-4 minutes until softened. Add the diced tomato and cook for another 3-5 minutes, until the tomato softens and releases its juices.',
                    'Return the cooked chicken to the skillet with the vegetables. Stir well to combine. Serve the chicken and vegetable mixture over the cooked white rice.',
                ],
            },
            target_macros: {
                calories: 525.0,
                protein_g: 37.5,
                carbs_g: 55.0,
                fats_g: 16.25,
            },
            actual_macros: {
                calories: 604.0300000000001,
                protein: 41.8726,
                carbs: 54.862399999999994,
                fats: 23.803199999999997,
            },
            status: 'success',
            attempts: 1,
        },
        dinner: {
            recipe: {
                recipe_name: 'One-Pan Chicken & Tomato Rice',
                ingredients: [
                    {
                        item: 'chicken breast',
                        quantity_g: 95,
                    },
                    {
                        item: 'white rice raw',
                        quantity_g: 45,
                    },
                    {
                        item: 'tomato',
                        quantity_g: 100,
                    },
                    {
                        item: 'olive oil',
                        quantity_g: 9,
                    },
                    {
                        item: 'onion',
                        quantity_g: 50,
                    },
                ],
                steps: [
                    'Rinse the white rice thoroughly. In a small pot, combine the 45g raw rice with 90ml of water. Bring to a boil, then reduce heat to low, cover, and simmer for 12-15 minutes, or until water is absorbed. Remove from heat and let it sit, covered, for 5 minutes.',
                    'Dice the chicken breast into bite-sized pieces. Chop the onion and dice the tomato.',
                    'Heat the olive oil in a non-stick skillet over medium-high heat. Add the chopped onion and cook until softened, about 3-4 minutes.',
                    'Add the diced chicken breast to the skillet and cook, stirring occasionally, until browned on all sides and cooked through, about 5-7 minutes.',
                    'Stir in the diced tomato and cook for another 2-3 minutes, until slightly softened.',
                    'Add the cooked rice to the skillet with the chicken and vegetables. Stir everything together gently to combine. Serve immediately.',
                ],
            },
            target_macros: {
                calories: 420.0,
                protein_g: 30.0,
                carbs_g: 44.0,
                fats_g: 13.0,
            },
            actual_macros: {
                calories: 609.6400000000001,
                protein: 32.8365,
                carbs: 57.2085,
                fats: 27.3605,
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
