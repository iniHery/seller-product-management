<script setup>
import { ref } from 'vue';
import { downloadProductTemplateCSV, importProductsCSV } from '@/api/productService';
import { triggerFileDownload, generateCSVFilename } from '@/utils/download';

const emit = defineEmits(['close', 'success']);

const selectedFile = ref(null);
const fileInput = ref(null);
const isDragging = ref(false);
const uploading = ref(false);
const downloadingTemplate = ref(false);
const generalError = ref('');
const validationErrors = ref([]);

function handleFileSelect(event) {
  const file = event.target.files?.[0];
  processFile(file);
}

function handleDragOver(event) {
  event.preventDefault();
  isDragging.value = true;
}

function handleDragLeave(event) {
  event.preventDefault();
  isDragging.value = false;
}

function handleDrop(event) {
  event.preventDefault();
  isDragging.value = false;
  const file = event.dataTransfer?.files?.[0];
  processFile(file);
}

function processFile(file) {
  generalError.value = '';
  validationErrors.value = [];

  if (!file) return;

  if (!file.name.toLowerCase().endsWith('.csv')) {
    generalError.value = 'Hanya file dengan format .csv yang didukung.';
    return;
  }

  if (file.size > 5 * 1024 * 1024) {
    generalError.value = 'Ukuran file terlalu besar. Maksimal ukuran file adalah 5 MB.';
    return;
  }

  selectedFile.value = file;
}

