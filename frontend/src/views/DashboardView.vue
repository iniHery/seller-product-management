<template>
  <div class="min-h-screen w-full bg-slate-50 px-4 py-6 text-slate-900 sm:px-6 sm:py-8 lg:px-8">
    <div class="mx-auto w-full min-w-0 max-w-7xl">
      <!-- Header -->
      <div class="mb-6 flex flex-col gap-4 sm:mb-8 sm:flex-row sm:items-center sm:justify-between">
        <div class="min-w-0">
          <h1 class="text-2xl font-bold leading-tight tracking-tight text-slate-900 sm:text-3xl">
            Dashboard
          </h1>
          <p class="mt-2 text-sm leading-6 text-slate-500 sm:text-base">
            Overview of your product statistics.
          </p>
        </div>
        <button
          @click="fetchDashboardStats"
          :disabled="loading"
          class="inline-flex min-h-10 w-full items-center justify-center whitespace-nowrap rounded-xl border border-transparent bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
        >
          <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="-ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      <!-- Notifications -->
      <div v-if="error" role="alert" class="mb-6 rounded-2xl border border-red-200 bg-red-50 p-4 sm:p-5">
        <div class="flex items-start gap-3">
          <div class="shrink-0">
            <svg class="h-5 w-5 text-red-600" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="wrap-break-word text-sm leading-6 text-red-700">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div
        v-if="loading"
        class="flex min-h-48 flex-col items-center justify-center gap-3 rounded-2xl border border-slate-200 bg-white px-6 py-12 shadow-sm"
        role="status"
        aria-live="polite"
      >
        <svg class="h-8 w-8 animate-spin text-slate-900" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-sm font-medium text-slate-500">Loading statistics...</span>
      </div>

      <!-- Stats Grid -->
      <div v-else-if="stats" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 lg:gap-5">
        <!-- Total Products -->
        <div class="flex h-full min-h-32 min-w-0 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div class="flex w-full items-center p-5 sm:p-6">
            <div class="flex min-w-0 flex-1 items-center gap-4">
              <div class="shrink-0 rounded-xl bg-blue-50 p-3">
                <svg class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <div class="min-w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium leading-5 text-slate-500">Total Products</dt>
                  <dd>
                    <div class="mt-1 wrap-break-word text-2xl font-bold leading-tight tabular-nums text-slate-900 sm:text-3xl">{{ stats.total_products }}</div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- Active Products -->
        <div class="flex h-full min-h-32 min-w-0 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div class="flex w-full items-center p-5 sm:p-6">
            <div class="flex min-w-0 flex-1 items-center gap-4">
              <div class="shrink-0 rounded-xl bg-emerald-50 p-3">
                <svg class="h-6 w-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="min-w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium leading-5 text-slate-500">Active Products</dt>
                  <dd>
                    <div class="mt-1 wrap-break-word text-2xl font-bold leading-tight tabular-nums text-slate-900 sm:text-3xl">{{ stats.active_products }}</div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- Inactive Products -->
        <div class="flex h-full min-h-32 min-w-0 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div class="flex w-full items-center p-5 sm:p-6">
            <div class="flex min-w-0 flex-1 items-center gap-4">
              <div class="shrink-0 rounded-xl bg-red-50 p-3">
                <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="min-w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium leading-5 text-slate-500">Inactive Products</dt>
                  <dd>
                    <div class="mt-1 wrap-break-word text-2xl font-bold leading-tight tabular-nums text-slate-900 sm:text-3xl">{{ stats.inactive_products }}</div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- Total Stock -->
        <div class="flex h-full min-h-32 min-w-0 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div class="flex w-full items-center p-5 sm:p-6">
            <div class="flex min-w-0 flex-1 items-center gap-4">
              <div class="shrink-0 rounded-xl bg-amber-50 p-3">
                <svg class="h-6 w-6 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                </svg>
              </div>
              <div class="min-w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium leading-5 text-slate-500">Total Stock</dt>
                  <dd>
                    <div class="mt-1 wrap-break-word text-2xl font-bold leading-tight tabular-nums text-slate-900 sm:text-3xl">{{ stats.total_stock }}</div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getDashboardStats } from '@/api/dashboardService';

const stats = ref(null);
const loading = ref(true);
const error = ref('');

const fetchDashboardStats = async () => {
  loading.value = true;
  error.value = '';
  try {
    const response = await getDashboardStats();
    if (response.data && response.data.success) {
      stats.value = response.data.data;
    } else {
      error.value = 'Failed to load dashboard statistics.';
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'An error occurred while fetching dashboard statistics.';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchDashboardStats();
});
</script>
