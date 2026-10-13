<script setup>
import { computed, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { getDashboardStats } from '@/api/dashboardService';

const stats = ref(null);
const loading = ref(false);
const error = ref('');
const lastUpdated = ref('');

const numberFormatter = new Intl.NumberFormat('id-ID');
const activePercentage = computed(() => {
  if (!stats.value?.total_products) return 0;

  return Math.min(
    100,
    Math.round((stats.value.active_products / stats.value.total_products) * 100),
  );
});

const metricCards = computed(() => {
  if (!stats.value) return [];

  return [
    {
      label: 'Total produk',
      value: stats.value.total_products,
      description: 'Semua produk yang Anda kelola',
      icon: 'products',
      iconClass: 'bg-indigo-50 text-indigo-600',
      accentClass: 'bg-indigo-500',
    },
    {
      label: 'Produk aktif',
      value: stats.value.active_products,
      description: 'Produk siap dijual',
      icon: 'active',
      iconClass: 'bg-emerald-50 text-emerald-600',
      accentClass: 'bg-emerald-500',
    },
    {
      label: 'Produk tidak aktif',
      value: stats.value.inactive_products,
      description: 'Produk yang sedang disembunyikan',
      icon: 'inactive',
      iconClass: 'bg-amber-50 text-amber-600',
      accentClass: 'bg-amber-500',
    },
    {
      label: 'Total stok',
      value: stats.value.total_stock,
      description: 'Jumlah unit dari seluruh produk',
      icon: 'stock',
      iconClass: 'bg-sky-50 text-sky-600',
      accentClass: 'bg-sky-500',
    },
  ];
});

function isValidStats(data) {
  const fields = ['total_products', 'active_products', 'inactive_products', 'total_stock'];

  return data && fields.every((field) => (
    typeof data[field] === 'number'
    && Number.isFinite(data[field])
    && data[field] >= 0
  ));
}

async function fetchDashboardStats() {
  if (loading.value) return;

  loading.value = true;
  error.value = '';

  try {
    const response = await getDashboardStats();
    const data = response.data?.data;

    if (response.data?.success !== true || !isValidStats(data)) {
      throw new Error('Respons statistik dasbor tidak valid.');
    }

    stats.value = data;
    lastUpdated.value = new Intl.DateTimeFormat('id-ID', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date());
  } catch (err) {
    error.value = err.response?.data?.detail
      || 'Statistik belum dapat dimuat. Periksa koneksi Anda, lalu coba lagi.';
  } finally {
    loading.value = false;
  }
}

onMounted(fetchDashboardStats);
</script>

<template>
  <div class="min-h-full bg-slate-50 px-4 py-6 text-slate-900 sm:px-6 sm:py-8 lg:px-8">
    <div class="mx-auto w-full min-w-0 max-w-7xl">
      <section class="relative isolate mb-7 overflow-hidden rounded-3xl bg-linear-to-br from-slate-950 via-indigo-950 to-indigo-800 px-5 py-7 text-white shadow-lg shadow-indigo-950/10 sm:px-8 sm:py-9">
        <div class="pointer-events-none absolute -right-12 -top-24 -z-10 h-64 w-64 rounded-full bg-indigo-400/20 blur-3xl"></div>
        <div class="pointer-events-none absolute -bottom-32 right-1/3 -z-10 h-56 w-56 rounded-full bg-sky-300/10 blur-3xl"></div>

        <div class="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
          <div class="min-w-0">
            <p class="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-indigo-200">
              Nivora
            </p>
            <h1 class="text-2xl font-bold tracking-tight sm:text-3xl">Dasbor</h1>
            <p class="mt-2 max-w-2xl text-sm leading-6 text-indigo-100 sm:text-base">
              Product Management Made Simple
            </p>
          </div>

          <div class="flex flex-col gap-3 sm:items-end">
            <p v-if="lastUpdated" class="text-xs text-indigo-200">
              Diperbarui {{ lastUpdated }}
            </p>
            <button
              type="button"
              @click="fetchDashboardStats"
              :disabled="loading"
              class="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-white/20 bg-white/10 px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-indigo-900 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <svg
                class="h-4 w-4"
                :class="{ 'animate-spin': loading }"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              {{ loading ? 'Memuat...' : 'Segarkan data' }}
            </button>
          </div>
        </div>
      </section>

      <div
        v-if="error"
        role="alert"
        class="mb-6 flex flex-col gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 sm:flex-row sm:items-center sm:justify-between sm:px-5"
      >
        <div class="flex min-w-0 items-start gap-3">
          <svg class="mt-0.5 h-5 w-5 shrink-0 text-red-600" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          <p class="min-w-0 text-sm leading-6 text-red-800">{{ error }}</p>
        </div>
        <button
          type="button"
          @click="fetchDashboardStats"
          :disabled="loading"
          class="shrink-0 self-start rounded-lg px-3 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-60 sm:self-auto"
        >
          Coba lagi
        </button>
      </div>

      <section
        v-if="loading && !stats"
        class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4"
        aria-label="Memuat ringkasan statistik"
        role="status"
      >
        <div
          v-for="item in 4"
          :key="item"
          class="h-36 animate-pulse rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div class="flex items-center gap-4">
            <div class="h-12 w-12 rounded-xl bg-slate-100"></div>
            <div class="flex-1 space-y-3">
              <div class="h-3 w-2/3 rounded bg-slate-100"></div>
              <div class="h-6 w-1/3 rounded bg-slate-100"></div>
            </div>
          </div>
          <div class="mt-6 h-3 w-4/5 rounded bg-slate-100"></div>
        </div>
        <span class="sr-only">Memuat statistik dasbor...</span>
      </section>

      <template v-else-if="stats">
        <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-label="Ringkasan produk">
          <article
            v-for="card in metricCards"
            :key="card.label"
            class="relative min-w-0 overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-md sm:p-6"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <p class="text-sm font-medium text-slate-500">{{ card.label }}</p>
                <p class="mt-3 text-3xl font-bold tracking-tight text-slate-950 tabular-nums">
                  {{ numberFormatter.format(card.value) }}
                </p>
              </div>
              <div class="shrink-0 rounded-xl p-3" :class="card.iconClass">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <template v-if="card.icon === 'products'">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                  </template>
                  <template v-else-if="card.icon === 'active'">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </template>
                  <template v-else-if="card.icon === 'inactive'">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </template>
                  <template v-else>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                  </template>
                </svg>
              </div>
            </div>
            <p class="mt-4 text-xs leading-5 text-slate-500">{{ card.description }}</p>
            <div class="absolute inset-x-0 bottom-0 h-1" :class="card.accentClass"></div>
          </article>
        </section>

        <section class="mt-6 grid grid-cols-1 gap-5 lg:grid-cols-5">
          <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6 lg:col-span-3">
            <div class="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 class="text-base font-semibold text-slate-900">Status produk</h2>
                <p class="mt-1 text-sm text-slate-500">Perbandingan produk aktif dan tidak aktif.</p>
              </div>
              <span class="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">
                {{ activePercentage }}% aktif
              </span>
            </div>

            <div v-if="stats.total_products > 0" class="mt-6">
              <div
                class="flex h-3 overflow-hidden rounded-full bg-amber-100"
                role="img"
                :aria-label="`${activePercentage}% produk aktif`"
              >
                <div
                  class="rounded-full bg-emerald-500 transition-all duration-500"
                  :style="{ width: `${activePercentage}%` }"
                ></div>
              </div>
              <div class="mt-5 grid grid-cols-2 gap-4">
                <div class="rounded-xl bg-emerald-50/70 p-4">
                  <p class="text-xs font-medium text-emerald-700">Aktif</p>
                  <p class="mt-1 text-xl font-bold tabular-nums text-emerald-900">
                    {{ numberFormatter.format(stats.active_products) }}
                  </p>
                  <p class="mt-1 text-xs text-emerald-700">{{ activePercentage }}% dari produk</p>
                </div>
                <div class="rounded-xl bg-amber-50/80 p-4">
                  <p class="text-xs font-medium text-amber-700">Tidak aktif</p>
                  <p class="mt-1 text-xl font-bold tabular-nums text-amber-900">
                    {{ numberFormatter.format(stats.inactive_products) }}
                  </p>
                  <p class="mt-1 text-xs text-amber-700">Perlu ditinjau</p>
                </div>
              </div>
            </div>

            <div v-else class="mt-6 rounded-xl border border-dashed border-slate-200 bg-slate-50 px-5 py-7 text-center">
              <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <h3 class="mt-3 text-sm font-semibold text-slate-900">Belum ada produk</h3>
              <p class="mt-1 text-sm text-slate-500">Tambahkan produk pertama untuk mulai memantau performa toko.</p>
              <RouterLink
                to="/products"
                class="mt-4 inline-flex min-h-10 items-center justify-center rounded-xl bg-indigo-600 px-4 text-sm font-semibold text-white transition hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                Mulai kelola produk
              </RouterLink>
            </div>
          </article>

          <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6 lg:col-span-2">
            <div>
              <h2 class="text-base font-semibold text-slate-900">Akses cepat</h2>
              <p class="mt-1 text-sm text-slate-500">Lanjutkan pekerjaan toko Anda.</p>
            </div>

            <div class="mt-5 space-y-3">
              <RouterLink
                to="/products"
                class="group flex items-center gap-4 rounded-xl border border-slate-200 p-4 transition hover:border-indigo-200 hover:bg-indigo-50/50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 4v16m8-8H4" />
                  </svg>
                </span>
                <span class="min-w-0 flex-1">
                  <span class="block text-sm font-semibold text-slate-900">Kelola produk</span>
                  <span class="mt-1 block text-xs text-slate-500">Tambah, cari, atau perbarui produk</span>
                </span>
                <svg class="h-4 w-4 shrink-0 text-slate-400 transition group-hover:translate-x-0.5 group-hover:text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </RouterLink>

              <RouterLink
                to="/categories"
                class="group flex items-center gap-4 rounded-xl border border-slate-200 p-4 transition hover:border-sky-200 hover:bg-sky-50/50 focus:outline-none focus:ring-2 focus:ring-sky-500"
              >
                <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-sky-50 text-sky-600">
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                </span>
                <span class="min-w-0 flex-1">
                  <span class="block text-sm font-semibold text-slate-900">Kelola kategori</span>
                  <span class="mt-1 block text-xs text-slate-500">Atur pengelompokan produk</span>
                </span>
                <svg class="h-4 w-4 shrink-0 text-slate-400 transition group-hover:translate-x-0.5 group-hover:text-sky-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </RouterLink>
            </div>
          </article>
        </section>
      </template>
    </div>
  </div>
</template>
