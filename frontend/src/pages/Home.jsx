/**
 * Home page with login and register tabs.
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login as loginApi, register as registerApi, getMe } from '../api/auth.js';
import { getStatus } from '../api/onboarding.js';
import useAuth from '../hooks/useAuth.js';
import AlertBanner from '../components/ui/AlertBanner.jsx';
import Button from '../components/ui/Button.jsx';

export default function Home() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [tab, setTab] = useState('login');
  const [form, setForm] = useState({ username: '', email: '', password: '', confirmPassword: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (field) => (event) => {
    setForm({ ...form, [field]: event.target.value });
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      const token = await loginApi(form.username, form.password);
      localStorage.setItem('token', token);
      const userData = await getMe();
      login(token, userData);
      const statusData = await getStatus();
      if (statusData.onboarding_complete) {
        navigate('/dashboard');
      } else {
        navigate('/onboarding');
      }
    } catch (apiError) {
      setError(apiError.response?.data?.detail || 'Login failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);
    try {
      await registerApi({ username: form.username, email: form.email, password: form.password });
      setSuccess('Registration successful. Please log in.');
      setTab('login');
    } catch (apiError) {
      setError(apiError.response?.data?.detail || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl rounded-3xl bg-white p-8 shadow-lg sm:p-10">
      <div className="mb-6 flex gap-4 rounded-full bg-slate-100 p-2">
        <button
          type="button"
          onClick={() => setTab('login')}
          className={`rounded-full px-5 py-2 ${tab === 'login' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600'}`}
        >
          Login
        </button>
        <button
          type="button"
          onClick={() => setTab('register')}
          className={`rounded-full px-5 py-2 ${tab === 'register' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600'}`}
        >
          Register
        </button>
      </div>
      {error ? <AlertBanner type="error" message={error} onDismiss={() => setError('')} /> : null}
      {success ? <AlertBanner type="success" message={success} onDismiss={() => setSuccess('')} /> : null}
      {tab === 'login' ? (
        <form onSubmit={handleLogin} className="space-y-5">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-slate-700">Username</label>
            <input id="username" value={form.username} onChange={handleChange('username')} className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 focus:border-primary focus:outline-none" />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-700">Password</label>
            <input id="password" type="password" value={form.password} onChange={handleChange('password')} className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 focus:border-primary focus:outline-none" />
          </div>
          <Button type="submit" loading={loading} disabled={loading}>Login</Button>
        </form>
      ) : (
        <form onSubmit={handleRegister} className="space-y-5">
          <div>
            <label htmlFor="username-register" className="block text-sm font-medium text-slate-700">Username</label>
            <input id="username-register" value={form.username} onChange={handleChange('username')} className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 focus:border-primary focus:outline-none" />
          </div>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-slate-700">Email</label>
            <input id="email" type="email" value={form.email} onChange={handleChange('email')} className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 focus:border-primary focus:outline-none" />
          </div>
          <div>
            <label htmlFor="password-register" className="block text-sm font-medium text-slate-700">Password</label>
            <input id="password-register" type="password" value={form.password} onChange={handleChange('password')} className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 focus:border-primary focus:outline-none" />
          </div>
          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-700">Confirm Password</label>
            <input id="confirmPassword" type="password" value={form.confirmPassword} onChange={handleChange('confirmPassword')} className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 focus:border-primary focus:outline-none" />
          </div>
          <Button type="submit" variant="primary" loading={loading} disabled={loading}>Create account</Button>
        </form>
      )}
    </div>
  );
}
