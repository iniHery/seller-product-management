<script setup>
import { computed, onMounted, ref, onBeforeUnmount } from 'vue';
import { RouterLink } from 'vue-router';
import { getDashboardStats } from '@/api/dashboardService';
import { formatCurrency } from '@/utils/formatters';
import DashboardDonutChart from '@/components/DashboardDonutChart.vue';

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

const criticalStockCount = computed(() => {
  if (!stats.value) return 0;
  return (stats.value.low_stock_products || 0) + (stats.value.out_of_stock_products || 0);
});

const stockHealth = computed(() => {
  if (!stats.value || !stats.value.active_products) {
    return { safe: 0, safePercent: 0, low: 0, lowPercent: 0, out: 0, outPercent: 0 };
  }

  const total = stats.value.active_products;
  const out = stats.value.out_of_stock_products || 0;
  const low = stats.value.low_stock_products || 0;
  const safe = Math.max(0, total - out - low);

  return {
    safe,
    safePercent: Math.round((safe / total) * 100),
    low,
    lowPercent: Math.round((low / total) * 100),
    out,
    outPercent: Math.round((out / total) * 100),
  };
});


// Dashboard metric cards definition
const metricCards = computed(() => {
  if (!stats.value) return [];
  const totalProducts = stats.value.total_products || 0;
  const activeProducts = stats.value.active_products || 0;
  const inactiveProducts = stats.value.inactive_products || 0;
  const totalStock = stats.value.total_stock || 0;
  const totalValuation = stats.value.total_valuation || 0;
  const valuation = formatCurrency(totalValuation);
  return [
    { label: 'Total Produk', value: totalProducts, icon: 'products', iconClass: 'bg-indigo-100 text-indigo-600' },
    { label: 'Produk Aktif', value: activeProducts, icon: 'active', iconClass: 'bg-emerald-100 text-emerald-600' },
    { label: 'Produk Tidak Aktif', value: inactiveProducts, icon: 'inactive', iconClass: 'bg-gray-100 text-gray-600' },
    { label: 'Stok Total', value: totalStock, icon: 'stock', iconClass: 'bg-sky-100 text-sky-600' },
    { label: 'Valuasi inventaris', value: valuation, icon: 'valuation', iconClass: 'bg-amber-100 text-amber-600' },
  ];
});
const valuationCard = computed(() =>
  metricCards.value.find(
    (card) => card.label === 'Valuasi inventaris'
  )
);

const otherCards = computed(() =>
  metricCards.value.filter(
    (card) => card.label !== 'Valuasi inventaris'
  )
);

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

onMounted(() => {
  fetchDashboardStats();
  // Set up periodic refresh every 60 seconds
  const intervalId = setInterval(fetchDashboardStats, 60_000);
  onBeforeUnmount(() => clearInterval(intervalId));
});
</script>

