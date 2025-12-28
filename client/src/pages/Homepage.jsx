import { ChartNoAxesCombined, Database } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

function Homepage() {
    const navigate = useNavigate()
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-800 to-slate-900 font-sans text-white">
            <header className="flex w-full items-center justify-between border-b border-slate-700 bg-slate-900/70 px-8 py-5 text-white shadow-md backdrop-blur-md">
                <h1 className="text-2xl font-bold tracking-wide text-violet-400">
                    FitAI
                </h1>
                <div className="flex items-center gap-6 text-white/80">
                    <h2 className="cursor-pointer transition hover:text-violet-300">
                        How it works
                    </h2>
                    <h2 className="cursor-pointer transition hover:text-violet-300">
                        Contact
                    </h2>
                    <span className="text-sm font-medium opacity-70">
                        Beta v1.0
                    </span>
                </div>
            </header>

            <main className="flex flex-col items-center justify-center px-6 py-24 text-center">
                <h2 className="mb-6 text-4xl font-extrabold tracking-tight text-white drop-shadow-lg md:text-5xl">
                    Your Personalized Fitness & Nutrition Companion
                </h2>
                <p className="max-w-2xl text-lg leading-relaxed text-slate-300">
                    <strong className="text-violet-400">FitAI</strong> adapts
                    workouts, meals, and recovery plans to your body, goals, and
                    experience level — using intelligent, data-driven feedback
                    every single day.
                </p>

                <div className="mt-10 flex flex-wrap gap-4">
                    <button
                        onClick={() => navigate('/get-started')}
                        className="rounded-lg bg-white px-6 py-3 text-sm font-semibold text-slate-900 shadow-md transition hover:scale-105 hover:bg-gray-200"
                    >
                        Get Started
                    </button>
                    <button className="rounded-lg bg-violet-500 px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:scale-105 hover:bg-violet-600">
                        Build My Plan
                    </button>
                </div>
            </main>

            <section className="grid grid-cols-1 gap-12 px-8 py-10 md:grid-cols-2 md:px-28">
                <div className="flex flex-col justify-center rounded-xl bg-slate-800/70 p-6 shadow-inner">
                    <h2 className="mb-4 inline-flex w-fit items-center gap-2 border-b border-violet-500 pb-2 text-2xl font-bold text-violet-400">
                        <ChartNoAxesCombined />
                        How FitAI Works
                    </h2>
                    <ul className="text-md list-none space-y-4 leading-relaxed text-slate-300">
                        <li>
                            Start by entering your{' '}
                            <strong className="text-white">
                                name, current weight, fitness goal, and
                                experience level
                            </strong>
                            .
                        </li>
                        <li>
                            FitAI breaks your goal into{' '}
                            <strong className="text-white">
                                daily workouts, weekly targets, and monthly
                                milestones
                            </strong>
                            .
                        </li>
                        <li>
                            Your completed workouts and meals are tracked to
                            continuously refine intensity, nutrition, and
                            recovery.
                        </li>
                    </ul>
                </div>

                <div className="flex flex-col justify-center rounded-xl bg-slate-800/70 p-6 shadow-inner">
                    <h2 className="mb-4 inline-flex w-fit items-center gap-2 border-b border-violet-500 pb-2 text-2xl font-bold text-violet-400">
                        <Database />
                        Why Use FitAI?
                    </h2>
                    <ul className="text-md list-none space-y-4 leading-relaxed text-slate-300">
                        <li>
                            Delivers{' '}
                            <strong className="text-white">
                                adaptive workouts
                            </strong>{' '}
                            based on your experience level — beginner,
                            intermediate, or pro.
                        </li>
                        <li>
                            Generates{' '}
                            <strong className="text-white">
                                meal plans aligned with your workouts
                            </strong>{' '}
                            using real nutrition data.
                        </li>
                        <li>
                            Tracks your progress over time and intelligently
                            adjusts future workouts and calorie targets.
                        </li>
                    </ul>
                </div>
            </section>

            <footer className="bg-slate-950 py-6 text-center text-sm text-slate-400">
                © 2025 FitAI — Train smarter, not harder.
            </footer>
        </div>
    )
}

export default Homepage
