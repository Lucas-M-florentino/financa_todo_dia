// src/context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from "react";
import {
  loadTokenFromStorage,
  clearAuthToken,
} from "../utils/api";
import {saveLocalProfile, clearLocalProfile, getLocalProfile} from "../utils/localStorage";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};


export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  // Verifica se já está logado ao carregar a app
  useEffect(() => {
    const init = async () => {
      const token = loadTokenFromStorage();
      if (!token) {
        setIsAuthenticated(false);
        setLoading(false);
        return;
      }

      // Decodificar token para obter dados do usuário
      const userData = getLocalProfile();
      if (userData) {
        setIsAuthenticated(true);
        setUser(userData); // Isso deve incluir o email
      } else {
        // Token inválido, limpar
        clearAuthToken();
        clearLocalProfile();
        setIsAuthenticated(false);
      }
      
      setLoading(false);
    };

    init();
  }, []);

  const login = (userData) => {
    setIsAuthenticated(true);
    setUser(userData);
    saveLocalProfile(userData);
    setLoading(false);
  };

  const logout = () => {
    clearAuthToken();
    clearLocalProfile();
    setIsAuthenticated(false);
    setUser(null);
  };

  const value = {
    isAuthenticated,
    user,
    loading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
};