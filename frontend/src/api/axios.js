import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach the token except on login and logout requests.
api.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  const isAuthEndpoint = config.url?.includes('auth/login') || config.url?.includes('auth/logout');
  if (token && !isAuthEndpoint) {
    config.headers['Authorization'] = `Token ${token}`;
  }
  return config;
});

export default api;
