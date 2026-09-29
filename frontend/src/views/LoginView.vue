// src/views/LoginView.vue
<template>
  <div class="min-h-screen bg-slate-50 px-4 py-6 sm:px-6">
    <div class="mx-auto flex min-h-[calc(100vh-5rem)] max-w-md items-center justify-center">
      <div
        class="w-full rounded-2xl border border-slate-200 bg-white p-6 shadow-xl sm:p-8"
      >
        <!-- Branding -->
        <div class="mb-8 text-center">
          <h1 class="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Seller Product Management
          </h1>

          <p class="mt-2 text-sm text-slate-500">
            Manage your products easily
          </p>
        </div>

        <!-- Login Header -->
        <div class="mb-6">
          <h2 class="text-xl font-semibold text-slate-900">
            Login
          </h2>

          <p class="mt-1 text-sm text-slate-500">
            Sign in to continue to your account
          </p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- Username -->
          <div>
            <label
              for="username"
              class="mb-2 block text-sm font-medium text-slate-700"
            >
              Username
            </label>

            <input
              v-model="form.username"
              id="username"
              type="text"
              required
              autocomplete="username"
              placeholder="Enter your username"
              class="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-500 focus:ring-4 focus:ring-slate-100"
            />
          </div>

          <!-- Password -->
          <div>
            <label
              for="password"
              class="mb-2 block text-sm font-medium text-slate-700"
            >
              Password
            </label>

            <input
              v-model="form.password"
              id="password"
              type="password"
              required
              autocomplete="current-password"
              placeholder="Enter your password"
              class="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-500 focus:ring-4 focus:ring-slate-100"
            />
          </div>

          <!-- Error -->
          <div
            v-if="errorMessage"
            class="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            {{ errorMessage }}
          </div>

          <!-- Login Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 focus:outline-none focus:ring-4 focus:ring-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <span v-if="loading">Logging in...</span>
            <span v-else>Login</span>
          </button>
        </form>

        <p class="mt-6 text-center text-sm text-slate-500">
          Belum punya akun?
          <RouterLink
            :to="{ name: 'Register' }"
            class="font-semibold text-slate-900 underline-offset-4 hover:underline"
          >
            Register
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const form = reactive({
  username: '',
  password: '',
});

const loading = ref(false);
const errorMessage = ref('');

async function handleLogin() {
  errorMessage.value = '';

  if (!form.username || !form.password) {
    errorMessage.value = 'Username and password are required.';
    return;
  }

  loading.value = true;

  try {
    await authStore.login({
      username: form.username,
      password: form.password,
    });

    router.push({ name: 'Dashboard' });
  } catch (e) {
    console.error('Login error:', e);
    console.dir(e);
    console.log('Request URL was:', e.config?.url);
    console.log('Base URL was:', e.config?.baseURL);
    // Show more specific error if available
    if (e.response && e.response.data) {
      errorMessage.value = e.response.data.detail || JSON.stringify(e.response.data);
    } else {
      errorMessage.value = e.message || 'Login failed. Please check your credentials.';
    }
  } finally {
    loading.value = false;
  }
}
</script>