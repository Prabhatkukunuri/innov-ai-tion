import { useLocation, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { Loader2, Image as ImageIcon } from 'lucide-react'

function TodayMeals() {
    const location = useLocation()
    const navigate = useNavigate()

    // 🔑 FULL CONTEXTS PASSED FROM PREVIOUS PAGE
    const workoutResponse = location.state?.workoutResponse
    const mealsResponse = location.state?.mealsResponse

    const [uploadedImage, setUploadedImage] = useState(null)
    const [loading, setLoading] = useState(false)

    if (!workoutResponse || !mealsResponse) {
        return (
            <div className="flex min-h-screen flex-col items-center justify-center bg-slate-900 text-white">
                <p className="mb-4">Missing workout or meal data.</p>
                <button
                    onClick={() => navigate('/get-started')}
                    className="rounded bg-violet-500 px-4 py-2"
                >
                    Go Back
                </button>
            </div>
        )
    }

    function handleImageChange(e) {
        setUploadedImage(e.target.files[0])
    }

    function handleSubmitTracking() {
        const request3Payload = {
            workout_response: workoutResponse, // FULL workout JSON
            meals_response: mealsResponse,     // FULL meals JSON
            image: uploadedImage || null,
        }

        console.log('REQUEST 3 (TrackingLLM):', request3Payload)

        setLoading(true)

        // 🔁 simulate backend TrackingLLM request
        setTimeout(() => {
            setLoading(false)
            alert('TrackingLLM request sent (simulated)')
        }, 1500)
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-800 to-slate-900 px-6 py-10 text-white">
            <div className="mx-auto max-w-5xl space-y-10 rounded-2xl bg-slate-900/80 p-8 shadow-2xl">

                <h1 className="text-3xl font-extrabold text-violet-400">
                    Today’s Meals
                </h1>

                {/* ===== MEALS ===== */}
                {Object.entries(mealsResponse.meals).map(([mealKey, meal]) => (
                    <div
                        key={mealKey}
                        className="rounded-xl bg-slate-800 p-6 ring-1 ring-slate-700 space-y-6"
                    >
                        <h2 className="text-2xl font-bold text-violet-400 capitalize">
                            {mealKey.replace('_', ' ')}
                        </h2>

                        {/* Recipe Name */}
                        <p className="text-lg font-semibold text-white">
                            {meal.recipe.recipe_name}
                        </p>

                        {/* Ingredients */}
                        <div>
                            <p className="mb-2 text-sm text-slate-400">
                                Ingredients
                            </p>
                            <ul className="list-disc list-inside text-sm text-slate-300">
                                {meal.recipe.ingredients.map((ing, idx) => (
                                    <li key={idx}>
                                        {ing.item} — {ing.quantity_g} g
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* Steps */}
                        <div>
                            <p className="mb-2 text-sm text-slate-400">
                                Cooking Steps
                            </p>
                            <ol className="list-decimal list-inside text-sm text-slate-300 space-y-1">
                                {meal.recipe.steps.map((step, idx) => (
                                    <li key={idx}>{step}</li>
                                ))}
                            </ol>
                        </div>

                        {/* Macros */}
                        <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
                            <Macro label="Target kcal" value={meal.target_macros.calories.toFixed(2)} />
                            <Macro label="Actual kcal" value={meal.actual_macros.calories.toFixed(2)} />
                            <Macro label="Protein (g)" value={meal.actual_macros.protein.toFixed(2)} />
                            <Macro label="Carbs (g)" value={meal.actual_macros.carbs.toFixed(2)} />
                            <Macro label="Fats (g)" value={meal.actual_macros.fats.toFixed(2)} />
                        </div>

                       
                       
                    </div>
                ))}

                {/* ===== IMAGE UPLOAD ===== */}
                <div className="rounded-xl bg-slate-800 p-6 ring-1 ring-slate-700">
                    <h2 className="mb-3 text-xl font-bold text-violet-400">
                        Upload Meal Image
                    </h2>

                    <label className="flex cursor-pointer items-center gap-3 rounded-lg bg-slate-900 px-4 py-3 ring-1 ring-slate-700">
                        <ImageIcon className="text-violet-400" />
                        <span className="text-slate-300">
                            {uploadedImage ? uploadedImage.name : 'Choose image'}
                        </span>
                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleImageChange}
                            className="hidden"
                        />
                    </label>
                </div>

                {/* ===== SUBMIT REQUEST 3 ===== */}
                <button
                    onClick={handleSubmitTracking}
                    disabled={loading}
                    className="flex w-full items-center justify-center gap-2 rounded-lg bg-violet-500 py-4 font-semibold transition hover:bg-violet-600"
                >
                    {loading ? (
                        <>
                            <Loader2 className="animate-spin" />
                            Analyzing today’s progress...
                        </>
                    ) : (
                        'Submit Day for Tracking'
                    )}
                </button>
            </div>
        </div>
    )
}

/* ===== REUSABLE ===== */

function Macro({ label, value }) {
    return (
        <div className="rounded-lg bg-slate-900 p-4 ring-1 ring-slate-700">
            <p className="text-xs text-slate-400">{label}</p>
            <p className="text-lg font-semibold text-white">{value}</p>
        </div>
    )
}

export default TodayMeals
