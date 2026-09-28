// src/api/authService.js
import api from './axios';

/**
 * Login user – expects credentials object { username, password }
 * Returns the raw Axios response.
 */
export function login(credentials) {
  return api.post('auth/login/', credentials);
}

/**
 * Logout current user.
 */
export function logout() {
  return api.post('auth/logout/');
}

/**
 * Get current authenticated user information.
 */
export function me() {
  return api.get('auth/me/');
}
