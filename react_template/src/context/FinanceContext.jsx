// src/context/FinanceContext.jsx
import React, { createContext, useState, useEffect } from 'react';
import { getTransactions, saveTransactions } from '../utils/localStorage';

export const FinanceContext = createContext();

export const FinanceProvider = ({ children }) => {
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load transactions from localStorage on initial render
  useEffect(() => {
    const loadTransactions = async () => {
      try {
        const savedTransactions = getTransactions();
        setTransactions(savedTransactions);
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

  // Save transactions to localStorage whenever they change
  useEffect(() => {
    if (!isLoading) {
      saveTransactions(transactions);
    }
  }, [transactions, isLoading]);

  // Add a new transaction
  const addTransaction = (transaction) => {
    setTransactions(prevTransactions => [...prevTransactions, transaction]);
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
      .filter(t => t.amount > 0)
      .reduce((sum, t) => sum + t.amount, 0);
      
    const expenses = transactions
      .filter(t => t.amount < 0)
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);
      
    const balance = income - expenses;
    
    return { income, expenses, balance };
  };

  return (
    <FinanceContext.Provider value={{
      transactions,
      isLoading,
      addTransaction,
      deleteTransaction,
      updateTransaction,
      clearTransactions,
      getFinancialSummary
    }}>
      {children}
    </FinanceContext.Provider>
  );
};