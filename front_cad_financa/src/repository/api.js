import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3001/api', // URL da sua API NestJS
});

export default api;
