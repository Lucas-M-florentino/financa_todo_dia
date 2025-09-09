// src/context/ProfileContext.jsx
import React, { createContext, useState, useEffect } from 'react';
import { getLocalProfile, saveLocalProfile } from '../utils/localStorage';
import { getUserProfile, register as saveProfileApi, setAuthToken } from '../utils/api';
import { useAuth } from './AuthContext';

export const ProfileContext = createContext();

export const ProfileProvider = ({ children }) => {
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const { user, isAuthenticated, loading: authLoading } = useAuth();

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      setAuthToken(token);
    }
  }, []);

  // Load profile from API on initial render
  useEffect(() => {
    // Aguardar o AuthContext carregar
    if (authLoading) return;
    
    // Se não estiver autenticado, não carregar perfil
    if (!isAuthenticated || !user?.email) {
      setIsLoading(false);
      return;
    }

    const loadProfile = async () => {
      try {
        const userEmail = user.email; // Obter email do AuthContext
        
        const savedProfile = await getUserProfile(userEmail); // Passar email como parâmetro
        const localProfile = getLocalProfile();
        
        if (!localProfile && savedProfile) {
          setProfile(savedProfile);
          saveLocalProfile(savedProfile);
        } else {
          setProfile(localProfile);
        }
      } catch (error) {
        console.error("Error loading profile:", error);
        setProfile(null);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadProfile();
  }, [isAuthenticated, user, authLoading]); // Dependências do useEffect

  // Save profile to API and localStorage when it changes
  const saveProfile = async (newProfile) => {
    try {
      const updatedProfile = await saveProfileApi(newProfile);
      setProfile(updatedProfile);
      saveLocalProfile(updatedProfile);
    } catch (error) {
      console.error('Error saving profile:', error);
      throw error;
    }
  };

  return (
    <ProfileContext.Provider value={{ profile, isLoading, saveProfile }}>
      {children}
    </ProfileContext.Provider>
  ); 
};