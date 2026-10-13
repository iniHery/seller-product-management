<script setup>
import { reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const form = reactive({
  username: '',
  password: '',
});

const loading = ref(false);
const errorMessage = ref('');
const showPassword = ref(false);

function getLoginErrorMessage(error) {
  if (error.response?.status === 400 || error.response?.status === 401) {
    return 'Username atau kata sandi salah.';
  }

  return 'Login gagal. Silakan coba lagi.';
}

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
  } catch (error) {
    errorMessage.value = getLoginErrorMessage(error);
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
          <h1 class="break-words text-xl font-bold leading-tight tracking-tight text-slate-900 sm:text-3xl">
            Nivora
          </h1>

          <p class="mt-2 text-sm text-slate-500">
            Product Management Made Simple
          </p>
        </div>

        <div class="mb-6">
          <h2 class="text-xl font-semibold text-slate-900">
            Masuk
          </h2>

          <p class="mt-1 text-sm text-slate-500">
            Masuk untuk melanjutkan ke akun Anda
          </p>

          <p
            v-if="route.query.passwordChanged === '1'"
            role="status"
            class="mt-3 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700"
          >
            Password berhasil diubah. Silakan masuk kembali.
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

            <div class="relative">
              <input
                v-model="form.password"
                id="password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="current-password"
                placeholder="Masukkan kata sandi Anda"
                class="w-full rounded-xl border border-slate-300 bg-white py-3 pl-4 pr-12 text-sm text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-600 focus:ring-4 focus:ring-indigo-100"
              />
              <button
                type="button"
                :aria-label="showPassword ? 'Sembunyikan kata sandi' : 'Tampilkan kata sandi'"
                :aria-pressed="showPassword"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 inline-flex w-11 items-center justify-center rounded-r-xl text-slate-500 transition hover:text-indigo-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
              >
                <svg
                  v-if="showPassword"
                  class="h-5 w-5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  aria-hidden="true"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 3l18 18M10.6 10.6a2 2 0 002.8 2.8" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9.9 5.2A10.8 10.8 0 0112 5c5 0 8.5 4.5 9.5 7-.4 1-1.2 2.1-2.3 3.1M6.2 6.2C4.3 7.5 3 9.4 2.5 12c1 2.5 4.5 7 9.5 7 1.2 0 2.3-.2 3.3-.7" />
                </svg>
                <svg
                  v-else
                  class="h-5 w-5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  aria-hidden="true"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.5 12s3.5-7 9.5-7 9.5 7 9.5 7-3.5 7-9.5 7-9.5-7-9.5-7z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              </button>
            </div>
          </div>

          <div
            v-if="errorMessage"
            role="alert"
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
