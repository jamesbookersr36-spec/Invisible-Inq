import { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';

const AuthContext = createContext(null);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Check if token is expired
  const isTokenExpired = (token) => {
    try {
      const decoded = jwtDecode(token);
      return decoded.exp * 1000 < Date.now();
    } catch (error) {
      return true;
    }
  };

  // Load user from token on mount
  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (token && !isTokenExpired(token)) {
      const decoded = jwtDecode(token);
      // Check if user is admin
      if (decoded.is_admin) {
        setUser(decoded);
      } else {
        localStorage.removeItem('admin_token');
      }
    }
    setLoading(false);
  }, []);

  // Admin login
  const login = async (email, password) => {
    try {
      setError(null);
      const response = await fetch(`${API_BASE_URL}/api/auth/admin/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('admin_token', data.access_token);
        const decoded = jwtDecode(data.access_token);
        setUser(decoded);
        return { success: true };
      } else {
        setError(data.detail || 'Login failed');
        return { success: false, error: data.detail || 'Login failed' };
      }
    } catch (error) {
      const errorMessage = error.message || 'Network error during login';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Logout
  const logout = () => {
    localStorage.removeItem('admin_token');
    setUser(null);
    setError(null);
    navigate('/login');
  };

  // Get auth token
  const getToken = () => {
    return localStorage.getItem('admin_token');
  };

  // Check if user is authenticated
  const isAuthenticated = () => {
    return user !== null;
  };

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    getToken,
    isAuthenticated
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