<template>
  <div class="min-h-full bg-slate-50 px-4 py-6 text-slate-900 sm:px-6 sm:py-8 lg:px-8">
    <div class="mx-auto w-full min-w-0 max-w-7xl">
      <!-- Header Banner -->
      <section class="relative isolate mb-7 overflow-hidden rounded-3xl bg-linear-to-br from-slate-950 via-indigo-950 to-indigo-800 px-5 py-7 text-white shadow-lg shadow-indigo-950/10 sm:px-8 sm:py-9">
        <div class="pointer-events-none absolute -right-12 -top-24 -z-10 h-64 w-64 rounded-full bg-indigo-400/20 blur-3xl"></div>
        <div class="pointer-events-none absolute -bottom-32 right-1/3 -z-10 h-56 w-56 rounded-full bg-sky-300/10 blur-3xl"></div>

        <div class="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
          <div class="min-w-0">
            <p class="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-indigo-200">
              Nivora
            </p>
            <h1 class="text-2xl font-bold tracking-tight sm:text-3xl">Dasbor Penjual</h1>
            <p class="mt-2 max-w-2xl text-sm leading-6 text-indigo-100 sm:text-base">
              Pantau performa stok, nilai inventaris, dan komposisi kategori toko Anda secara real-time.
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

      <!-- Low Stock / Critical Alert Banner (Tahap 1) -->
      <div
        v-if="stats && criticalStockCount > 0"
        class="mb-6 flex flex-col gap-4 rounded-2xl border border-amber-200 bg-amber-50/90 p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-6 sm:py-4.5"
        role="alert"
      >
        <div class="flex items-start gap-3.5">
          <div class="rounded-xl bg-amber-100 p-2 text-amber-700 shrink-0">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div>
            <h3 class="text-sm font-bold text-amber-900">Perhatian: Stok Kritis Terdeteksi</h3>
            <p class="mt-0.5 text-xs sm:text-sm text-amber-800">
              Terdapat <strong>{{ criticalStockCount }} produk</strong> dengan persediaan kritis
              ({{ stats.out_of_stock_products || 0 }} unit habis, {{ stats.low_stock_products || 0 }} unit menipis &le; 5 unit).
            </p>
          </div>
        </div>
        <RouterLink
          :to="{ path: '/products', query: { stock_status: 'critical' } }"
          class="inline-flex shrink-0 items-center justify-center rounded-xl bg-amber-600 px-4 py-2.5 text-xs sm:text-sm font-semibold text-white shadow-sm transition hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-amber-500"
        >
          Tinjau Stok Kritis &rarr;
        </RouterLink>
      </div>

      <!-- Error State -->
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

      <!-- Loading State Skeleton -->
      <section
        v-if="loading && !stats"
        class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5"
        aria-label="Memuat ringkasan statistik"
        role="status"
      >
        <div
          v-for="item in 5"
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

      <!-- Dashboard Content -->
      <template v-else-if="stats">
        <!-- 5 Summary Cards Grid -->
        <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6" aria-label="Ringkasan produk">
          <article
            v-for="card in metricCards"
            :key="card.label"
            :class="['relative min-w-0 overflow-visible rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-md sm:p-6', card.label === 'Valuasi inventaris' ? 'col-span-2' : '']"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="text-xs sm:text-sm font-medium text-slate-500">{{ card.label }}</p>
                <p class="mt-2.5 text-2xl sm:text-3xl font-bold tracking-tight text-slate-950 tabular-nums whitespace-nowrap">
                  {{ card.value }}
                </p>
              </div>
              <div class="shrink-0 rounded-xl p-3" :class="card.iconClass">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path v-if="card.icon === 'products'" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                  <path v-else-if="card.icon === 'active'" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path v-else-if="card.icon === 'stock'" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                  <path v-else-if="card.icon === 'valuation'" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.770 1.333.192 3 1.732 3z" />
                </svg>
              </div>
            </div>
            <p class="mt-3 text-xs leading-5 text-slate-500">{{ card.description }}</p>
            <div class="absolute inset-x-0 bottom-0 h-1 rounded-b-xl" :class="card.accentClass"></div>
          </article>
        </section>

        <!-- Analytics Row: Donut Chart & Stock Health Overview (Tahap 4) -->
        <section class="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-5">
          <!-- Category Composition Donut Chart -->
          <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6 lg:col-span-3">
            <div class="mb-5 flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 class="text-base font-semibold text-slate-900">Distribusi Kategori Produk</h2>
                <p class="mt-1 text-sm text-slate-500">Komposisi jumlah produk aktif berdasarkan kategori.</p>
              </div>
              <span class="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">
                {{ stats.category_distribution?.length || 0 }} Kategori
              </span>
            </div>

            <div v-if="stats.total_products > 0">
              <DashboardDonutChart
                :items="stats.category_distribution || []"
                :total-products="stats.active_products || 0"
              />
            </div>
            <div v-else class="py-12 text-center text-sm text-slate-400">
              Belum ada data produk aktif untuk dianalisis.
            </div>
          </article>

          <!-- Stock Health & Availability Overview -->
          <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6 lg:col-span-2 flex flex-col justify-between">
            <div>
              <div class="flex items-start justify-between gap-3">
                <div>
                  <h2 class="text-base font-semibold text-slate-900">Kesehatan Stok</h2>
                  <p class="mt-1 text-sm text-slate-500">Pemantauan persediaan barang di toko.</p>
                </div>
                <span
                  class="rounded-full px-2.5 py-1 text-xs font-semibold"
                  :class="criticalStockCount > 0 ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'"
                >
                  {{ criticalStockCount > 0 ? 'Perlu Restock' : 'Semua Aman' }}
                </span>
              </div>

              <!-- Multi-segment Progress Bar -->
              <div class="mt-6">
                <div class="flex h-3 w-full overflow-hidden rounded-full bg-slate-100 shadow-inner">
                  <div
                    class="bg-emerald-500 transition-all duration-500"
                    :style="{ width: `${stockHealth.safePercent}%` }"
                    title="Stok Aman (>5)"
                  ></div>
                  <div
                    class="bg-amber-500 transition-all duration-500"
                    :style="{ width: `${stockHealth.lowPercent}%` }"
                    title="Stok Menipis (1-5)"
                  ></div>
                  <div
                    class="bg-rose-500 transition-all duration-500"
                    :style="{ width: `${stockHealth.outPercent}%` }"
                    title="Stok Habis (0)"
                  ></div>
                </div>

                <!-- Segments Details Cards -->
                <div class="mt-5 space-y-2.5">
                  <div class="flex items-center justify-between rounded-xl bg-emerald-50/60 px-3.5 py-2.5">
                    <div class="flex items-center gap-2.5">
                      <span class="h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
                      <span class="text-xs font-semibold text-emerald-900">Stok Aman (> 5 unit)</span>
                    </div>
                    <span class="text-xs font-bold tabular-nums text-emerald-800">
                      {{ stockHealth.safe }} produk ({{ stockHealth.safePercent }}%)
                    </span>
                  </div>

                  <div class="flex items-center justify-between rounded-xl bg-amber-50/70 px-3.5 py-2.5">
                    <div class="flex items-center gap-2.5">
                      <span class="h-2.5 w-2.5 rounded-full bg-amber-500"></span>
                      <span class="text-xs font-semibold text-amber-900">Stok Menipis (1 - 5 unit)</span>
                    </div>
                    <span class="text-xs font-bold tabular-nums text-amber-800">
                      {{ stockHealth.low }} produk ({{ stockHealth.lowPercent }}%)
                    </span>
                  </div>

                  <div class="flex items-center justify-between rounded-xl bg-rose-50/70 px-3.5 py-2.5">
                    <div class="flex items-center gap-2.5">
                      <span class="h-2.5 w-2.5 rounded-full bg-rose-500"></span>
                      <span class="text-xs font-semibold text-rose-900">Stok Habis (0 unit)</span>
                    </div>
                    <span class="text-xs font-bold tabular-nums text-rose-800">
                      {{ stockHealth.out }} produk ({{ stockHealth.outPercent }}%)
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div class="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span>Batas aman: &gt; 5 unit</span>
              <RouterLink
                to="/products"
                class="font-semibold text-indigo-600 hover:text-indigo-700 hover:underline"
              >
                Lihat di Katalog &rarr;
              </RouterLink>
            </div>
          </article>
        </section>

        <!-- Bottom Row: Quick Restock Table & Quick Actions -->
        <section class="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-5">
          <!-- Critical Items Quick Table (Tahap 1 & 4) -->
          <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6 lg:col-span-3">
            <div class="flex items-center justify-between gap-3 mb-4">
              <div>
                <h2 class="text-base font-semibold text-slate-900">Prioritas Restock</h2>
                <p class="mt-0.5 text-xs sm:text-sm text-slate-500">Daftar produk aktif dengan ketersediaan terendah.</p>
              </div>
              <RouterLink
                v-if="stats.critical_products && stats.critical_products.length > 0"
                :to="{ path: '/products', query: { stock_status: 'critical' } }"
                class="text-xs font-semibold text-indigo-600 hover:text-indigo-700 hover:underline"
              >
                Lihat Semua ({{ criticalStockCount }}) &rarr;
              </RouterLink>
            </div>

            <div v-if="stats.critical_products && stats.critical_products.length > 0" class="overflow-x-auto">
              <table class="w-full text-left text-xs sm:text-sm">
                <thead>
                  <tr class="border-b border-slate-100 text-slate-500">
                    <th scope="col" class="pb-2.5 font-semibold">Produk</th>
                    <th scope="col" class="pb-2.5 font-semibold">Kategori</th>
                    <th scope="col" class="pb-2.5 font-semibold text-center">Sisa Stok</th>
                    <th scope="col" class="pb-2.5 font-semibold text-right">Aksi</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                  <tr v-for="item in stats.critical_products" :key="item.id" class="hover:bg-slate-50/60 transition">
                    <td class="py-3 pr-2">
                      <p class="font-semibold text-slate-900 truncate max-w-44 sm:max-w-xs">{{ item.name }}</p>
                      <p class="text-xs text-slate-400">SKU: {{ item.sku }}</p>
                    </td>
                    <td class="py-3 px-2 text-slate-600">{{ item.category_name }}</td>
                    <td class="py-3 px-2 text-center">
                      <span
                        v-if="item.is_out_of_stock"
                        class="inline-flex rounded-md bg-rose-50 px-2 py-0.5 text-xs font-bold text-rose-700 ring-1 ring-inset ring-rose-600/20"
                      >
                        Habis (0)
                      </span>
                      <span
                        v-else
                        class="inline-flex rounded-md bg-amber-50 px-2 py-0.5 text-xs font-bold text-amber-700 ring-1 ring-inset ring-amber-600/20"
                      >
                        {{ item.stock }} unit
                      </span>
                    </td>
                    <td class="py-3 pl-2 text-right">
                      <RouterLink
                        :to="`/products`"
                        class="rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-indigo-600 hover:bg-indigo-50"
                      >
                        Kelola
                      </RouterLink>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-else class="rounded-xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center">
              <p class="text-sm font-medium text-emerald-800">Semua produk memiliki persediaan aman!</p>
              <p class="mt-1 text-xs text-slate-500">Tidak ada produk aktif dengan persediaan &le; 5 unit saat ini.</p>
            </div>
          </article>

          <!-- Quick Actions Panel -->
          <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6 lg:col-span-2">
            <div>
              <h2 class="text-base font-semibold text-slate-900">Akses Cepat</h2>
              <p class="mt-1 text-sm text-slate-500">Pintasan navigasi operasional toko Anda.</p>
            </div>

            <div class="mt-5 space-y-3">
              <RouterLink
                to="/products"
                class="group flex items-center gap-4 rounded-xl border border-slate-200 p-3.5 transition hover:border-indigo-200 hover:bg-indigo-50/50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 4v16m8-8H4" />
                  </svg>
                </span>
                <span class="min-w-0 flex-1">
                  <span class="block text-sm font-semibold text-slate-900">Kelola Produk</span>
                  <span class="mt-0.5 block text-xs text-slate-500">Tambah, cari, atau perbarui produk</span>
                </span>
                <svg class="h-4 w-4 shrink-0 text-slate-400 transition group-hover:translate-x-0.5 group-hover:text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </RouterLink>

              <RouterLink
                :to="{ path: '/products', query: { stock_status: 'critical' } }"
                class="group flex items-center gap-4 rounded-xl border border-slate-200 p-3.5 transition hover:border-amber-200 hover:bg-amber-50/50 focus:outline-none focus:ring-2 focus:ring-amber-500"
              >
                <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </span>
                <span class="min-w-0 flex-1">
                  <span class="block text-sm font-semibold text-slate-900">Filter Stok Kritis</span>
                  <span class="mt-0.5 block text-xs text-slate-500">Lihat semua barang yang butuh restock</span>
                </span>
                <svg class="h-4 w-4 shrink-0 text-slate-400 transition group-hover:translate-x-0.5 group-hover:text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </RouterLink>

              <RouterLink
                to="/categories"
                class="group flex items-center gap-4 rounded-xl border border-slate-200 p-3.5 transition hover:border-sky-200 hover:bg-sky-50/50 focus:outline-none focus:ring-2 focus:ring-sky-500"
              >
                <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-sky-50 text-sky-600">
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                </span>
                <span class="min-w-0 flex-1">
                  <span class="block text-sm font-semibold text-slate-900">Kelola Kategori</span>
                  <span class="mt-0.5 block text-xs text-slate-500">Atur pengelompokan etalase toko</span>
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
