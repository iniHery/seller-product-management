<template>
  <div class="min-h-screen bg-slate-50 px-4 py-6 sm:px-6">
    <div class="mx-auto flex min-h-[calc(100vh-3rem)] max-w-md items-center justify-center">
      <div class="w-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
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
            Daftar
          </h2>
          <p class="mt-1 text-sm text-slate-500">
            Buat akun untuk memulai
          </p>
        </div>

        <form class="space-y-5" @submit.prevent="handleRegister">
          <div>
            <label
              for="username"
              class="mb-2 block text-sm font-medium text-slate-700"
            >
              Username
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              autocomplete="username"
              placeholder="Masukkan username Anda"
              class="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-500 focus:ring-4 focus:ring-slate-100"
            />
          </div>

          <div>
            <label
              for="email"
              class="mb-2 block text-sm font-medium text-slate-700"
            >
              Email
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              autocomplete="email"
              placeholder="Masukkan email Anda"
              class="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-500 focus:ring-4 focus:ring-slate-100"
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
              id="password"
              v-model="form.password"
              type="password"
              required
              autocomplete="new-password"
              placeholder="Buat kata sandi"
              class="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-500 focus:ring-4 focus:ring-slate-100"
            />
          </div>

          <p
            v-if="errorMessage"
            role="alert"
            class="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-700"
          >
            {{ errorMessage }}
          </p>

          <p
            v-if="successMessage"
            role="status"
            aria-live="polite"
            class="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm leading-6 text-emerald-700"
          >
            {{ successMessage }}
          </p>

          <button
            type="submit"
            :disabled="loading"
            class="w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 focus:outline-none focus:ring-4 focus:ring-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <span v-if="loading">Membuat akun...</span>
            <span v-else>Daftar</span>
          </button>
        </form>

        <p class="mt-6 text-center text-sm text-slate-500">
          Sudah punya akun?
          <RouterLink
            :to="{ name: 'Login' }"
            class="font-semibold text-slate-900 underline-offset-4 hover:underline"
          >
            Masuk
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { register } from '@/api/authService';

const router = useRouter();

const form = reactive({
  username: '',
  email: '',
  password: '',
});

const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

function getErrorMessage(data) {
  if (typeof data?.detail === 'string') {
    return data.detail;
  }

  if (data && typeof data === 'object') {
    const messages = Object.entries(data)
      .flatMap(([field, value]) => {
        const fieldMessages = Array.isArray(value) ? value : [value];
        return fieldMessages
          .filter((message) => typeof message === 'string')
          .map((message) => `${field}: ${message}`);
      });

    if (messages.length > 0) {
      return messages.join(' ');
    }
  }

  return 'Pendaftaran gagal. Silakan periksa informasi Anda dan coba lagi.';
}

async function handleRegister() {
  errorMessage.value = '';
  successMessage.value = '';
  loading.value = true;

  try {
    const response = await register({
      username: form.username,
      email: form.email,
      password: form.password,
    });

    if (response.data?.success === false) {
      errorMessage.value = getErrorMessage(response.data);
      return;
    }

    successMessage.value = 'Pendaftaran berhasil. Mengalihkan ke halaman masuk...';
    window.setTimeout(() => {
      router.push({ name: 'Login' });
    }, 1000);
  } catch (error) {
    console.error('Registration error:', error);
    errorMessage.value = getErrorMessage(error.response?.data);
  } finally {
    loading.value = false;
  }
}
</script>
