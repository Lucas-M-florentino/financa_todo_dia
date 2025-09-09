// utils/api.js (parte relevante)
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

api.defaults.headers.common["Content-Type"] = "application/json";
api.defaults.headers.common["Accept"] = "application/json";

// interceptor global de resposta
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response) {
      const status = err.response.status;
      if ([401, 403].includes(status)) {
        console.warn("⚠️ Token expirado ou inválido. Fazendo logout...");
        localStorage.removeItem("authToken");
        delete api.defaults.headers.common["Authorization"];
        // opcional: redirecionar ao login
        // window.location.href = "/";
      }
    }
    return Promise.reject(err);
  }
);

export const setAuthToken = (token) => {
  if (token) {
    const clean = String(token).replace(/^["']|["']$/g, "");
    api.defaults.headers.common["Authorization"] = `Bearer ${clean}`;
    localStorage.setItem("authToken", clean);
  } else {
    delete api.defaults.headers.common["Authorization"];
    localStorage.removeItem("authToken");
  }
};

export const loadTokenFromStorage = () => {
  const token = localStorage.getItem("authToken");
  if (token) {
    const clean = token.replace(/^["']|["']$/g, "");
    api.defaults.headers.common["Authorization"] = `Bearer ${clean}`;
    return clean;
  }
  return null;
};

export const clearAuthToken = () => {
  delete api.defaults.headers.common["Authorization"];
  localStorage.removeItem("authToken");
};

// LOGIN
export const login = async (credentials) => {
  try {
    const res = await api.post("/user/login", credentials);
    const data = res.data;
    const token = data.access_token;

    if (token) {
      setAuthToken(token);
    }
    // opcional: retornar dados do usuário
    return data.user;
  } catch (err) {
    console.error("Error during login:", err);
    throw err;
  }
};

// GET PROFILE
export const getUserProfile = async (user_email) => {
  try {
    console.log("Fetching profile for:", user_email);
    const res = await api.get("/user/profile/" + user_email);
    return res.data;
  } catch (err) {
    console.error("Error fetching user profile:", err);
    throw err;
  }
};

// REGISTER (exemplo simples)
export const register = async (userInfo) => {
  try {
    const res = await api.post("/user/signup", userInfo);
    return res.data;
  } catch (err) {
    console.error("Error during registration:", err);
    throw err;
  }
};

// CATEGORIES
export const getAllCategories = async () => {
  try {
    const res = await api.get("/categories");
    return res.data;
  } catch (err) {
    console.error("Error fetching categories:", err);
    throw err;
  }
};

// TRANSACTIONS
export const getTransactions = async (user_id) => {
  try {
    const res = await api.get("/transactions/" + user_id);
    return res.data;
  } catch (err) {
    console.error("Error fetching transactions:", err);
    throw err;
  }
};

export const createTransaction = async (transaction) => {
  try {
    const res = await api.post("/transactions", transaction);
    return res.data;
  } catch (err) {
    console.error("Error creating transaction:", err);
    throw err;
  }
};

export const deleteTransactionId = async (id) => {
  try {
    const res = await api.delete(`/transactions/${id}`);
    return res.data;
  } catch (err) {
    console.error("Error deleting transaction:", err);
    throw err;
  }
};

export const updateTransactionId = async (id, transaction) => {
  try {
    const res = await api.put(`/transactions/${id}`, transaction);
    return res.data;
  } catch (err) {
    console.error("Error updating transaction:", err);
    throw err;
  }
};
