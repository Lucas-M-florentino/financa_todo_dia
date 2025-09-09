// utils/api.js
import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
  withCredentials: false,
});

// Interceptor para erros globais
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const status = error.response.status;

      // Token expirado ou inválido
      if ([401, 403].includes(status)) {
        console.warn("⚠️ Token expirado ou inválido. Fazendo logout...");
        // se a rota for login remover o token do localstorage
        if (window.location.pathname !== "/login") {
          localStorage.removeItem("authToken");
        }
        // window.location.href = "/"; // redireciona pro login
      }
    }
    return Promise.reject(error);
  }
);

// Adicionar/remover token nos headers
export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
};

// Carregar token salvo no localStorage
export const loadTokenFromStorage = () => {
  const token = localStorage.getItem("authToken");
  if (token) {
    const cleanToken = token.replace(/^["']|["']$/g, ""); // remove aspas extras
    setAuthToken(cleanToken);
    return cleanToken;
  }
  return null;
};

export const clearAuthToken = () => {
  localStorage.removeItem("authToken");
  setAuthToken(null);
  console.log("Token removido");
};

// ==================== AUTH ====================
export const login = async (credentials) => {
  try {
    const { data } = await api.post("/user/login", credentials);

    const token = data.access_token || data.token;
    if (token) {
      const cleanToken = String(token).replace(/^["']|["']$/g, "");
      setAuthToken(cleanToken);
      localStorage.setItem("authToken", cleanToken);
      localStorage.setItem("userEmail", credentials.email);
    }

    return data;
  } catch (error) {
    console.error("Error during login:", error);
    throw error;
  }
};

export const register = async (userInfo) => {
  try {
    const { data } = await api.post("/user/register", userInfo);
    return data;
  } catch (error) {
    console.error("Error during registration:", error);
    throw error;
  }
};

// ==================== PROFILE ====================
export const getUserProfile = async () => {
  const { data } = await api.get("/user/profile");
  return data;
};

export const saveProfile = async (profileData) => {
  const { data } = await api.post("/user/profile", profileData);
  return data;
};

export const updateUserProfile = async (profileData) => {
  const { data } = await api.put("/user/profile", profileData);
  return data;
};

// ==================== TRANSACTIONS ====================
export const getTransactions = async () => {
  const { data } = await api.get("/transactions");
  return data;
};

export const saveTransactions = async (transaction) => {
  const { data } = await api.post("/transactions", transaction);
  return data;
};

export const createTransaction = async (transaction) => {
  const { data } = await api.post("/transactions", transaction);
  return data;
};

export const deleteTransactionId = async (id) => {
  const { data } = await api.delete(`/transactions/${id}`);
  return data;
};

export const updateTransactionId = async (id, transaction) => {
  const { data } = await api.put(`/transactions/${id}`, transaction);
  return data;
};

// ==================== CATEGORIES ====================
export const getAllCategories = async () => {
  const { data } = await api.get("/categories");
  return data;
};

export default api;
