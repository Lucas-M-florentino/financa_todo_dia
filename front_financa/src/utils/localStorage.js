// src/utils/localStorage.js
const STORAGE_KEY = 'financeai_transactions';

/**
 * Gets transactions from localStorage
 * @returns {Array} Array of transaction objects
 */
export const getLocalTransactions = () => {
  try {
    const transactions = localStorage.getItem(STORAGE_KEY);
    return transactions ? JSON.parse(transactions) : [];
  } catch (error) {
    console.error('Error retrieving transactions from localStorage:', error);
    return [];
  }
};

export const getLocalProfile = () => {
  try {
    const profile = localStorage.getItem('financeai_profile');
    return profile ? JSON.parse(profile) : null;
  } catch (error) {
    console.error('Error retrieving profile from localStorage:', error);
    return null;
  }
};

export const saveLocalProfile = (profile) => {
  try {
    localStorage.setItem('financeai_profile', JSON.stringify(profile));
    return true;
  } catch (error) {
    console.error('Error saving profile to localStorage:', error);
    return false;
  }
};

export const clearLocalProfile = () => {
  try {
    localStorage.removeItem('financeai_profile');
     return true;
  } catch (error) {
    console.error('Error clearing profile from localStorage:', error);
    return false;
  }
};

/**
 * Saves transactions to localStorage
 * @param {Array} transactions Array of transaction objects
 * @returns {boolean} Success status
 */
export const saveLocalTransactions = (transactions) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(transactions));
    return true;
  } catch (error) {
    console.error('Error saving transactions to localStorage:', error);
    return false;
  }
};
/**
 * Updates a specific transaction in localStorage
 * @param {Object} updatedTransaction Transaction object with updated data
 * @returns {boolean} Success status
 */
export const updateLocalTransaction = (updatedTransaction) => {
  try {
    const transactions = getLocalTransactions();
    const index = transactions.findIndex(t => t.id === updatedTransaction.id);
    if (index !== -1) {
      transactions[index] = updatedTransaction;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(transactions));
      return true;
    } else {
      console.warn('Transaction not found for update:', updatedTransaction.id);
      return false;
    }
  } catch (error) {
    console.error('Error updating transaction in localStorage:', error);
    return false;
  }
};

/**
 * Deletes a specific transaction from localStorage
 * @param {number} id ID of the transaction to delete
 * @returns {boolean} Success status
 */
export const deleteLocalTransaction = (id) => {
  try {
    const transactions = getLocalTransactions();
    const updatedTransactions = transactions.filter(t => t.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedTransactions));
    return true;
  } catch (error) {
    console.error('Error deleting transaction from localStorage:', error);
    return false;
  }
};

/**
 * Clears all transaction data from localStorage
 * @returns {boolean} Success status
 */
export const clearLocalTransactions = () => {
  try {
    localStorage.removeItem(STORAGE_KEY);
    return true;
  } catch (error) {
    console.error('Error clearing transactions from localStorage:', error);
    return false;
  }
};

/**
 * Exports transactions as JSON file for download
 * @param {Array} transactions Array of transaction objects
 */
export const exportLocalTransactionsToJson = (transactions) => {
  try {
    const dataStr = JSON.stringify(transactions, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `finance_data_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    linkElement.remove();
  } catch (error) {
    console.error('Error exporting transactions:', error);
    return false;
  }
};

/**
 * Imports transactions from JSON file
 * @param {File} file JSON file object
 * @returns {Promise<Array>} Promise resolving to array of transactions
 */
export const importLocalTransactionsFromJson = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (event) => {
      try {
        const transactions = JSON.parse(event.target.result);
        resolve(transactions);
      } catch (error) {
        reject(new Error('Invalid JSON file format'));
      }
    };
    
    reader.onerror = () => {
      reject(new Error('Error reading file'));
    };
    
    reader.readAsText(file);
  });
};