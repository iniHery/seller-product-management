<script setup>
const props = defineProps({
  product: { type: Object, default: null },
  deleting: Boolean,
});

const emit = defineEmits(['cancel', 'confirm']);
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div
      class="fixed inset-0 bg-slate-900/50 backdrop-blur-[1px] transition-opacity"
      @click="!props.deleting && emit('cancel')"
    ></div>

    <div
      class="relative max-h-[calc(100vh-2rem)] w-full max-w-md transform overflow-y-auto rounded-2xl bg-white p-5 text-left shadow-xl transition-all sm:p-6"
    >
      <div class="mb-5">
        <h3 class="text-lg font-bold text-slate-900">
          Hapus Produk?
        </h3>
        <p class="mt-2 text-sm leading-6 text-slate-500">
          Apakah Anda yakin ingin menghapus
          <span class="font-semibold text-slate-900">{{ product?.name }}</span>?
          Tindakan ini tidak dapat dibatalkan.
        </p>
      </div>

      <div class="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <button
          type="button"
          @click="emit('cancel')"
          :disabled="deleting"
          class="inline-flex w-full justify-center rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
        >
          Batal
        </button>
        <button
          type="button"
          @click="emit('confirm')"
          :disabled="deleting"
          class="inline-flex w-full justify-center rounded-xl border border-transparent bg-red-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
        >
          {{ deleting ? 'Menghapus...' : 'Hapus Produk' }}
        </button>
      </div>
    </div>
  </div>
</template>
