

// Use environment variables instead of .env
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/**
 * Gets transactions from the API
 * @returns {Promise<Array>} Promise that resolves to array of transaction objects
 */
export const getTransactions = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions`);
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
    const response = await fetch(`${API_BASE_URL}/categories`);
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
  console.log('Saving transactions to API:', transaction);
  console.log('typeof transactions:', typeof transaction);
  try {
    const response = await fetch(`${API_BASE_URL}/transactions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(...transaction),
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
      headers: {
        'Content-Type': 'application/json',
      },
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
export const deleteTransaction = async (id) => {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions/${id}`, {
      method: 'DELETE',
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
export const updateTransaction = async (id, transaction) => {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
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