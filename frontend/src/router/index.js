// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '@/views/LoginView.vue';
import RegisterView from '@/views/RegisterView.vue';
import { useAuthStore } from '@/stores/auth';

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
  },
  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/ProductView.vue'),
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('@/views/CategoryView.vue'),
      },
    ],
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
      return { name: 'Login' };
    }
  }

  // Protect authenticated routes
  if (to.matched.some((record) => record.meta.requiresAuth) && !isAuthenticated) {
    return { name: 'Login' };
  }

  // Prevent logged-in users from accessing login page
  if (to.name === 'Login' && isAuthenticated) {
    return { name: 'Dashboard' };
  }

  return true;
});

export default router;
