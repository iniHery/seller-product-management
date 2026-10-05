import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/',
  headers: {
    'Content-Type': 'application/json',
  },
});

function isPublicAuthenticationEndpoint(url = '') {
  const endpoint = url.split('?')[0].replace(/\/+$/, '');

  return endpoint.endsWith('auth/login') || endpoint.endsWith('auth/register');
}

// Public authentication requests should not carry a possibly stale token.
api.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  const isPublicEndpoint = isPublicAuthenticationEndpoint(config.url);
  config._authTokenAttached = Boolean(token && !isPublicEndpoint);

  if (token && !isPublicEndpoint) {
    config.headers['Authorization'] = `Token ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    const config = error.config;

    if (
      error.response?.status === 401 &&
      config?._authTokenAttached &&
      !isPublicAuthenticationEndpoint(config.url)
    ) {
      window.dispatchEvent(new Event('auth:expired'));
    }

    return Promise.reject(error);
  },
);

export default api;
