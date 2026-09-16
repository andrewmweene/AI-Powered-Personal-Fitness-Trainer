/**
 * Top navigation bar with links and logout actions.
 */
import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from '../../context/AuthContext.jsx';
import { Dumbbell, LogOut, UserCircle } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useContext(AuthContext);
  const location = useLocation();
  const navClass = ({ isActive }) => `rounded-md px-3 py-2 transition ${isActive ? 'font-semibold text-primary underline decoration-2 underline-offset-8' : 'text-slate-700 hover:bg-slate-100'}`;

  return (
    <header className="border-b border-slate-200 bg-white shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div>
          <NavLink to="/" className="inline-flex items-center gap-2 text-lg font-semibold text-slate-900">
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-primary text-white"><Dumbbell className="h-4 w-4" /></span>
            AI Personal Trainer
          </NavLink>
        </div>
        <nav className="flex items-center gap-3 text-sm">
          {user ? (
            <>
              <NavLink to="/dashboard" className={navClass}>
                Dashboard
              </NavLink>
              <NavLink to="/plan" className={navClass}>
                Workout Plan
              </NavLink>
              <NavLink to="/exercise" className={navClass}>
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
              <div className="group relative">
                <button type="button" aria-label="Open profile menu" className="inline-flex items-center gap-2 rounded-md px-3 py-2 text-slate-700 hover:bg-slate-100">
                  <UserCircle className="h-5 w-5" />
                  <span className="hidden sm:inline">{user.username}</span>
                </button>
                <div className="invisible absolute right-0 top-full z-20 mt-2 w-56 rounded-2xl border border-slate-200 bg-white p-4 text-sm shadow-lg group-focus-within:visible group-hover:visible">
                  <p className="font-semibold text-slate-900">{user.username}</p>
                  <p className="mt-1 truncate text-slate-500">{user.email}</p>
                  <NavLink to="/onboarding?edit=1" className="mt-3 block font-medium text-primary hover:text-blue-700">Edit profile</NavLink>
                </div>
              </div>
            </>
          ) : (
            location.pathname !== '/' ? <NavLink to="/" className={navClass}>
              Login
            </NavLink> : null
          )}
        </nav>
      </div>
    </header>
  );
}
