// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '@/views/LoginView.vue';
import { defineAsyncComponent } from 'vue';
import { useAuthStore } from '@/stores/auth';

// Lazy load Product view placeholder (can be replaced later)
const ProductView = defineAsyncComponent(() => import('@/views/ProductView.vue'));

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
  },
  {
    path: '/products',
    name: 'Products',
    component: ProductView,
    // In a real app you would protect this route with a navigation guard.
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach(async (to, from) => {
  const authStore = useAuthStore();
  const token = localStorage.getItem('auth_token');
  const isAuthenticated = !!token;

  // If we have a token but user data not loaded, try to fetch current user
  if (isAuthenticated && !authStore.user) {
    try {
      await authStore.fetchMe();
    } catch (e) {
      // Invalid token – clear and redirect to login
      authStore.clearAuth();
      return { path: '/login' };
    }
  }

  // Protect /products route
  if (to.name === 'Products' && !isAuthenticated) {
    return { path: '/login' };
  }

  // Prevent logged-in users from accessing login page
  if (to.name === 'Login' && isAuthenticated) {
    return { path: '/products' };
  }

  return true;
});

export default router;
