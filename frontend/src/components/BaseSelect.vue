<script setup>
defineProps({
  id: { type: String, required: true },
  modelValue: { type: [String, Number], default: '' },
  disabled: Boolean,
  required: Boolean,
  error: { type: String, default: '' },
});

const emit = defineEmits(['update:modelValue']);
</script>

<template>
  <div class="relative">
    <select
      :id="id"
      :value="modelValue"
      :disabled="disabled"
      :required="required"
      :aria-invalid="error ? 'true' : undefined"
      :aria-describedby="error ? `${id}-error` : undefined"
      class="block w-full appearance-none rounded-xl border bg-white px-4 py-3 pr-10 text-sm font-medium text-slate-900 shadow-sm outline-none transition focus:ring-2 disabled:cursor-not-allowed disabled:bg-slate-100"
      :class="error
        ? 'border-red-400 focus:border-red-400 focus:ring-red-100'
        : 'border-slate-300 hover:border-slate-400 focus:border-indigo-600 focus:ring-indigo-100'"
      @change="emit('update:modelValue', $event.target.value)"
    >
      <slot />
    </select>

    <svg
      class="pointer-events-none absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500"
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
    >
      <path
        fill-rule="evenodd"
        d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.51a.75.75 0 01-1.08 0l-4.25-4.51a.75.75 0 01.02-1.06z"
        clip-rule="evenodd"
      />
    </svg>
  </div>
</template>
