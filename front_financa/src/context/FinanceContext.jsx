// src/context/FinanceContext.jsx
import React, { createContext, useState, useEffect } from "react";
import {
  getLocalTransactions,
  saveLocalTransactions,
  updateLocalTransaction,
  deleteLocalTransaction,
} from "../utils/localStorage";
import {
  saveTransactions,
  updateTransactionId,
  deleteTransactionId,
  getAllCategories,
  setAuthToken,
} from "../utils/api";

export const FinanceContext = createContext();

export const FinanceProvider = ({ children }) => {
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [categories, setCategories] = useState({ income: [], expense: [] });

  // Seta o token no axios sempre que a app iniciar
  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (token) {
      setAuthToken(token);
    }
  }, []);

  // Carrega só do localStorage
  useEffect(() => {
    const localTransactions = getLocalTransactions();
    setTransactions(Array.isArray(localTransactions) ? localTransactions : []);
    setIsLoading(false);
  }, []);

  // Busca categorias da API
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await getAllCategories();
        if (data?.income && data?.expense) {
          setCategories(data);
        } else {
          console.warn("Formato inesperado ao carregar categorias:", data);
          setCategories({ income: [], expense: [] });
        }
      } catch (error) {
        console.error("Erro ao buscar categorias:", error);
        setCategories({ income: [], expense: [] });
      }
    };

    fetchCategories();
  }, []);

  // Add a new transaction
  const addTransaction = async (transaction) => {
    try {
      const saved = await saveTransactions(transaction); // grava na API
      const updatedList = [...transactions, saved];
      setTransactions(updatedList);
      saveLocalTransactions(updatedList); // sincroniza local
    } catch (error) {
      console.error("Erro ao salvar transação:", error);
    }
  };

  // Delete a transaction by ID
  const deleteTransaction = async (id) => {
    try {
      await deleteTransactionId(id);
      const updated = transactions.filter((t) => t.id !== id);
      setTransactions(updated);
      deleteLocalTransaction(id);
    } catch (error) {
      console.error("Erro ao deletar transação:", error);
    }
  };

  // Update an existing transaction
  const updateTransaction = async (id, updatedTransaction) => {
    try {
      await updateTransactionId(id, updatedTransaction);
      const updated = transactions.map((t) =>
        t.id === id ? { ...t, ...updatedTransaction } : t
      );
      setTransactions(updated);
      updateLocalTransaction({ id, ...updatedTransaction });
    } catch (error) {
      console.error("Erro ao atualizar transação:", error);
    }
  };

  const clearTransactions = () => {
    setTransactions([]);
    saveLocalTransactions([]);
  };

  const getFinancialSummary = () => {
    const income = transactions
      .filter((t) => t.type === "income")
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);

    const expenses = transactions
      .filter((t) => t.type === "expense")
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);

    return { income, expenses, balance: income - expenses };
  };

  const contextValue = {
    transactions,
    categories,
    isLoading,
    addTransaction,
    deleteTransaction,
    updateTransaction,
    clearTransactions,
    getFinancialSummary,
  };

  return (
    <FinanceContext.Provider value={contextValue}>
      {children}
    </FinanceContext.Provider>
  );
};
