// src/components/ChatInterface.jsx
import React, { useState, useContext, useEffect, useRef } from 'react';
import { FinanceContext } from '../context/FinanceContext';

const ChatInterface = () => {
  const { transactions } = useContext(FinanceContext);
  const [messages, setMessages] = useState([
    {
      id: '1',
      role: 'assistant',
      content: 'Olá! Sou seu assistente financeiro. Como posso te ajudar a analisar seus dados financeiros hoje?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const generateResponse = (query) => {
    // This is a simulated AI response for the MVP
    // In a real app, this would call an actual AI service
    setIsTyping(true);
    
    // Prepare financial data summary for AI context
    const income = transactions
      .filter(t => t.amount > 0)
      .reduce((sum, t) => sum + t.amount, 0);
      
    const expenses = transactions
      .filter(t => t.amount < 0)
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);
    
    const balance = income - expenses;
    
    // Get expense categories
    const expenseCategories = {};
    transactions
      .filter(t => t.amount < 0)
      .forEach(t => {
        expenseCategories[t.category] = (expenseCategories[t.category] || 0) + Math.abs(t.amount);
      });
    
    const currentMonth = new Date().toLocaleString('default', { month: 'long' });
    
    // Simulate AI thinking time
    setTimeout(() => {
      let response = '';
      
      // Pattern matching for common financial queries
      const queryLower = query.toLowerCase();
      
      if (queryLower.includes('saldo') || queryLower.includes('balanço')) {
        response = `Seu saldo atual é R$ ${balance.toFixed(2)}.`;
      } else if (queryLower.includes('receita') || queryLower.includes('ganho') || queryLower.includes('entrada')) {
        response = `O total de suas receitas é R$ ${income.toFixed(2)}.`;
      } else if (queryLower.includes('despesa') || queryLower.includes('gasto') || queryLower.includes('saída')) {
        response = `O total de suas despesas é R$ ${expenses.toFixed(2)}.`;
      } else if (queryLower.includes('categoria')) {
        if (Object.keys(expenseCategories).length === 0) {
          response = 'Você ainda não tem despesas registradas por categoria.';
        } else {
          const categories = Object.entries(expenseCategories)
            .sort((a, b) => b[1] - a[1])
            .map(([cat, val]) => `${cat}: R$ ${val.toFixed(2)}`)
            .join('\n');
          
          response = `Suas despesas por categoria são:\n${categories}`;
        }
      } else if (queryLower.includes('onde mais gasto') || queryLower.includes('maior despesa')) {
        if (Object.keys(expenseCategories).length === 0) {
          response = 'Você ainda não tem despesas registradas.';
        } else {
          const topCategory = Object.entries(expenseCategories)
            .sort((a, b) => b[1] - a[1])[0];
          
          response = `Sua maior categoria de despesa é "${topCategory[0]}" com R$ ${topCategory[1].toFixed(2)}.`;
        }
      } else if (queryLower.includes('economia') || queryLower.includes('poupar')) {
        if (balance > 0) {
          const savingRate = (balance / income * 100).toFixed(1);
          response = `Você está economizando R$ ${balance.toFixed(2)}, o que representa ${savingRate}% da sua renda. Continue assim!`;
        } else {
          response = `Atualmente você está com déficit de R$ ${Math.abs(balance).toFixed(2)}. Tente reduzir algumas despesas para começar a economizar.`;
        }
      } else if (queryLower.includes('conselho') || queryLower.includes('dica')) {
        const tips = [
          'Tente criar um orçamento mensal e siga-o rigorosamente.',
          'Reserve pelo menos 10-20% da sua receita para economias e emergências.',
          'Revise suas despesas recorrentes e veja se há algo que pode ser eliminado.',
          'Compare preços antes de fazer compras grandes.',
          'Considere investir seu dinheiro para fazer ele trabalhar para você.'
        ];
        response = `Aqui vai uma dica financeira: ${tips[Math.floor(Math.random() * tips.length)]}`;
      } else if (queryLower.includes('como estou indo') || queryLower.includes('situação')) {
        if (balance > 0) {
          response = `Você está indo bem! Tem um saldo positivo de R$ ${balance.toFixed(2)}. Continue controlando seus gastos.`;
        } else if (balance === 0) {
          response = 'Você está empatando receitas e despesas. Tente aumentar sua margem de economia.';
        } else {
          response = `Atenção! Você está com um déficit de R$ ${Math.abs(balance).toFixed(2)}. Recomendo revisar seus gastos.`;
        }
      } else if (queryLower.includes('mês') || queryLower.includes('mensal')) {
        response = `Estamos em ${currentMonth}. Para este mês, você tem receitas de R$ ${income.toFixed(2)} e despesas de R$ ${expenses.toFixed(2)}, resultando em um saldo de R$ ${balance.toFixed(2)}.`;
      } else {
        response = "Desculpe, não entendi completamente sua pergunta. Você pode me perguntar sobre seu saldo, receitas, despesas, categorias de gastos ou pedir conselhos financeiros.";
      }
      
      setIsTyping(false);
      
      setMessages(prevMessages => [
        ...prevMessages, 
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: response
        }
      ]);
    }, 1500); // Simulate processing time
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isTyping) return;
    
    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input
    };
    
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInput('');
    
    // Generate AI response
    generateResponse(input);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-120px)]">
      <div className="bg-white rounded-lg shadow-md p-4 mb-4">
        <h2 className="text-xl font-semibold text-gray-800 mb-1">Assistente Financeiro</h2>
        <p className="text-sm text-gray-600">Pergunte sobre seus gastos, receitas, dicas de economia ou análise financeira.</p>
      </div>
      
      <div className="flex-1 bg-white rounded-lg shadow-md flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-4">
            {messages.map(message => (
              <div 
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div 
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === 'user' 
                      ? 'bg-indigo-600 text-white' 
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {message.content.split('\n').map((line, i) => (
                    <React.Fragment key={i}>
                      {line}
                      {i < message.content.split('\n').length - 1 && <br />}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-800 rounded-lg p-3 max-w-[80%]">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>
        
        <form onSubmit={handleSubmit} className="border-t p-3">
          <div className="flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Digite sua pergunta aqui..."
              className="flex-1 p-2 border rounded-l-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              disabled={isTyping}
            />
            <button
              type="submit"
              className="bg-indigo-600 text-white p-2 rounded-r-md hover:bg-indigo-700 focus:outline-none"
              disabled={isTyping || !input.trim()}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;