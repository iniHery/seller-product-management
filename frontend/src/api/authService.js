import api from './axios';

export function login(credentials) {
  return api.post('auth/login/', credentials);
}

export function register(userData) {
  return api.post('auth/register/', userData);
}

export function logout() {
  return api.post('auth/logout/');
}

export function me() {
  return api.get('auth/me/');
}

export function updateProfile(profile) {
  return api.patch('auth/me/', profile);
}

export function changePassword(passwords) {
  return api.post('auth/change-password/', passwords);
}
