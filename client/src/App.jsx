import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { Toaster } from 'react-hot-toast'
import Homepage from './pages/Homepage'
import GetStarted from './pages/GetStarted'
import TodayWorkout from './pages/TodayWorkout'
import TodayMeals from './pages/TodayMeals'

function App() {
    return (
        <>
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<Homepage />} />
                    <Route path="/get-started" element={<GetStarted />} />
                    <Route path="/today-workout" element={<TodayWorkout />} />
                    <Route path="/today-meals" element={<TodayMeals />} />
                </Routes>
            </BrowserRouter>
            <Toaster
                position="top-center"
                gutter={12}
                containerStyle={{ margin: '8px' }}
                toastOptions={{
                    success: { duration: 3000 },
                    error: { duration: 5000 },
                    style: {
                        fontSize: '16px',
                        maxWidth: '500px',
                        padding: '16px 24px',
                        backgroundColor: 'bg-white',
                        color: 'var(--color-grey-700)',
                    },
                }}
            />
        </>
    )
}

export default App
