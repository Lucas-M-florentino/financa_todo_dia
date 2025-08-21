// src/components/Header.jsx
import React from 'react';
import { useAuth } from '../context/AuthContext';

const Header = () => {
  const { logout, user } = useAuth();

  const handleLogout = () => {
    if (window.confirm('Deseja realmente sair?')) {
      logout();
    }
  };

  return (
    <header className="bg-indigo-600 text-white shadow-md">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm3 1h6v4H7V5zm6 6H7v2h6v-2z" clipRule="evenodd" />
            <path d="M7 12h6v2H7v-2z" />
          </svg>
          <h1 className="text-xl font-bold">FinanceAI Manager</h1>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="hidden md:block text-center">
            <p className="text-sm text-indigo-100">Seu assistente inteligente para gerenciamento financeiro</p>
          </div>
          
          <div className="flex items-center space-x-3">
            {user && (
              <div className="hidden sm:block text-right">
                <p className="text-sm font-medium">{user.name || 'Usuário'}</p>
                <p className="text-xs text-indigo-200">{user.email}</p>
              </div>
            )}
            
            <button
              onClick={handleLogout}
              className="flex items-center space-x-1 text-sm text-indigo-100 hover:text-white px-3 py-2 rounded-md hover:bg-indigo-700 transition-colors duration-200"
              title="Sair do sistema"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span className="hidden sm:inline">Sair</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;