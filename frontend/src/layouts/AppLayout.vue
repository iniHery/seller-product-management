<script setup>
import { ref, computed, h } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const mobileMenuOpen = ref(false);
const loggingOut = ref(false);
const logoutError = ref('');

const userInitial = computed(() => {
  const username = authStore.user?.username || '';
  return username.charAt(0).toUpperCase() || '?';
});

// Inline SVG icon components
const IconDashboard = {
  render() {
    return h('svg', {
      class: 'h-5 w-5',
      fill: 'none',
      viewBox: '0 0 24 24',
      stroke: 'currentColor',
      'stroke-width': '2',
    }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        d: 'M4 5a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm10 0a1 1 0 011-1h4a1 1 0 011 1v2a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zm0 7a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1h-4a1 1 0 01-1-1v-5zm-10-2a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1H5a1 1 0 01-1-1v-5z',
      }),
    ]);
  },
};

const IconProducts = {
  render() {
    return h('svg', {
      class: 'h-5 w-5',
      fill: 'none',
      viewBox: '0 0 24 24',
      stroke: 'currentColor',
      'stroke-width': '2',
    }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        d: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4',
      }),
    ]);
  },
};

const IconCategories = {
  render() {
    return h('svg', {
      class: 'h-5 w-5',
      fill: 'none',
      viewBox: '0 0 24 24',
      stroke: 'currentColor',
      'stroke-width': '2',
    }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        d: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z',
      }),
    ]);
  },
};

const navItems = [
  {
    name: 'dashboard',
    label: 'Dasbor',
    path: '/dashboard',
    routeName: 'Dashboard',
    icon: IconDashboard,
  },
  {
    name: 'products',
    label: 'Produk',
    path: '/products',
    routeName: 'Products',
    icon: IconProducts,
  },
  {
    name: 'categories',
    label: 'Kategori',
    path: '/categories',
    routeName: 'Categories',
    icon: IconCategories,
  },
];

function isActive(routeName) {
  return route.name === routeName;
}

async function handleLogout() {
  loggingOut.value = true;
  logoutError.value = '';

  try {
    await authStore.logout();
    mobileMenuOpen.value = false;
    await router.push({ name: 'Login' });
  } catch {
    logoutError.value = 'Gagal mengakhiri sesi di server. Anda masih masuk; periksa koneksi lalu coba lagi.';
  } finally {
    loggingOut.value = false;
  }
}
</script>


<template>
  <div class="min-h-screen w-full bg-slate-50">

    <div class="sticky top-0 z-40 flex items-center justify-between gap-3 border-b border-slate-200 bg-white px-4 py-3 lg:hidden">
      <span class="min-w-0 truncate text-sm font-bold tracking-tight text-slate-900">
        Seller Product Management
      </span>

      <button
        type="button"
        @click="mobileMenuOpen = !mobileMenuOpen"
        class="inline-flex shrink-0 items-center justify-center rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        :aria-label="mobileMenuOpen ? 'Tutup menu navigasi' : 'Buka menu navigasi'"
        :aria-expanded="mobileMenuOpen"
        aria-controls="mobile-navigation"
      >
        <svg
          v-if="!mobileMenuOpen"
          class="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>

        <svg
          v-else
          class="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>

    <!-- Mobile navigation drawer -->
    <div
      v-if="mobileMenuOpen"
      class="fixed inset-0 z-50 lg:hidden"
    >
      <div
        class="absolute inset-0 bg-slate-950/40"
        @click="mobileMenuOpen = false"
      ></div>

      <nav
        id="mobile-navigation"
        aria-label="Mobile navigation"
        class="fixed inset-y-0 left-0 z-10 flex w-64 max-w-[calc(100vw-2rem)] flex-col border-r border-slate-200 bg-white shadow-xl"
      >
        <div class="flex h-16 shrink-0 items-center justify-between gap-3 px-5">
          <span class="min-w-0 text-base font-bold leading-tight tracking-tight text-slate-900">
            Seller Product Management
          </span>
          <button
            type="button"
            @click="mobileMenuOpen = false"
            class="inline-flex shrink-0 items-center justify-center rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            aria-label="Tutup menu navigasi"
          >
            <svg
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div class="flex min-h-0 flex-1 flex-col overflow-y-auto px-3 py-4">
          <ul class="space-y-1">
            <li v-for="item in navItems" :key="item.name">
              <router-link
                :to="item.path"
                @click="mobileMenuOpen = false"
                class="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition"
                :aria-current="isActive(item.routeName) ? 'page' : undefined"
                :class="
                  isActive(item.routeName)
                    ? 'bg-indigo-50 text-indigo-700'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                "
              >
                <component :is="item.icon" />
                {{ item.label }}
              </router-link>
            </li>
          </ul>

          <div class="mt-auto border-t border-slate-200 pt-4">
            <div
              v-if="authStore.user"
              class="mb-3 flex items-center gap-3 rounded-xl px-3 py-2"
            >
              <div
                class="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-xs font-bold uppercase text-indigo-700"
              >
                {{ userInitial }}
              </div>

              <span class="truncate text-sm font-medium text-slate-600">
                {{ authStore.user.username }}
              </span>
            </div>

            <button
              type="button"
              @click="handleLogout"
              :disabled="loggingOut"
              class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-red-600 transition hover:bg-red-50 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <svg
                class="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
              {{ loggingOut ? 'Keluar...' : 'Keluar' }}
            </button>
          </div>
        </div>
      </nav>
    </div>

    <!-- Desktop layout -->
    <div class="flex min-h-screen">

      <aside
        class="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col lg:border-r lg:border-slate-200"
      >
        <div class="flex min-h-0 flex-1 flex-col bg-white">

          <div class="flex h-16 shrink-0 items-center border-b border-slate-100 px-6">
            <span class="text-base font-bold leading-tight tracking-tight text-slate-900 lg:text-lg">
              Seller Product Management
            </span>
          </div>

          <div class="flex min-h-0 flex-1 flex-col overflow-y-auto px-3 py-4">
            <ul class="space-y-1">
              <li v-for="item in navItems" :key="item.name">
                <router-link
                  :to="item.path"
                  class="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition"
                  :aria-current="isActive(item.routeName) ? 'page' : undefined"
                  :class="
                    isActive(item.routeName)
                      ? 'bg-indigo-50 text-indigo-700'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  "
                >
                  <component :is="item.icon" />
                  {{ item.label }}
                </router-link>
              </li>
            </ul>

            <div class="mt-auto border-t border-slate-200 pt-4">
              <div
                v-if="authStore.user"
                class="mb-3 flex items-center gap-3 rounded-xl px-3 py-2"
              >
                <div
                  class="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-xs font-bold uppercase text-indigo-700"
                >
                  {{ userInitial }}
                </div>

                <span class="truncate text-sm font-medium text-slate-600">
                  {{ authStore.user.username }}
                </span>
              </div>

              <button
                type="button"
                @click="handleLogout"
                :disabled="loggingOut"
                class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-red-600 transition hover:bg-red-50 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <svg
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                  />
                </svg>
                {{ loggingOut ? 'Keluar...' : 'Keluar' }}
              </button>
            </div>
          </div>
        </div>
      </aside>

      <main class="min-w-0 w-full flex-1 lg:pl-64">
        <div
          v-if="logoutError"
          role="alert"
          class="mx-4 mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700 sm:mx-6 lg:mx-8"
        >
          {{ logoutError }}
        </div>
        <router-view />
      </main>
    </div>
  </div>
</template>