<template>
  <div class="min-h-screen bg-slate-50 px-4 py-6 text-slate-900 sm:px-6 lg:px-8">
    <div class="mx-auto w-full max-w-7xl">
      <!-- Header -->
      <div class="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Dashboard</h1>
          <p class="mt-1 text-sm text-slate-500 sm:text-base">Overview of your product statistics.</p>
        </div>
        <button
          @click="fetchDashboardStats"
          :disabled="loading"
          class="inline-flex items-center rounded-xl border border-transparent bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:opacity-50"
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
      <div v-if="error" class="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-slate-900" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-slate-500 font-medium">Loading statistics...</span>
      </div>

      <!-- Stats Grid -->
      <div v-else-if="stats" class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <!-- Total Products -->
        <div class="bg-white overflow-hidden shadow-sm rounded-xl border border-slate-200">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0 bg-blue-50 rounded-md p-3">
                <svg class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-slate-500 truncate">Total Products</dt>
                  <dd>
                    <div class="text-2xl font-bold text-slate-900">{{ stats.total_products }}</div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- Active Products -->
        <div class="bg-white overflow-hidden shadow-sm rounded-xl border border-slate-200">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0 bg-emerald-50 rounded-md p-3">
                <svg class="h-6 w-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-slate-500 truncate">Active Products</dt>
                  <dd>
                    <div class="text-2xl font-bold text-slate-900">{{ stats.active_products }}</div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- Inactive Products -->
        <div class="bg-white overflow-hidden shadow-sm rounded-xl border border-slate-200">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0 bg-red-50 rounded-md p-3">
                <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-slate-500 truncate">Inactive Products</dt>
                  <dd>
                    <div class="text-2xl font-bold text-slate-900">{{ stats.inactive_products }}</div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- Total Stock -->
        <div class="bg-white overflow-hidden shadow-sm rounded-xl border border-slate-200">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0 bg-amber-50 rounded-md p-3">
                <svg class="h-6 w-6 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-slate-500 truncate">Total Stock</dt>
                  <dd>
                    <div class="text-2xl font-bold text-slate-900">{{ stats.total_stock }}</div>
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
