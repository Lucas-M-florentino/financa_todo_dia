// src/context/ProfileContext.jsx
import React, { createContext, useState, useEffect } from 'react';
import { getLocalProfile, saveLocalProfile } from '../utils/localStorage';
import { getUserProfile, saveProfile as saveProfileApi, setAuthToken } from '../utils/api';

export const ProfileContext = createContext();

export const ProfileProvider = ({ children }) => {
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      setAuthToken(token);
    }
  }, []);

  // Load profile from API on initial render
  useEffect(() => {
    const loadProfile = async () => {
      try {
        const savedProfile = await getUserProfile();
        const localProfile = getLocalProfile();

        // If localStorage is empty, use API data
        if (!localProfile && savedProfile) {
          setProfile(savedProfile);
          saveLocalProfile(savedProfile);
        } else {
          // If localStorage has data, prefer it
          setProfile(localProfile);
        }
      } catch (error) {
        console.error('Error loading profile:', error);
        // Start with null if error occurs
        setProfile(null);
      } finally {
        setIsLoading(false);
      }
    };

    loadProfile();
  }, []);

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