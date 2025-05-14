// src/components/TransactionForm.jsx
import React, { useState, useContext } from 'react';
import { FinanceContext } from '../context/FinanceContext';

const TransactionForm = () => {
  const { addTransaction } = useContext(FinanceContext);
  
  const initialState = {
    description: '',
    amount: '',
    type: 'expense',
    category: '',
    date: new Date().toISOString().split('T')[0]
  };
  
  const [formData, setFormData] = useState(initialState);
  const [feedback, setFeedback] = useState({ show: false, message: '', type: '' });
  
  const categories = {
    income: ['Salário', 'Freelance', 'Investimentos', 'Outros'],
    expense: ['Alimentação', 'Moradia', 'Transporte', 'Lazer', 'Saúde', 'Educação', 'Outros']
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validação
    if (!formData.description || !formData.amount || !formData.category) {
      setFeedback({ show: true, message: 'Por favor, preencha todos os campos', type: 'error' });
      return;
    }

    const amountValue = parseFloat(formData.amount);
    if (isNaN(amountValue) || amountValue <= 0) {
      setFeedback({ show: true, message: 'Valor inválido', type: 'error' });
      return;
    }
    
    // Criar transação
    const newTransaction = {
      id: Date.now().toString(),
      description: formData.description,
      amount: formData.type === 'expense' ? -amountValue : amountValue,
      category: formData.category,
      date: formData.date,
      createdAt: new Date().toISOString()
    };
    
    addTransaction(newTransaction);
    
    // Reset e feedback
    setFormData(initialState);
    setFeedback({ 
      show: true, 
      message: 'Transação registrada com sucesso!', 
      type: 'success' 
    });
    
    setTimeout(() => setFeedback({ show: false, message: '', type: '' }), 3000);
  };

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">Registrar Transação</h2>
      
      {feedback.show && (
        <div className={`p-3 rounded-md mb-4 ${
          feedback.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          {feedback.message}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700 font-medium mb-2" htmlFor="type">
            Tipo
          </label>
          <div className="flex space-x-4">
            <label className={`flex-1 flex items-center p-3 border rounded-md cursor-pointer ${
              formData.type === 'income' ? 'bg-green-100 border-green-400' : 'bg-white'
            }`}>
              <input
                type="radio"
                name="type"
                value="income"
                checked={formData.type === 'income'}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Receita</span>
            </label>
            
            <label className={`flex-1 flex items-center p-3 border rounded-md cursor-pointer ${
              formData.type === 'expense' ? 'bg-red-100 border-red-400' : 'bg-white'
            }`}>
              <input
                type="radio"
                name="type"
                value="expense"
                checked={formData.type === 'expense'}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Despesa</span>
            </label>
          </div>
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-700 font-medium mb-2" htmlFor="description">
            Descrição
          </label>
          <input
            type="text"
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Ex: Compra no supermercado"
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-700 font-medium mb-2" htmlFor="amount">
            Valor (R$)
          </label>
          <input
            type="number"
            id="amount"
            name="amount"
            value={formData.amount}
            onChange={handleChange}
            min="0.01"
            step="0.01"
            className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="0.00"
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-700 font-medium mb-2" htmlFor="category">
            Categoria
          </label>
          <select
            id="category"
            name="category"
            value={formData.category}
            onChange={handleChange}
            className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Selecione uma categoria</option>
            {categories[formData.type].map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>
        
        <div className="mb-6">
          <label className="block text-gray-700 font-medium mb-2" htmlFor="date">
            Data
          </label>
          <input
            type="date"
            id="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        
        <button
          type="submit"
          className={`w-full py-2 px-4 rounded-md text-white font-medium ${
            formData.type === 'income' ? 'bg-green-600 hover:bg-green-700' : 'bg-indigo-600 hover:bg-indigo-700'
          } transition duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
        >
          Registrar {formData.type === 'income' ? 'Receita' : 'Despesa'}
        </button>
      </form>
    </div>
  );
};

export default TransactionForm;