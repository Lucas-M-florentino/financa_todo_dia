// src/context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { loadTokenFromStorage, clearAuthToken } from '../utils/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  // Verifica se já está logado ao carregar a app
  useEffect(() => {
    console.log('🔍 Verificando autenticação...');
    
    const token = loadTokenFromStorage(); // Usa a nova função
    if (token) {
      console.log('✅ Token encontrado, usuário autenticado');
      setIsAuthenticated(true);
      // Aqui você poderia buscar dados do usuário se necessário
    } else {
      console.log('❌ Nenhum token encontrado');
    }
    setLoading(false);
  }, []);

  const login = (userData) => {
    console.log('✅ Login realizado com sucesso');
    setIsAuthenticated(true);
    setUser(userData);
  };

  const logout = () => {
    console.log('👋 Fazendo logout...');
    clearAuthToken(); // Usa a nova função
    setIsAuthenticated(false);
    setUser(null);
  };

  const value = {
    isAuthenticated,
    user,
    loading,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};