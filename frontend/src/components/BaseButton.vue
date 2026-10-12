<script setup>
defineProps({
  variant: { type: String, default: 'primary' },
  type: { type: String, default: 'button' },
  disabled: Boolean,
});
</script>

<template>
  <button
    :type="type"
    :disabled="disabled"
    :class="{
      'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-500': variant === 'primary',
      'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 focus:ring-slate-300': variant === 'secondary',
      'border border-red-200 bg-red-50 text-red-700 hover:bg-red-100 focus:ring-red-400': variant === 'danger',
    }"
    class="inline-flex items-center justify-center rounded-xl px-4 py-2.5 text-sm font-semibold shadow-sm transition focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
  >
    <slot />
  </button>
</template>