function removeFile() {
  selectedFile.value = null;
  generalError.value = '';
  validationErrors.value = [];
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

function triggerBrowse() {
  fileInput.value?.click();
}

async function handleDownloadTemplate() {
  if (downloadingTemplate.value) return;
  downloadingTemplate.value = true;
  generalError.value = '';

  try {
    const response = await downloadProductTemplateCSV();
    triggerFileDownload(response.data, generateCSVFilename('template-import-produk'));
  } catch (err) {
    console.error('Failed to download template:', err);
    generalError.value = 'Gagal mengunduh template CSV. Silakan coba lagi.';
  } finally {
    downloadingTemplate.value = false;
  }
}

async function handleImport() {
  if (!selectedFile.value || uploading.value) return;

  uploading.value = true;
  generalError.value = '';
  validationErrors.value = [];

  try {
    const response = await importProductsCSV(selectedFile.value);
    const message = response.data?.message || 'Produk berhasil diimpor!';
    emit('success', message);
    emit('close');
  } catch (err) {
    console.error('Failed to import products:', err);
    const responseData = err.response?.data;
    if (responseData?.errors && Array.isArray(responseData.errors)) {
      validationErrors.value = responseData.errors;
      generalError.value = responseData.message || 'Ditemukan beberapa kesalahan validasi pada file CSV.';
    } else if (responseData?.message) {
      generalError.value = responseData.message;
    } else if (err.response?.data?.detail) {
      generalError.value = err.response.data.detail;
    } else {
      generalError.value = 'Terjadi kesalahan saat memproses file CSV. Periksa koneksi dan coba lagi.';
    }
  } finally {
    uploading.value = false;
  }
}

function formatFileSize(bytes) {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div
      class="fixed inset-0 bg-slate-900/50 backdrop-blur-[1px] transition-opacity"
      @click="emit('close')"
    ></div>

    <!-- Modal Dialog -->
    <section
      role="dialog"
      aria-modal="true"
      aria-labelledby="product-import-title"
      class="relative max-h-[calc(100vh-2rem)] w-full max-w-2xl overflow-y-auto rounded-2xl border border-slate-200 bg-white p-5 shadow-2xl sm:p-7"
    >
      <!-- Header -->
      <div class="mb-5 flex items-start justify-between gap-4 border-b border-slate-100 pb-4">
        <div>
          <div class="flex items-center gap-2">
            <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
            </span>
            <h2 id="product-import-title" class="text-xl font-bold text-slate-900">
              Impor Produk dari CSV
            </h2>
          </div>
          <p class="mt-1 text-sm text-slate-500">
            Unggah file CSV untuk menambahkan beberapa produk sekaligus ke toko Anda.
          </p>
        </div>

        <button
          type="button"
          @click="emit('close')"
          class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-300"
          aria-label="Tutup modal impor"
        >
          <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path
              fill-rule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>

      <!-- Quick Template Download Banner -->
      <div class="mb-5 flex flex-col gap-3 rounded-xl border border-indigo-100 bg-indigo-50/70 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-start gap-3">
          <svg class="mt-0.5 h-5 w-5 shrink-0 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="text-xs text-indigo-950 sm:text-sm">
            <span class="font-semibold">Format kolom yang dibutuhkan:</span>
            SKU, Nama Produk, Kategori, Harga, Stok, Status, Deskripsi.
          </div>
        </div>
        <button
          type="button"
          @click="handleDownloadTemplate"
          :disabled="downloadingTemplate"
          class="inline-flex shrink-0 items-center justify-center gap-1.5 rounded-lg border border-indigo-300 bg-white px-3 py-1.5 text-xs font-semibold text-indigo-700 shadow-xs transition hover:bg-indigo-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-60"
        >
          <svg v-if="!downloadingTemplate" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <svg v-else class="h-3.5 w-3.5 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ downloadingTemplate ? 'Mengunduh...' : 'Unduh Template' }}
        </button>
      </div>

      <!-- Drag & Drop Upload Zone -->
      <div
        v-if="!selectedFile"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
        @click="triggerBrowse"
        :class="[
          'group relative flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center transition-all sm:p-10',
          isDragging
            ? 'border-indigo-500 bg-indigo-50/50 scale-[1.01]'
            : 'border-slate-300 bg-slate-50/50 hover:border-indigo-400 hover:bg-slate-50'
        ]"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".csv"
          class="hidden"
          @change="handleFileSelect"
        />

        <div class="mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-100/80 text-indigo-600 transition group-hover:scale-110">
          <svg class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>

        <p class="text-sm font-semibold text-slate-800 sm:text-base">
          Tarik & lepaskan file CSV di sini, atau <span class="text-indigo-600 underline">pilih file</span>
        </p>
        <p class="mt-1 text-xs text-slate-500">
          Format .csv hingga ukuran 5 MB
        </p>
      </div>

      <!-- Selected File Card -->
      <div
        v-else
        class="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-4"
      >
        <div class="flex items-center gap-3 min-w-0">
          <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="truncate text-sm font-semibold text-slate-900">
              {{ selectedFile.name }}
            </p>
            <p class="text-xs text-slate-500">
              {{ formatFileSize(selectedFile.size) }}
            </p>
          </div>
        </div>

        <button
          type="button"
          @click="removeFile"
          :disabled="uploading"
          class="rounded-lg p-1.5 text-slate-400 transition hover:bg-slate-200 hover:text-slate-700 disabled:opacity-50"
          title="Ganti file"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>

      <!-- General Error Alert -->
      <div
        v-if="generalError"
        class="mt-4 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-3.5 text-sm text-red-800"
        role="alert"
      >
        <svg class="mt-0.5 h-5 w-5 shrink-0 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="flex-1">
          <p class="font-semibold">{{ generalError }}</p>
        </div>
      </div>

      <!-- Detailed Validation Errors Table -->
      <div
        v-if="validationErrors.length > 0"
        class="mt-4 overflow-hidden rounded-xl border border-red-200 bg-white"
      >
        <div class="bg-red-50/70 px-4 py-2.5 text-xs font-semibold uppercase tracking-wider text-red-900 border-b border-red-200">
          Rincian Kesalahan Validasi ({{ validationErrors.length }} baris bermasalah)
        </div>
        <div class="max-h-56 overflow-y-auto">
          <table class="min-w-full divide-y divide-red-100 text-left text-xs">
            <thead class="bg-slate-50 text-slate-600">
              <tr>
                <th class="px-3 py-2 font-medium">Baris</th>
                <th class="px-3 py-2 font-medium">SKU</th>
                <th class="px-3 py-2 font-medium">Kolom</th>
                <th class="px-3 py-2 font-medium">Pesan Error</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-red-100 text-slate-800">
              <tr
                v-for="(err, index) in validationErrors"
                :key="index"
                class="hover:bg-red-50/30"
              >
                <td class="px-3 py-2 font-mono font-semibold text-red-700">
                  {{ err.row || '-' }}
                </td>
                <td class="px-3 py-2 font-mono text-slate-700">
                  {{ err.sku || '-' }}
                </td>
                <td class="px-3 py-2 uppercase font-medium text-slate-600">
                  {{ err.field || '-' }}
                </td>
                <td class="px-3 py-2 text-red-600">
                  {{ err.message }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Footer Action Buttons -->
      <div class="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-end border-t border-slate-100 pt-5">
        <button
          type="button"
          @click="emit('close')"
          :disabled="uploading"
          class="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-xs transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-300 disabled:opacity-60"
        >
          Batal
        </button>

        <button
          type="button"
          @click="handleImport"
          :disabled="!selectedFile || uploading"
          class="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <svg
            v-if="uploading"
            class="h-4 w-4 animate-spin text-white"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ uploading ? 'Memproses Impor...' : 'Unggah & Impor' }}
        </button>
      </div>
    </section>
  </div>
</template>
