// src/api/axios.js
import axios from 'axios';

// Create an Axios instance with base URL from Vite environment variables
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor – attach token if present in localStorage
api.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  // Do not attach token for authentication endpoints (login/logout)
  const isAuthEndpoint = config.url?.includes('auth/login') || config.url?.includes('auth/logout');
  if (token && !isAuthEndpoint) {
    config.headers['Authorization'] = `Token ${token}`;
  }
  return config;
});

export default api;
