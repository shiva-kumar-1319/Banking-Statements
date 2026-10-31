import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [theme, setTheme] = useState(localStorage.getItem('banksense_theme') || 'dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('banksense_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const loadUser = async () => {
    const token = localStorage.getItem('banksense_access_token');
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const res = await authService.getProfile();
      setUser(res.data);
      if (res.data.profile?.theme) {
        setTheme(res.data.profile.theme);
      }
    } catch (err) {
      authService.logout();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUser();

    const handleLogoutEvent = () => {
      setUser(null);
    };

    window.addEventListener('banksense_auth_logout', handleLogoutEvent);
    return () => window.removeEventListener('banksense_auth_logout', handleLogoutEvent);
  }, []);

  const login = async (username, password) => {
    const res = await authService.login({ username, password });
    localStorage.setItem('banksense_access_token', res.data.access);
    localStorage.setItem('banksense_refresh_token', res.data.refresh);
    await loadUser();
    return res.data;
  };

  const register = async (userData) => {
    const res = await authService.register(userData);
    localStorage.setItem('banksense_access_token', res.data.tokens.access);
    localStorage.setItem('banksense_refresh_token', res.data.tokens.refresh);
    setUser(res.data.user);
    return res.data;
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const updateProfile = async (data) => {
    const res = await authService.updateProfile(data);
    setUser(res.data);
    return res.data;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        theme,
        toggleTheme,
        login,
        register,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

