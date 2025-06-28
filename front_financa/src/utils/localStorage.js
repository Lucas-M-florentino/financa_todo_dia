// src/utils/localStorage.js
const STORAGE_KEY = 'financeai_transactions';

/**
 * Gets transactions from localStorage
 * @returns {Array} Array of transaction objects
 */
export const getTransactions = () => {
  try {
    const transactions = localStorage.getItem(STORAGE_KEY);
    return transactions ? JSON.parse(transactions) : [];
  } catch (error) {
    console.error('Error retrieving transactions from localStorage:', error);
    return [];
  }
};

/**
 * Saves transactions to localStorage
 * @param {Array} transactions Array of transaction objects
 * @returns {boolean} Success status
 */
export const saveTransactions = (transactions) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(transactions));
    return true;
  } catch (error) {
    console.error('Error saving transactions to localStorage:', error);
    return false;
  }
};

/**
 * Clears all transaction data from localStorage
 * @returns {boolean} Success status
 */
export const clearTransactions = () => {
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
export const exportTransactionsToJson = (transactions) => {
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
export const importTransactionsFromJson = (file) => {
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