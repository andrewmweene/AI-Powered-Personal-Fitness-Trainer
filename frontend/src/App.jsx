/**
 * Application shell and routing setup.
 * Includes protected routes and a shared navbar.
 */
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext.jsx';
import Navbar from './components/layout/Navbar.jsx';
import ProtectedRoute from './components/layout/ProtectedRoute.jsx';
import Home from './pages/Home.jsx';
import Onboarding from './pages/Onboarding.jsx';
import Exercise from './pages/Exercise.jsx';
import Dashboard from './pages/Dashboard.jsx';
import WorkoutPlan from './pages/WorkoutPlan.jsx';

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-surface">
        <Navbar />
        <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/onboarding" element={<ProtectedRoute><Onboarding /></ProtectedRoute>} />
            <Route path="/exercise" element={<ProtectedRoute><Exercise /></ProtectedRoute>} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/plan" element={<ProtectedRoute><WorkoutPlan /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </AuthProvider>
  );
}

export default App;
