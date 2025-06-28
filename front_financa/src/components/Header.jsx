// src/components/Header.jsx
import React from 'react';

const Header = () => {
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
        <div className="hidden md:block">
          <p className="text-sm text-indigo-100">Seu assistente inteligente para gerenciamento financeiro</p>
        </div>
      </div>
    </header>
  );
};

export default Header;