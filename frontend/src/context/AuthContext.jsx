/**
 * Authentication context provider.
 * Restores user state from the token and supplies login/logout helpers.
 */
import React, { createContext, useEffect, useState } from 'react';
import { getMe, logout as logoutApi, refresh } from '../api/auth.js';
import { clearAccessToken, setAccessToken } from '../api/client.js';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function restore() {
      try {
        const restoredToken = await refresh();
        setAccessToken(restoredToken);
        setToken(restoredToken);
        const userData = await getMe();
        setUser(userData);
      } catch (error) {
        clearAccessToken();
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    restore();
  }, []);

  const login = (newToken, userData) => {
    setAccessToken(newToken);
    setToken(newToken);
    setUser(userData);
  };

  const logout = async () => {
    try {
      await logoutApi();
    } catch (error) {
      // Clear local auth state even if the server session has already expired.
    }
    clearAccessToken();
    setToken(null);
    setUser(null);
    window.location.href = '/';
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
