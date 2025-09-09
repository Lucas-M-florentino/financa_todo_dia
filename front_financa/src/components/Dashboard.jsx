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
      return <p className="text-gray-500 dark:text-gray-200">Sem dados de despesas para exibir</p>;
    }
    
    const maxValue = Math.max(...Object.values(summary.expensesByCategory));
    
    return (
      <div className="space-y-3">
        {Object.entries(summary.expensesByCategory).map(([category_name, value]) => (
          <div key={category_name} className="flex flex-col dark:text-gray-200">
            <div className="flex justify-between text-sm mb-1">
              <span>{category_name}</span>
              <span>R$ {value.toFixed(2)}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-indigo-600 dark:text-gray-200 h-2.5 rounded-full" 
                style={{ width: `${(value / maxValue) * 100}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  // State for number of transactions to show
  const [transactionsToShow, setTransactionsToShow] = useState(5);

  return (
    <div className="bg-gray-100 dark:bg-gray-900 min-h-screen">
      <div className="space-y-6 px-2 sm:px-0">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="flex flex-wrap items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">Dashboard Financeiro</h2>
            <div className="flex space-x-2 mt-2 sm:mt-0">
              <select 
                value={timeFilter}
                onChange={(e) => setTimeFilter(e.target.value)}
                className="border rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500
                  bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 border-gray-300 dark:border-gray-600"
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
                className="border rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500
                  bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 border-gray-300 dark:border-gray-600"
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
                  className="border rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500
                    bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 border-gray-300 dark:border-gray-600"
                  placeholder="Data inicial"
                />
                <span className="text-gray-500 dark:text-gray-300">até</span>
                <input
                  type="date"
                  value={filterEndDate}
                  onChange={(e) => setFilterEndDate(e.target.value)}
                  className="border rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500
                    bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 border-gray-300 dark:border-gray-600"
                  placeholder="Data final"
                />
              </div>
            )}
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-green-50 dark:bg-green-900 p-4 rounded-lg border border-green-100 dark:border-green-800">
              <h3 className="text-sm font-medium text-green-800 dark:text-green-200 mb-2">Receitas</h3>
              <p className="text-2xl font-bold text-green-700 dark:text-green-300">R$ {summary.income.toFixed(2)}</p>
            </div>
            
            <div className="bg-red-50 dark:bg-red-900 p-4 rounded-lg border border-red-100 dark:border-red-800">
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200 mb-2">Despesas</h3>
              <p className="text-2xl font-bold text-red-700 dark:text-red-300">R$ {summary.expenses.toFixed(2)}</p>
            </div>
            
            <div className={`p-4 rounded-lg border ${
              summary.balance >= 0
                ? 'bg-blue-50 dark:bg-blue-900 border-blue-100 dark:border-blue-800'
                : 'bg-orange-50 dark:bg-orange-900 border-orange-100 dark:border-orange-800'
            }`}>
              <h3 className={`text-sm font-medium mb-2 ${
                summary.balance >= 0 ? 'text-blue-800 dark:text-blue-200' : 'text-orange-800 dark:text-orange-200'
              }`}>
                Saldo
              </h3>
              <p className={`text-2xl font-bold ${
                summary.balance >= 0 ? 'text-blue-700 dark:text-blue-300' : 'text-orange-700 dark:text-orange-300'
              }`}>
                R$ {summary.balance.toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Despesas por Categoria</h3>
            {renderBarChart()}
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mt-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Transações Recentes</h3>
              <div>
                <label htmlFor="transactionsToShow" className="mr-2 text-sm text-gray-600 dark:text-gray-300">Mostrar:</label>
                <select
                  id="transactionsToShow"
                  value={transactionsToShow}
                  onChange={e => setTransactionsToShow(Number(e.target.value))}
                  className="border rounded-md p-1 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500
                    bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 border-gray-300 dark:border-gray-600"
                >
                  {[5, 10, 15, 20, 25, 30].map(num => (
                    <option key={num} value={num}>{num}</option>
                  ))}
                </select>
              </div>
            </div>
            
            {filteredTransactions.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-300">Sem transações para exibir</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <th className="text-left py-2 px-3 text-gray-700 dark:text-gray-200">Data</th>
                      <th className="text-left py-2 px-3 text-gray-700 dark:text-gray-200">Descrição</th>
                      <th className="text-left py-2 px-3 text-gray-700 dark:text-gray-200">Categoria</th>
                      <th className="text-right py-2 px-3 text-gray-700 dark:text-gray-200">Valor</th>
                      <th className="text-right py-2 px-3 text-gray-700 dark:text-gray-200">Remover</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTransactions
                      .sort((a, b) => new Date(b.date) - new Date(a.date))
                      .slice(0, transactionsToShow)
                      .map((transaction, index) => (
                      <tr key={transaction.id || index} className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
                        <td className="py-2 px-3 text-gray-800 dark:text-gray-100">{new Date(transaction.date).toLocaleDateString()}</td>
                        <td className="py-2 px-3 text-gray-800 dark:text-gray-100">{transaction.description}</td>
                        <td className="py-2 px-3 text-gray-800 dark:text-gray-100">{transaction.category}</td>
                        <td className={`py-2 px-3 text-right font-medium ${
                          transaction.type === 'income' ? 'text-green-600 dark:text-green-300' : 'text-red-600 dark:text-red-300'
                        }`}>
                          R$ {transaction.type === 'expense' ? - Math.abs(transaction.amount).toFixed(2) : Math.abs(transaction.amount).toFixed(2)}
                        </td>
                        <td className="py-2 px-3 text-right">
                          <button 
                            onClick={() => {
                              deleteTransaction(transaction.id);
                            }}
                            className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
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
            
            {filteredTransactions.length > transactionsToShow && (
              <div className="mt-4 text-right">
                <span className="text-sm text-gray-500 dark:text-gray-300">
                  Mostrando {transactionsToShow} de {filteredTransactions.length} transações
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;