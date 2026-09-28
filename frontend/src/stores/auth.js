// src/stores/auth.js
import { defineStore } from 'pinia';
import * as authService from '@/api/authService';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('auth_token') || null,
    user: JSON.parse(localStorage.getItem('auth_user')) || null,
    status: 'idle', // 'idle' | 'loading' | 'error' | 'authenticated'
  }),

  actions: {
    async login(credentials) {
      this.status = 'loading';
      try {
        const response = await authService.login(credentials);
        const data = response.data;
        if (data.success) {
          const token = data.data.token;
          const user = data.data.user;
          // persist
          localStorage.setItem('auth_token', token);
          localStorage.setItem('auth_user', JSON.stringify(user));
          // update state
          this.token = token;
          this.user = user;
          this.status = 'authenticated';
        } else {
          this.status = 'error';
        }
        return response;
      } catch (e) {
        this.status = 'error';
        throw e;
      }
    },

    async logout() {
      this.status = 'loading';
      try {
        await authService.logout();
      } catch (e) {
        // ignore logout failure, still clear locally
      }
      this.clearAuth();
    },

    async fetchMe() {
      if (!this.token) return;
      this.status = 'loading';
      try {
        const response = await authService.me();
        const data = response.data;
        if (data.success) {
          this.user = data.data;
          localStorage.setItem('auth_user', JSON.stringify(this.user));
          this.status = 'authenticated';
        } else {
          this.status = 'error';
        }
      } catch (e) {
        this.status = 'error';
        throw e;
      }
    },

    clearAuth() {
      this.token = null;
      this.user = null;
      this.status = 'idle';
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
    },
  },
});
