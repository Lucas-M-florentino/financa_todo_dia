// src/App.jsx
import React, { useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import TransactionForm from './components/TransactionForm';
import Dashboard from './components/Dashboard';
import ChatInterface from './components/ChatInterface';
import { FinanceProvider } from './context/FinanceContext';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch(activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'transactions':
        return <TransactionForm />;
      case 'chat':
        return <ChatInterface />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <FinanceProvider>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Header />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
          <main className="flex-1 overflow-y-auto p-4 md:p-6">
            {renderContent()}
          </main>
        </div>
      </div>
    </FinanceProvider>
  );
}

export default App;