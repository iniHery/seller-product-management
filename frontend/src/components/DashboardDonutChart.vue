<script setup>
import { computed } from 'vue';

const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  totalProducts: {
    type: Number,
    default: 0,
  },
});

// Curated harmonious color palette
const palette = [
  { fill: '#6366f1', bg: 'bg-indigo-500', text: 'text-indigo-600', ring: 'ring-indigo-200' }, // Indigo
  { fill: '#10b981', bg: 'bg-emerald-500', text: 'text-emerald-600', ring: 'ring-emerald-200' }, // Emerald
  { fill: '#f59e0b', bg: 'bg-amber-500', text: 'text-amber-600', ring: 'ring-amber-200' }, // Amber
  { fill: '#0ea5e9', bg: 'bg-sky-500', text: 'text-sky-600', ring: 'ring-sky-200' }, // Sky
  { fill: '#ec4899', bg: 'bg-pink-500', text: 'text-pink-600', ring: 'ring-pink-200' }, // Pink
  { fill: '#8b5cf6', bg: 'bg-violet-500', text: 'text-violet-600', ring: 'ring-violet-200' }, // Violet
];

const CIRCUMFERENCE = 2 * Math.PI * 40; // ~251.327

const chartSegments = computed(() => {
  if (!props.items || props.items.length === 0) return [];

  const totalCount = props.items.reduce((acc, curr) => acc + (curr.count || 0), 0);
  if (totalCount === 0) return [];

  let accumulatedPercent = 0;

  return props.items.map((item, index) => {
    const percent = item.percentage != null
      ? item.percentage
      : (totalCount > 0 ? (item.count / totalCount) * 100 : 0);
    const dashLength = (percent / 100) * CIRCUMFERENCE;
    const dashOffset = -(accumulatedPercent / 100) * CIRCUMFERENCE;
    accumulatedPercent += percent;

    const color = palette[index % palette.length];

    return {
      ...item,
      color,
      dashArray: `${dashLength} ${CIRCUMFERENCE}`,
      dashOffset,
      displayPercent: Math.round(percent),
    };
  });
});
</script>

<template>
  <div class="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
    <!-- SVG Donut Chart -->
    <div class="relative mx-auto flex h-48 w-48 shrink-0 items-center justify-center">
      <svg class="h-full w-full -rotate-90 transform" viewBox="0 0 100 100">
        <!-- Background Circle -->
        <circle
          cx="50"
          cy="50"
          r="40"
          stroke="#f1f5f9"
          stroke-width="14"
          fill="transparent"
        />

        <!-- Segments -->
        <circle
          v-for="segment in chartSegments"
          :key="segment.category_name"
          cx="50"
          cy="50"
          r="40"
          :stroke="segment.color.fill"
          stroke-width="14"
          fill="transparent"
          :stroke-dasharray="segment.dashArray"
          :stroke-dashoffset="segment.dashOffset"
          stroke-linecap="round"
          class="transition-all duration-500 ease-out hover:opacity-85"
        />
      </svg>

      <!-- Center Info -->
      <div class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
        <span class="text-2xl font-bold tracking-tight text-slate-900 tabular-nums">
          {{ totalProducts }}
        </span>
        <span class="text-xs font-medium text-slate-500">Produk</span>
      </div>
    </div>

    <!-- Legend -->
    <div class="flex-1 space-y-2.5">
      <div
        v-for="segment in chartSegments"
        :key="segment.category_name"
        class="flex items-center justify-between rounded-xl px-3 py-2 transition hover:bg-slate-50"
      >
        <div class="flex items-center gap-2.5 min-w-0">
          <span
            class="h-3 w-3 shrink-0 rounded-full"
            :class="segment.color.bg"
          />
          <span class="truncate text-sm font-medium text-slate-700">
            {{ segment.category_name }}
          </span>
        </div>
        <div class="flex items-center gap-3 shrink-0">
          <span class="text-xs font-semibold text-slate-500 tabular-nums">
            {{ segment.count }} unit
          </span>
          <span
            class="rounded-md px-1.5 py-0.5 text-xs font-bold tabular-nums"
            :class="[segment.color.text, 'bg-slate-100']"
          >
            {{ segment.displayPercent }}%
          </span>
        </div>
      </div>

      <div
        v-if="chartSegments.length === 0"
        class="py-6 text-center text-sm text-slate-400"
      >
        Belum ada data distribusi produk.
      </div>
    </div>
  </div>
</template>
