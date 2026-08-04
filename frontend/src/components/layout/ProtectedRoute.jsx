/**
 * Guard for protected pages that require authentication.
 */
import React from 'react';
import { Navigate } from 'react-router-dom';
import useAuth from '../../hooks/useAuth.js';

export default function ProtectedRoute({ children }) {
  const { token, loading } = useAuth();
  if (loading) {
    return <div className="py-20 text-center">Loading...</div>;
  }
  if (!token) {
    return <Navigate to="/" replace />;
  }
  return children;
}
