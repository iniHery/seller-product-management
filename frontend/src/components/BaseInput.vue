<script setup>
defineProps({
  id: { type: String, required: true },
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  inputmode: { type: String, default: undefined },
  autocomplete: { type: String, default: undefined },
  disabled: Boolean,
  required: Boolean,
  error: { type: String, default: '' },
  inputClass: { type: String, default: '' },
});

const emit = defineEmits(['update:modelValue']);
</script>

<template>
  <input
    :id="id"
    :type="type"
    :value="modelValue"
    :placeholder="placeholder"
    :inputmode="inputmode"
    :autocomplete="autocomplete"
    :disabled="disabled"
    :required="required"
    :aria-invalid="error ? 'true' : undefined"
    :aria-describedby="error ? `${id}-error` : undefined"
    :class="[
      'block w-full rounded-xl border bg-white px-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 shadow-sm outline-none transition focus:ring-2 disabled:cursor-not-allowed disabled:bg-slate-100',
      error
        ? 'border-red-400 focus:border-red-400 focus:ring-red-100'
        : 'border-slate-300 hover:border-slate-400 focus:border-indigo-600 focus:ring-indigo-100',
      inputClass,
    ]"
    @input="emit('update:modelValue', $event.target.value)"
  />
</template>
