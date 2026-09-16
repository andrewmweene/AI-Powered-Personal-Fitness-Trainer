/**
 * Home page with login and register tabs.
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login as loginApi, register as registerApi, getMe } from '../api/auth.js';
import { getStatus } from '../api/onboarding.js';
import useAuth from '../hooks/useAuth.js';
import AlertBanner from '../components/ui/AlertBanner.jsx';
import Button from '../components/ui/Button.jsx';

const DEMO_USER = {
  username: 'testuser',
  email: 'test@example.com',
  password: 'FitTrainer123!',
};

export default function Home() {
  const navigate = useNavigate();
  const { login, token } = useAuth();
  const [tab, setTab] = useState('login');
  const [form, setForm] = useState({ username: 'testuser', email: 'test@example.com', password: 'FitTrainer123!', confirmPassword: 'FitTrainer123!' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token) return;

    const redirectIfLoggedIn = async () => {
      try {
        const statusData = await getStatus();
        if (statusData.onboarding_complete) {
          navigate('/dashboard', { replace: true });
        } else {
          navigate('/onboarding', { replace: true });
        }
      } catch (error) {
        navigate('/onboarding', { replace: true });
      }
    };

    redirectIfLoggedIn();
  }, [token, navigate]);

  const handleChange = (field) => (event) => {
    setForm({ ...form, [field]: event.target.value });
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      const token = await loginApi(form.username, form.password);
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

  const handleDemoLogin = async () => {
    setForm({ ...DEMO_USER, confirmPassword: DEMO_USER.password });
    setError('');
    setSuccess('');
    setTab('login');
    setLoading(true);
    try {
      const token = await loginApi(DEMO_USER.username, DEMO_USER.password);
      const userData = await getMe();
      login(token, userData);
      const statusData = await getStatus();
      if (statusData.onboarding_complete) {
        navigate('/dashboard');
      } else {
        navigate('/onboarding');
      }
    } catch (apiError) {
      setError(apiError.response?.data?.detail || 'Demo login failed.');
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
          <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
            Demo account ready: <strong>testuser</strong> / <strong>FitTrainer123!</strong>
          </div>
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-slate-700">Username</label>
            <input id="username" value={form.username} onChange={handleChange('username')} className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 focus:border-primary focus:outline-none" />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-700">Password</label>
            <input id="password" type="password" value={form.password} onChange={handleChange('password')} className="mt-2 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 focus:border-primary focus:outline-none" />
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Button type="submit" loading={loading} disabled={loading} className="flex-1">Login</Button>
            <Button type="button" variant="secondary" onClick={handleDemoLogin} disabled={loading} className="flex-1">Use demo account</Button>
          </div>
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
