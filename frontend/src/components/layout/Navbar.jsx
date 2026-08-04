/**
 * Top navigation bar with links and logout actions.
 */
import React from 'react';
import { NavLink } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from '../../context/AuthContext.jsx';
import { LogOut } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useContext(AuthContext);

  return (
    <header className="border-b border-slate-200 bg-white shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div>
          <NavLink to="/" className="text-lg font-semibold text-slate-900">
            AI Personal Trainer
          </NavLink>
        </div>
        <nav className="flex items-center gap-3 text-sm">
          {user ? (
            <>
              <NavLink to="/dashboard" className="rounded-md px-3 py-2 text-slate-700 hover:bg-slate-100">
                Dashboard
              </NavLink>
              <NavLink to="/plan" className="rounded-md px-3 py-2 text-slate-700 hover:bg-slate-100">
                Workout Plan
              </NavLink>
              <NavLink to="/exercise" className="rounded-md px-3 py-2 text-slate-700 hover:bg-slate-100">
                Exercise
              </NavLink>
              <button
                type="button"
                onClick={logout}
                aria-label="Logout"
                className="inline-flex items-center gap-2 rounded-md bg-slate-50 px-3 py-2 text-slate-700 hover:bg-slate-100"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
            </>
          ) : (
            <NavLink to="/" className="rounded-md px-3 py-2 text-slate-700 hover:bg-slate-100">
              Login
            </NavLink>
          )}
        </nav>
      </div>
    </header>
  );
}
