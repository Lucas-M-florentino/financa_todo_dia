// utils/api.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

let authToken = null;

const STORAGE_KEY = 'financeai_transactions';

// Permitir salvar o token na memória
export const setAuthToken = (token) => {
  authToken = token;
};

// Função helper para adicionar o header Authorization
const authHeaders = () => ({
  'Content-Type': 'application/json',
  ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
});

/**
 * Logs the user in by sending credentials to the API
 * @param {Object} credentials User credentials containing email and password
 * @returns {Promise<Object>} Promise that resolves to the login response
 */
export const login = async (credentials) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    
    const data = await response.json();
    console.log('Login response data:', data);
    
    // CORREÇÃO 1: Verificar ambos access_token e acces_token (typo comum)
    const token = data.access_token || data.acces_token || data.token;
    
    if (token) {
      // CORREÇÃO 2: Remover aspas extras e salvar corretamente
      const cleanToken = String(token).replace(/^["']|["']$/g, '');
      
      setAuthToken(cleanToken); // CORREÇÃO 3: Passar o token para a função
      localStorage.setItem('authToken', cleanToken); // CORREÇÃO 4: Salvar string limpa, não JSON
    }

    if (!response.ok) throw new Error('Login failed');
    return data;
  } catch (error) {
    console.error('Error during login:', error);
    throw error;
  }
};

// Função para carregar token do localStorage na inicialização
export const loadTokenFromStorage = () => {
  const token = localStorage.getItem('authToken');
  if (token) {
    // Remove aspas extras se existirem
    const cleanToken = token.replace(/^["']|["']$/g, '');
    setAuthToken(cleanToken);
    console.log('Token carregado do localStorage:', cleanToken);
    return cleanToken;
  }
  return null;
};

// Função para limpar token
export const clearAuthToken = () => {
  authToken = null;
  localStorage.removeItem('authToken');
  console.log('Token removido');
};

/**
 * Gets transactions from the API
 * @returns {Promise<Array>} Promise that resolves to array of transaction objects
 */
export const getTransactions = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions`, {
      headers: authHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch transactions');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching transactions:', error);
    return [];
  }
};

export const getAllCategories = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/categories`, {
      headers: authHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch categories');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching categories:', error);
    return [];
  }
};

/**
 * Saves transactions to the API
 * @param {Array} transactions Array of transaction objects
 * @returns {Promise<boolean>} Promise that resolves to success status
 */
export const saveTransactions = async (transaction) => {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions`, {
      method: 'POST',
      headers: authHeaders(), // CORREÇÃO 5: Usar authHeaders() consistentemente
      body: JSON.stringify(transaction), // CORREÇÃO 6: Remover spread operator desnecessário
    });

    if (!response.ok) {
      throw new Error('Failed to save transactions');
    }
    return true;
  } catch (error) {
    console.error('Error saving transactions:', error);
    return false;
  }
};

/**
 * Creates a new transaction
 * @param {Object} transaction Transaction object to create
 * @returns {Promise<Object>} Promise that resolves to the created transaction
 */
export const createTransaction = async (transaction) => {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions`, {
      method: 'POST',
      headers: authHeaders(), // CORREÇÃO 7: Usar authHeaders() consistentemente
      body: JSON.stringify(transaction),
    });

    if (!response.ok) {
      throw new Error('Failed to create transaction');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating transaction:', error);
    throw error;
  }
};

/**
 * Deletes a transaction
 * @param {number} id ID of the transaction to delete
 * @returns {Promise<boolean>} Promise that resolves to success status
 */
export const deleteTransactionId = async (id) => {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions/${id}`, {
      method: 'DELETE', // CORREÇÃO 8: Mover method para posição correta
      headers: authHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to delete transaction');
    }
    return true;
  } catch (error) {
    console.error('Error deleting transaction:', error);
    return false;
  }
};

/**
 * Updates a transaction
 * @param {number} id ID of the transaction to update
 * @param {Object} transaction Updated transaction object
 * @returns {Promise<Object>} Promise that resolves to the updated transaction
 */
export const updateTransactionId = async (id, transaction) => {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions/${id}`, {
      method: 'PUT',
      headers: authHeaders(), // CORREÇÃO 9: Usar authHeaders() consistentemente
      body: JSON.stringify(transaction),
    });

    if (!response.ok) {
      throw new Error('Failed to update transaction');
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating transaction:', error);
    throw error;
  }
};