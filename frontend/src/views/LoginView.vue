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
    errorMessage.value = 'Username dan kata sandi wajib diisi.';
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
    if (e.response && e.response.data) {
      errorMessage.value = e.response.data.detail || JSON.stringify(e.response.data);
    } else {
      errorMessage.value = e.message || 'Masuk gagal. Silakan periksa kredensial Anda.';
    }
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 px-4 py-6 sm:px-6">
    <div class="mx-auto flex min-h-[calc(100vh-5rem)] max-w-md items-center justify-center">
      <div
        class="w-full rounded-2xl border border-slate-200 bg-white p-6 shadow-lg shadow-slate-200/60 sm:p-8"
      >
        <div class="mb-8 text-center">
          <h1 class="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Seller Product Management
          </h1>

          <p class="mt-2 text-sm text-slate-500">
            Kelola produk Anda dengan mudah
          </p>
        </div>

        <div class="mb-6">
          <h2 class="text-xl font-semibold text-slate-900">
            Masuk
          </h2>

          <p class="mt-1 text-sm text-slate-500">
            Masuk untuk melanjutkan ke akun Anda
          </p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
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
              placeholder="Masukkan username Anda"
              class="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-600 focus:ring-4 focus:ring-indigo-100"
            />
          </div>

          <div>
            <label
              for="password"
              class="mb-2 block text-sm font-medium text-slate-700"
            >
              Kata Sandi
            </label>

            <input
              v-model="form.password"
              id="password"
              type="password"
              required
              autocomplete="current-password"
              placeholder="Masukkan kata sandi Anda"
              class="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-600 focus:ring-4 focus:ring-indigo-100"
            />
          </div>

          <div
            v-if="errorMessage"
            class="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            {{ errorMessage }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-200 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <span v-if="loading">Masuk...</span>
            <span v-else>Masuk</span>
          </button>
        </form>

        <p class="mt-6 text-center text-sm text-slate-500">
          Belum punya akun?
          <RouterLink
            :to="{ name: 'Register' }"
            class="font-semibold text-indigo-700 underline-offset-4 hover:text-indigo-800 hover:underline"
          >
            Daftar
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
