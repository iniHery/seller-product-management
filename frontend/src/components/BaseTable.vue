<script setup>
defineProps({
  tableClass: { type: String, default: 'min-w-full' },
});
</script>

<template>
  <div class="overflow-x-auto">
    <table :class="['divide-y divide-slate-200', tableClass]">
      <slot />
    </table>
  </div>
</template>
