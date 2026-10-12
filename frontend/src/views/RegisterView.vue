<template>
  <div class="min-h-screen bg-slate-50 px-4 py-6 sm:px-6">
    <div class="mx-auto flex min-h-[calc(100vh-3rem)] max-w-md items-center justify-center">
      <div class="w-full rounded-2xl border border-slate-200 bg-white p-6 shadow-lg shadow-slate-200/60 sm:p-8">
        <div class="mb-8 text-center">
          <h1 class="break-words text-xl font-bold leading-tight tracking-tight text-slate-900 sm:text-3xl">
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
              class="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-600 focus:ring-4 focus:ring-indigo-100"
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
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="new-password"
                placeholder="Buat kata sandi"
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
            class="w-full rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-200 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <span v-if="loading">Membuat akun...</span>
            <span v-else>Daftar</span>
          </button>
        </form>

        <p class="mt-6 text-center text-sm text-slate-500">
          Sudah punya akun?
          <RouterLink
            :to="{ name: 'Login' }"
            class="font-semibold text-indigo-700 underline-offset-4 hover:text-indigo-800 hover:underline"
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
const showPassword = ref(false);

function getErrorMessage(data) {
  if (data && typeof data === 'object') {
    const messages = [];

    for (const [field, value] of Object.entries(data)) {
      const fieldMessages = Array.isArray(value) ? value : [value];

      for (const message of fieldMessages) {
        if (typeof message !== 'string') continue;

        const normalizedMessage = message.toLowerCase();
        if (field === 'password') {
          if (normalizedMessage.includes('too similar')) {
            messages.push('Kata sandi terlalu mirip dengan username.');
          } else if (normalizedMessage.includes('too common')) {
            messages.push('Kata sandi terlalu umum. Silakan gunakan kata sandi yang lebih kuat.');
          } else if (normalizedMessage.includes('too short')) {
            messages.push('Kata sandi terlalu pendek.');
          } else {
            messages.push('Kata sandi belum memenuhi persyaratan. Silakan gunakan kata sandi yang lebih kuat.');
          }
        } else if (field === 'username' && normalizedMessage.includes('already exists')) {
          messages.push('Username sudah digunakan. Silakan pilih username lain.');
        } else if (field === 'email' && normalizedMessage.includes('already exists')) {
          messages.push('Email sudah digunakan. Silakan gunakan email lain.');
        } else if (field === 'email' && normalizedMessage.includes('valid email')) {
          messages.push('Format email tidak valid.');
        } else if (normalizedMessage.includes('required')) {
          const fieldName = {
            username: 'Username',
            email: 'Email',
            password: 'Kata sandi',
          }[field];
          if (fieldName) messages.push(`${fieldName} wajib diisi.`);
        } else if (field === 'non_field_errors') {
          messages.push('Data pendaftaran tidak valid. Silakan periksa kembali informasi Anda.');
        }
      }
    }

    if (messages.length > 0) {
      return [...new Set(messages)].join(' ');
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
    console.warn('Registration request failed.', {
      status: error.response?.status ?? null,
    });
    errorMessage.value = getErrorMessage(error.response?.data);
  } finally {
    loading.value = false;
  }
}
</script>
