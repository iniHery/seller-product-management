<template>
  <div class="min-h-screen w-full bg-slate-50">

    <div class="sticky top-0 z-40 flex items-center justify-between gap-3 bg-slate-900 px-4 py-3 lg:hidden">
      <span class="min-w-0 truncate text-sm font-bold tracking-tight text-white">
        Seller Product Management
      </span>

      <button
        type="button"
        @click="mobileMenuOpen = !mobileMenuOpen"
        class="inline-flex shrink-0 items-center justify-center rounded-lg p-2 text-slate-300 transition hover:bg-slate-800 hover:text-white focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 focus:ring-offset-slate-900"
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
        class="absolute inset-0 bg-slate-900/60"
        @click="mobileMenuOpen = false"
      ></div>

      <nav
        id="mobile-navigation"
        aria-label="Mobile navigation"
        class="fixed inset-y-0 left-0 z-10 flex w-64 max-w-[calc(100vw-2rem)] flex-col bg-slate-900 shadow-xl"
      >
        <div class="flex h-16 shrink-0 items-center justify-between gap-3 px-5">
          <span class="min-w-0 text-base font-bold leading-tight tracking-tight text-white">
            Seller Product Management
          </span>
          <button
            type="button"
            @click="mobileMenuOpen = false"
            class="inline-flex shrink-0 items-center justify-center rounded-lg p-2 text-slate-300 transition hover:bg-slate-800 hover:text-white focus:outline-none focus:ring-2 focus:ring-slate-400"
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
                    ? 'bg-slate-800 text-white ring-1 ring-inset ring-white/10'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                "
              >
                <component :is="item.icon" />
                {{ item.label }}
              </router-link>
            </li>
          </ul>

          <div class="mt-auto border-t border-slate-700 pt-4">
            <div
              v-if="authStore.user"
              class="mb-3 flex items-center gap-3 rounded-xl px-3 py-2"
            >
              <div
                class="flex h-8 w-8 items-center justify-center rounded-full bg-slate-700 text-xs font-bold uppercase text-white"
              >
                {{ userInitial }}
              </div>

              <span class="truncate text-sm font-medium text-slate-300">
                {{ authStore.user.username }}
              </span>
            </div>

            <button
              type="button"
              @click="handleLogout"
              :disabled="loggingOut"
              class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-red-300 transition hover:bg-slate-800 hover:text-red-200 focus:outline-none focus:ring-2 focus:ring-red-400 disabled:cursor-not-allowed disabled:opacity-50"
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
        class="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col lg:border-r lg:border-slate-800"
      >
        <div class="flex min-h-0 flex-1 flex-col bg-slate-900">

          <div class="flex h-16 shrink-0 items-center px-6">
            <span class="text-base font-bold leading-tight tracking-tight text-white lg:text-lg">
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
                      ? 'bg-slate-800 text-white ring-1 ring-inset ring-white/10'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  "
                >
                  <component :is="item.icon" />
                  {{ item.label }}
                </router-link>
              </li>
            </ul>

            <div class="mt-auto border-t border-slate-700 pt-4">
              <div
                v-if="authStore.user"
                class="mb-3 flex items-center gap-3 rounded-xl px-3 py-2"
              >
                <div
                  class="flex h-8 w-8 items-center justify-center rounded-full bg-slate-700 text-xs font-bold uppercase text-white"
                >
                  {{ userInitial }}
                </div>

                <span class="truncate text-sm font-medium text-slate-300">
                  {{ authStore.user.username }}
                </span>
              </div>

              <button
                type="button"
                @click="handleLogout"
                :disabled="loggingOut"
                class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-red-300 transition hover:bg-slate-800 hover:text-red-200 focus:outline-none focus:ring-2 focus:ring-red-400 disabled:cursor-not-allowed disabled:opacity-50"
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
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, h } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const mobileMenuOpen = ref(false);
const loggingOut = ref(false);

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

  try {
    await authStore.logout();
  } catch {
    // logout() in store already clears auth even on failure
  } finally {
    loggingOut.value = false;
    mobileMenuOpen.value = false;
    router.push({ name: 'Login' });
  }
}
</script>
