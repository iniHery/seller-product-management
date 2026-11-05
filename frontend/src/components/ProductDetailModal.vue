<script setup>
import { formatCurrency, formatDateTime } from '@/utils/formatters';

defineProps({
  product: { type: Object, default: null },
  loading: Boolean,
  error: { type: String, default: '' },
});

const emit = defineEmits(['close']);
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div
      class="fixed inset-0 bg-slate-900/50 backdrop-blur-[1px]"
      @click="emit('close')"
    ></div>

    <section
      role="dialog"
      aria-modal="true"
      aria-labelledby="product-detail-title"
      class="relative max-h-[calc(100vh-2rem)] w-full max-w-2xl overflow-y-auto rounded-2xl border border-slate-200 bg-white p-5 shadow-xl sm:p-6"
    >
      <div class="mb-5 flex items-start justify-between gap-4">
        <div>
          <h2 id="product-detail-title" class="text-xl font-bold text-slate-900">
            Detail Produk
          </h2>
          <p class="mt-1 text-sm text-slate-500">
            Informasi produk
          </p>
        </div>
        <button
          type="button"
          @click="emit('close')"
          class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-300"
          aria-label="Close product details"
        >
          <svg
            class="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true"
          >
            <path
              fill-rule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>

      <div
        v-if="loading"
        class="flex min-h-48 flex-col items-center justify-center gap-3"
        role="status"
        aria-live="polite"
      >
        <div
          class="h-9 w-9 animate-spin rounded-full border-4 border-slate-200 border-t-indigo-600"
          aria-hidden="true"
        ></div>
        <p class="text-sm font-medium text-slate-500">
          Memuat detail produk...
        </p>
      </div>

      <div
        v-else-if="error"
        role="alert"
        class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-700"
      >
        {{ error }}
      </div>

      <dl
        v-else-if="product"
        class="grid grid-cols-1 gap-4 sm:grid-cols-2"
      >
        <div class="min-w-0 rounded-xl bg-slate-50 p-4">
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Nama
          </dt>
          <dd class="mt-1 wrap-break-word text-sm font-semibold text-slate-900">
            {{ product.name || '-' }}
          </dd>
        </div>
        <div class="min-w-0 rounded-xl bg-slate-50 p-4">
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
            SKU
          </dt>
          <dd class="mt-1 wrap-break-word text-sm font-medium text-slate-900">
            {{ product.sku || '-' }}
          </dd>
        </div>
        <div class="min-w-0 rounded-xl bg-slate-50 p-4">
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Kategori
          </dt>
          <dd class="mt-1 wrap-break-word text-sm text-slate-900">
            {{ product.category?.name || '-' }}
          </dd>
        </div>
        <div class="min-w-0 rounded-xl bg-slate-50 p-4">
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Harga
          </dt>
          <dd class="mt-1 text-sm font-semibold text-slate-900">
            {{ formatCurrency(product.price) }}
          </dd>
        </div>
        <div class="min-w-0 rounded-xl bg-slate-50 p-4">
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Stok
          </dt>
          <dd class="mt-1 text-sm text-slate-900">
            {{ product.stock ?? '-' }}
          </dd>
        </div>
        <div class="min-w-0 rounded-xl bg-slate-50 p-4">
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Status & Favorit
          </dt>
          <dd class="mt-1 flex flex-wrap items-center gap-2">
            <span
              class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold"
              :class="product.status === 'active'
                ? 'bg-emerald-100 text-emerald-700'
                : 'bg-slate-200 text-slate-700'"
            >
              {{ product.status === 'active' ? 'Aktif' : 'Tidak Aktif' }}
            </span>
            <span
              v-if="product.is_favorite"
              class="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-800"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 fill-amber-500 text-amber-500" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
              Favorit
            </span>
          </dd>
        </div>
        <div class="rounded-xl bg-slate-50 p-4 sm:col-span-2">
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Deskripsi
          </dt>
          <dd class="mt-1 whitespace-pre-wrap wrap-break-word text-sm leading-6 text-slate-700">
            {{ product.description || '-' }}
          </dd>
        </div>
        <div class="min-w-0 rounded-xl bg-slate-50 p-4">
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Dibuat Pada
          </dt>
          <dd class="mt-1 wrap-break-word text-sm text-slate-700">
            {{ formatDateTime(product.created_at) }}
          </dd>
        </div>
        <div class="min-w-0 rounded-xl bg-slate-50 p-4">
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Diperbarui Pada
          </dt>
          <dd class="mt-1 wrap-break-word text-sm text-slate-700">
            {{ formatDateTime(product.updated_at) }}
          </dd>
        </div>
      </dl>

      <div class="mt-6 flex justify-end border-t border-slate-100 pt-4">
        <button
          type="button"
          @click="emit('close')"
          class="inline-flex w-full justify-center rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-300 sm:w-auto"
        >
          Tutup
        </button>
      </div>
    </section>
  </div>
</template>
