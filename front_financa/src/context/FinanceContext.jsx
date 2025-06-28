// src/context/FinanceContext.jsx
import React, { createContext, useState, useEffect } from 'react';
// import { getTransactions, saveTransactions } from '../utils/localStorage';
import { getTransactions, saveTransactions } from '../utils/api';
/*
  Modificação: Não consultar transações anteriores.
  Remover o carregamento inicial de transações.
  Apenas enviar (salvar) transações quando elas mudarem.
*/
export const FinanceContext = createContext();

export const FinanceProvider = ({ children }) => {
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load transactions from api on initial render
  useEffect(() => {
    const loadTransactions = async () => {
      try {
        const savedTransactions = await getTransactions();
        console.log('Loaded transactions:', savedTransactions);
        setTransactions(Array.isArray(savedTransactions) ? savedTransactions : []);
      } catch (error) {
        console.error('Error loading transactions:', error);
        // Start with empty array if error occurs
        setTransactions([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadTransactions();
  }, []);

  // Add a new transaction
  const addTransaction = (transaction) => {
    saveTransactions([transaction])
      .then(() => {
        setTransactions(prevTransactions => [...prevTransactions, transaction]);
      })
      .catch(error => {
        console.error('Error saving transaction:', error);
      });
  };

  // Delete a transaction by ID
  const deleteTransaction = (id) => {
    setTransactions(prevTransactions => 
      prevTransactions.filter(transaction => transaction.id !== id)
    );
  };

  // Update an existing transaction
  const updateTransaction = (id, updatedTransaction) => {
    setTransactions(prevTransactions => 
      prevTransactions.map(transaction => 
        transaction.id === id ? { ...transaction, ...updatedTransaction } : transaction
      )
    );
  };

  // Clear all transactions
  const clearTransactions = () => {
    setTransactions([]);
  };

  // Calculate summary statistics
  const getFinancialSummary = () => {
    const income = transactions
      .filter(t => t.type === 'income')
      .reduce((sum, t) => sum + t.amount, 0);
      
    const expenses = transactions
      .filter(t => t.type === 'expense')
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);
      
    const balance = income - expenses;
    
    return { income, expenses, balance };
  };

  // Memoize the context value to avoid unnecessary re-renders
  const contextValue = React.useMemo(() => ({
    transactions,
    isLoading,
    addTransaction,
    deleteTransaction,
    updateTransaction,
    clearTransactions,
    getFinancialSummary
  }), [
    transactions,
    isLoading,
    addTransaction,
    deleteTransaction,
    updateTransaction,
    clearTransactions,
    getFinancialSummary
  ]);

  return (
    <FinanceContext.Provider value={contextValue}>
      {children}
    </FinanceContext.Provider>
  );
};