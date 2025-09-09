// src/App.jsx
import React, { useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import TransactionForm from './components/TransactionForm';
import Dashboard from './components/Dashboard';
import ChatInterface from './components/ChatInterface';
import Login from './pages/Login';
import Profile from './pages/Profile';
import { FinanceProvider } from './context/FinanceContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProfileProvider } from './context/ProfileContext';

// Componente interno que usa o contexto de auth
const AppContent = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const { isAuthenticated, loading, login } = useAuth();

  const renderContent = () => {
    switch(activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'transactions':
        return <TransactionForm />;
      case 'chat':
        return <ChatInterface />;
      // case 'profile':
      //   return <Profile />
      default:
        return <Dashboard />;
    }
  };

  // Mostra loading enquanto verifica autenticação
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-lg">Carregando...</div>
      </div>
    );
  }

  // Se não está logado, mostra tela de login
  if (!isAuthenticated) {
    return <Login onLogin={login} />;
  }

  // Se está logado, mostra a aplicação normal
  return (
     <FinanceProvider>
      {/* <ProfileProvider> */}
        <div className="min-h-screen bg-gray-50 flex flex-col">
          <Header />
          <div className="flex flex-1 overflow-hidden">
            <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
            <main className="flex-1 overflow-y-auto p-4 md:p-6">
              {renderContent()}
            </main>
          </div>
        </div>
      {/* </ProfileProvider> */}
    </FinanceProvider>
  );
};

// Componente principal que provê o contexto
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;