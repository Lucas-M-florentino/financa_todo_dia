// src/components/Dashboard.jsx
import React, { useContext, useState, useMemo } from 'react';
import { FinanceContext } from '../context/FinanceContext';

const Dashboard = () => {
  const { transactions, deleteTransaction } = useContext(FinanceContext);
  const [timeFilter, setTimeFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [filterStartDate, setFilterStartDate] = useState(null);
  const [filterEndDate, setFilterEndDate] = useState(null);
  
  // Ensure transactions is always an array
  const safeTransactions = Array.isArray(transactions) ? transactions : [];

  // Filter transactions based on selected time period
  const filteredTransactions = useMemo(() => {
    let filtered = [...safeTransactions];
    
    // Time filter
    if (timeFilter !== 'all' || filterEndDate || filterStartDate) {
      const now = new Date();
      let startDate;
      
      let day;
      switch (timeFilter) {
        case 'month':
          startDate = new Date(now.getFullYear(), now.getMonth(), 1);
          break;
        case 'week':
          day = now.getDay();
          startDate = new Date(now);
          startDate.setDate(now.getDate() - day);
          break;
        case 'today':
          startDate = new Date(now.setHours(0, 0, 0, 0));
          break;
        case 'last_month':
          startDate = new Date(now.getFullYear(), now.getMonth() - 1, 1);
          break;
        case 'custom':
         if (filterStartDate || filterEndDate) {
            filtered = filtered.filter(transaction => {
              const transactionDate = new Date(transaction.date);
              
              // Aplicar filtro de data inicial se especificada
              if (filterStartDate) {
                const start = new Date(filterStartDate);
                start.setHours(0, 0, 0, 0); // Início do dia
                if (transactionDate < start) return false;
              }
              
              // Aplicar filtro de data final se especificada
              if (filterEndDate) {
                const end = new Date(filterEndDate);
                end.setHours(23, 59, 59, 999); // Final do dia
                if (transactionDate > end) return false;
              }
              
              return true;
            });
            console.log('Custom filter applied:', filterStartDate, filterEndDate);
          }
          break;
        default:
          startDate = null;
      }
      
      if (startDate) {
        filtered = filtered.filter(transaction => 
          new Date(transaction.date) >= startDate
        );
      }      
    }
    
    // Category filter
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(transaction => 
        transaction.category_name === categoryFilter
      );
    }
    
    return filtered;
  }, [transactions, timeFilter, categoryFilter]);

  // Calculate summary data
  const summary = useMemo(() => {
    const income = filteredTransactions
      .filter(t => t.type === 'income')
      .reduce((sum, t) => sum + t.amount, 0);
      
    const expenses = filteredTransactions
      .filter(t => t.type === 'expense')
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);
      
    const balance = income - expenses;
    
    // Get categories for expenses
    const expensesByCategory = {};
    filteredTransactions
      .filter(t => t.type === 'expense')
      .forEach(t => {
        expensesByCategory[t.category_name] = (expensesByCategory[t.category_name] || 0) + Math.abs(t.amount);
      });


    return {
      income, 
      expenses, 
      balance,
      expensesByCategory
    };
  }, [filteredTransactions]);

  const uniqueCategories = useMemo(() => {
    const categories = new Set();
    safeTransactions.forEach(t => categories.add(t.category_name));
    return ['all', ...Array.from(categories)];
  }, [safeTransactions]);

  // Create simplified bar chart for expenses by category
  const renderBarChart = () => {
    if (Object.keys(summary.expensesByCategory).length === 0) {
      return <p className="text-gray-500">Sem dados de despesas para exibir</p>;
    }
    
    const maxValue = Math.max(...Object.values(summary.expensesByCategory));
    
    return (
      <div className="space-y-3">
        {Object.entries(summary.expensesByCategory).map(([category_name, value]) => (
          <div key={category_name} className="flex flex-col">
            <div className="flex justify-between text-sm mb-1">
              <span>{category_name}</span>
              <span>R$ {value.toFixed(2)}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-indigo-600 h-2.5 rounded-full" 
                style={{ width: `${(value / maxValue) * 100}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex flex-wrap items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-800">Dashboard Financeiro</h2>
          {/* {timeFilter === 'custom' && (
            <div className="flex items-center space-x-2">
              <input
                type="date"
                value={filterStartDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="border rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Data inicial"
              />
              <span className="text-gray-500">até</span>
              <input
                type="date"
                value={filterEndDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="border rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Data final"
              />
            </div>
          )} */}
          <div className="flex space-x-2 mt-2 sm:mt-0">
            <select 
              value={timeFilter}
              onChange={(e) => setTimeFilter(e.target.value)}
              className="border rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">Todo período</option>
              <option value="month">Este mês</option>
              <option value="week">Esta semana</option>
              <option value="today">Hoje</option>
              <option value="last_month">Mês passado</option>
              <option value="custom">Intervalo personalizado</option>
            </select>
            
            <select 
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="border rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {uniqueCategories.map(category => (
                <option key={category} value={category}>
                  {category === 'all' ? 'Todas categorias' : category}
                </option>
              ))}
            </select>
          </div>
           {timeFilter === 'custom' && (
            <div className="flex items-center space-x-2 mt-4 w-full">
              <input
                type="date"
                value={filterStartDate}
                onChange={(e) => setFilterStartDate(e.target.value)}
                className="border rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Data inicial"
              />
              <span className="text-gray-500">até</span>
              <input
                type="date"
                value={filterEndDate}
                onChange={(e) => setFilterEndDate(e.target.value)}
                className="border rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Data final"
              />
            </div>
          )}
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-green-50 p-4 rounded-lg border border-green-100">
            <h3 className="text-sm font-medium text-green-800 mb-2">Receitas</h3>
            <p className="text-2xl font-bold text-green-700">R$ {summary.income.toFixed(2)}</p>
          </div>
          
          <div className="bg-red-50 p-4 rounded-lg border border-red-100">
            <h3 className="text-sm font-medium text-red-800 mb-2">Despesas</h3>
            <p className="text-2xl font-bold text-red-700">R$ {summary.expenses.toFixed(2)}</p>
          </div>
          
          <div className={`p-4 rounded-lg border ${
            summary.balance >= 0 ? 'bg-blue-50 border-blue-100' : 'bg-orange-50 border-orange-100'
          }`}>
            <h3 className={`text-sm font-medium mb-2 ${
              summary.balance >= 0 ? 'text-blue-800' : 'text-orange-800'
            }`}>
              Saldo
            </h3>
            <p className={`text-2xl font-bold ${
              summary.balance >= 0 ? 'text-blue-700' : 'text-orange-700'
            }`}>
              R$ {summary.balance.toFixed(2)}
            </p>
          </div>
        </div>
      </div>

      <div className=" bg-white rounded-lg shadow-md p-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Despesas por Categoria</h3>
          {renderBarChart()}
        </div>
        
        
        <div className="bg-white rounded-lg shadow-md p-6 mt-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Transações Recentes</h3>
          
          {filteredTransactions.length === 0 ? (
            <p className="text-gray-500">Sem transações para exibir</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-3">Data</th>
                    <th className="text-left py-2 px-3">Descrição</th>
                    <th className="text-left py-2 px-3">Categoria</th>
                    <th className="text-right py-2 px-3">Valor</th>
                    <th className="text-right py-2 px-3">Remover</th>

                  </tr>
                </thead>
                <tbody>
                  {filteredTransactions
                    .sort((a, b) => new Date(b.date) - new Date(a.date))
                    .slice(0, 5)
                    .map((transaction) => (
                    <tr key={transaction.id} className="border-b hover:bg-gray-50">
                      <td className="py-2 px-3">{new Date(transaction.date).toLocaleDateString()}</td>
                      <td className="py-2 px-3">{transaction.description}</td>
                      <td className="py-2 px-3">{transaction.category}</td>
                      <td className={`py-2 px-3 text-right font-medium ${
                        transaction.type === 'income' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        R$ {transaction.type === 'expense' ? - Math.abs(transaction.amount).toFixed(2) : Math.abs(transaction.amount).toFixed(2)}
                      </td>
                      <td className="py-2 px-3 text-right">
                        <button 
                          onClick={() => {
                            // Call delete function here
                            deleteTransaction(transaction.id);
                          }}
                          className="text-red-600 hover:text-red-800"
                        >
                          Remover
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          
          {filteredTransactions.length > 5 && (
            <div className="mt-4 text-right">
              <span className="text-sm text-gray-500">
                Mostrando 5 de {filteredTransactions.length} transações
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;