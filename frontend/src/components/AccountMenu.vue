<script setup>
defineProps({
  user: { type: Object, default: null },
  userInitial: { type: String, required: true },
  loggingOut: Boolean,
});

const emit = defineEmits(['open-account', 'logout']);
</script>

<template>
  <div v-if="user" class="mb-3">
    <button
      type="button"
      @click="emit('open-account')"
      class="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left transition hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      aria-label="Buka pengaturan akun"
    >
      <span
        class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xs font-bold uppercase text-indigo-700"
      >
        {{ userInitial }}
      </span>

      <span class="truncate text-sm font-medium text-slate-600">
        {{ user.username }}
      </span>
    </button>
  </div>

  <button
    type="button"
    @click="emit('logout')"
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
</template>
