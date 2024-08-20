import axios from 'axios';

// Criação da instância do Axios
const api = axios.create({
  baseURL: 'http://localhost:3001/api', // URL da sua API NestJS
  withCredentials: true, // Garante que os cookies sejam enviados nas requisições
});

// Interceptação de erros de resposta
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Tratamento de erros, como redirecionamento em caso de token expirado
    if (error.response && error.response.status === 401) {
      // Token expirado ou inválido, redirecionar para login
      console.log('Token expirado ou inválido. Redirecionando para login.');
      // Redirecione o usuário para a página de login, por exemplo:
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
