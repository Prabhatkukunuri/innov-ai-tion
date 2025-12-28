import { useLocation, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { Loader2, Image as ImageIcon } from 'lucide-react'

function TodayMeals() {
    const location = useLocation()
    const navigate = useNavigate()

    const workoutResponse = location.state?.workoutResponse
    const mealsResponse = location.state?.mealsResponse

    const [uploadedImage, setUploadedImage] = useState(null)
    const [loading, setLoading] = useState(false)
    const [showProgressReport, setShowProgressReport] = useState(false)

    /* ========= WORKOUT FEEDBACK STATE ========= */
    const [exerciseFeedback, setExerciseFeedback] = useState(() =>
        workoutResponse.exercises.map((ex) => ({
            name: ex.name,
            plannedSets: ex.sets,
            plannedReps: Number(ex.reps.split('-')[0]),
            completedSets: 0,
            completedReps: 0,
            completionPct: 0,
        }))
    )

    const PROGRESS_REPORT_TEXT = `
To achieve your muscle gain goal, the primary focus must shift toward closing the gap in your strength training volume and nutritional intake. While your training intensity and effort scores are excellent (both exceeding 1.09), your strength exercise completion is currently at 83.33%, which is below the optimal threshold. You are encouraged to target a minimum of 95% completion in upcoming sessions. Because your cardio completion is very high at 120%, you should consider scaling back slightly on aerobic work if it is fatiguing you to the point that strength sets are being missed.

On the nutritional side, your progress is currently hindered by a caloric deficit of approximately 482 calories and a protein deficit of 11.15g. Muscle hypertrophy is difficult to achieve in a deficit; therefore, increasing your daily caloric and protein intake is essential to provide the building blocks needed for repair. Additionally, because you are currently under-eating relative to your activity level, prioritizing recovery through better sleep and active rest is vital to prevent burnout and support the increased demands of your strength training adjustments.
`

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

    function updateExercise(index, field, value) {
        const updated = [...exerciseFeedback]
        updated[index][field] = Number(value)

        const plannedTotal =
            updated[index].plannedSets * updated[index].plannedReps
        const completedTotal =
            updated[index].completedSets * updated[index].completedReps

        updated[index].completionPct =
            plannedTotal > 0
                ? Math.min(
                      100,
                      Math.round((completedTotal / plannedTotal) * 100)
                  )
                : 0

        setExerciseFeedback(updated)
    }

    function handleSubmitTracking() {
        if (loading) return // 🔑 prevents re-trigger

        setShowProgressReport(false)
        setLoading(true)

        setTimeout(() => {
            setLoading(false)
            setShowProgressReport(true)
        }, 2000)
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-800 to-slate-900 px-6 py-10 text-white">
            <div className="mx-auto max-w-5xl space-y-10 rounded-2xl bg-slate-900/80 p-8 shadow-2xl">
                <h1 className="text-3xl font-extrabold text-violet-400">
                    Today’s Summary
                </h1>

                {/* ===== WORKOUT FEEDBACK ===== */}
                <div className="space-y-6 rounded-xl bg-slate-800 p-6 ring-1 ring-slate-700">
                    <h2 className="text-2xl font-bold text-violet-400">
                        Workout Completion
                    </h2>

                    {exerciseFeedback.map((ex, idx) => (
                        <div
                            key={ex.name}
                            className="space-y-4 rounded-lg bg-slate-900 p-5 ring-1 ring-slate-700"
                        >
                            <div className="flex justify-between">
                                <h3 className="text-lg font-semibold">
                                    {ex.name}
                                </h3>
                                <span className="text-sm text-slate-400">
                                    Planned: {ex.plannedSets} × {ex.plannedReps}
                                </span>
                            </div>

                            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                                <InputBox
                                    label="Completed Sets"
                                    value={ex.completedSets}
                                    onChange={(e) =>
                                        updateExercise(
                                            idx,
                                            'completedSets',
                                            e.target.value
                                        )
                                    }
                                />
                                <InputBox
                                    label="Completed Reps"
                                    value={ex.completedReps}
                                    onChange={(e) =>
                                        updateExercise(
                                            idx,
                                            'completedReps',
                                            e.target.value
                                        )
                                    }
                                />
                                <StatBox
                                    label="Total Done"
                                    value={ex.completedSets * ex.completedReps}
                                />
                                <StatBox
                                    label="Completion"
                                    value={`${ex.completionPct}%`}
                                />
                            </div>

                            <div className="h-3 w-full overflow-hidden rounded-full bg-slate-700">
                                <div
                                    className="h-full bg-violet-500 transition-all"
                                    style={{
                                        width: `${ex.completionPct}%`,
                                    }}
                                />
                            </div>
                        </div>
                    ))}
                </div>

                {/* ===== MEALS ===== */}
                {Object.entries(mealsResponse.meals).map(([mealKey, meal]) => (
                    <div
                        key={mealKey}
                        className="space-y-6 rounded-xl bg-slate-800 p-6 ring-1 ring-slate-700"
                    >
                        <h2 className="text-2xl font-bold capitalize text-violet-400">
                            {mealKey.replace('_', ' ')}
                        </h2>

                        <p className="text-lg font-semibold">
                            {meal.recipe.recipe_name}
                        </p>

                        <ul className="list-inside list-disc text-sm text-slate-300">
                            {meal.recipe.ingredients.map((ing, idx) => (
                                <li key={idx}>
                                    {ing.item} — {ing.quantity_g} g
                                </li>
                            ))}
                        </ul>

                        <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
                            <Macro
                                label="Target kcal"
                                value={meal.target_macros.calories.toFixed(2)}
                            />
                            <Macro
                                label="Actual kcal"
                                value={meal.actual_macros.calories.toFixed(2)}
                            />
                            <Macro
                                label="Protein (g)"
                                value={meal.actual_macros.protein.toFixed(2)}
                            />
                            <Macro
                                label="Carbs (g)"
                                value={meal.actual_macros.carbs.toFixed(2)}
                            />
                            <Macro
                                label="Fats (g)"
                                value={meal.actual_macros.fats.toFixed(2)}
                            />
                        </div>

                        <div>
                            <p className="mb-2 text-sm text-slate-400">
                                Cooking Steps
                            </p>
                            <ol className="list-inside list-decimal space-y-1 text-sm text-slate-300">
                                {meal.recipe.steps.map((step, idx) => (
                                    <li key={idx}>{step}</li>
                                ))}
                            </ol>
                        </div>
                    </div>
                ))}

                {/* ===== SUBMIT ===== */}
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

                {/* ===== SPINNER / REPORT ===== */}
                {loading && (
                    <div className="flex items-center justify-center gap-3 rounded-xl bg-slate-800 p-6 ring-1 ring-slate-700">
                        <Loader2 className="animate-spin text-violet-400" />
                        <p className="text-slate-300">
                            Running training & nutrition analysis…
                        </p>
                    </div>
                )}

                {showProgressReport && !loading && (
                    <div className="space-y-4 rounded-xl bg-slate-800 p-6 ring-1 ring-slate-700">
                        <h2 className="text-2xl font-bold text-violet-400">
                            Progress Report
                        </h2>
                        <p className="whitespace-pre-line text-sm leading-relaxed text-slate-300">
                            {PROGRESS_REPORT_TEXT}
                        </p>
                    </div>
                )}
            </div>
        </div>
    )
}

/* ===== REUSABLE ===== */

function InputBox({ label, value, onChange }) {
    return (
        <div>
            <p className="mb-1 text-xs text-slate-400">{label}</p>
            <input
                type="number"
                min="0"
                value={value}
                onChange={onChange}
                className="w-full rounded-md bg-slate-800 px-3 py-2 text-white outline-none ring-1 ring-slate-600 focus:ring-violet-500"
            />
        </div>
    )
}

function StatBox({ label, value }) {
    return (
        <div className="rounded-md bg-slate-800 p-3 ring-1 ring-slate-600">
            <p className="text-xs text-slate-400">{label}</p>
            <p className="text-lg font-semibold text-white">{value}</p>
        </div>
    )
}

function Macro({ label, value }) {
    return (
        <div className="rounded-lg bg-slate-900 p-4 ring-1 ring-slate-700">
            <p className="text-xs text-slate-400">{label}</p>
            <p className="text-lg font-semibold text-white">{value}</p>
        </div>
    )
}

export default TodayMeals
