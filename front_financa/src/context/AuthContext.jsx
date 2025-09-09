// src/context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from "react";
import {
  loadTokenFromStorage,
  clearAuthToken,
  getUserProfile,
} from "../utils/api";

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
  const [profile, setProfile] = useState(null);

  // Verifica se já está logado ao carregar a app
  useEffect(() => {
    const checkAuth = async () => {
      console.log("🔍 Verificando autenticação...");

      const token = loadTokenFromStorage();
      if (!token) {
        console.log("❌ Nenhum token encontrado");
        setIsAuthenticated(false);
        setLoading(false);
        return;
      }

      try {
        const profileData = await getUserProfile();
        setProfile(profileData);
        setIsAuthenticated(true);
        console.log("✅ Token válido, usuário autenticado");
      } catch (err) {
        console.error("❌ Erro ao buscar perfil, token inválido:", err);
        clearAuthToken();
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = (userData) => {
    console.log("✅ Login realizado com sucesso");
    setIsAuthenticated(true);
    setUser(userData);
  };

  const logout = () => {
    console.log("👋 Fazendo logout...");
    clearAuthToken();
    setIsAuthenticated(false);
    setUser(null);
    setProfile(null);
  };

  const value = {
    isAuthenticated,
    user,
    profile,
    loading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
};
