import React, { createContext, useContext, useState } from 'react';
import { API_BASE_URL } from './config';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [loading, setLoading] = useState(false);


  const login = async (credentials) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    localStorage.setItem('token', data.access_token);
  };


  const logout = () => {
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ login, logout, loading }}>

      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
