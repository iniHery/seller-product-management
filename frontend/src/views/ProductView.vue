<script setup>
import { onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import ProductDeleteConfirmation from '@/components/ProductDeleteConfirmation.vue';
import ProductDetailModal from '@/components/ProductDetailModal.vue';
import ProductImportModal from '@/components/ProductImportModal.vue';
import ProductForm from '@/components/ProductForm.vue';
import BaseTable from '@/components/BaseTable.vue';

import CustomSelect from '@/components/CustomSelect.vue';
import {
  getProducts,
  getProduct,
  deleteProduct,
  patchProduct,
  exportProductsCSV,
  toggleProductFavorite,
} from '@/api/productService';
import { getCategories } from '@/api/categoryService';
import { formatCurrency } from '@/utils/formatters';
import { triggerFileDownload, generateCSVFilename } from '@/utils/download';

// State

const products = ref([]);
const categories = ref([]);
const categoryOptions = ref([
  { label: 'Semua Kategori', value: '' },
]);
const statusOptions = ref([
  { label: 'Semua Status', value: '' },
  { label: 'Aktif', value: 'active' },
  { label: 'Tidak Aktif', value: 'inactive' },
]);
const stockOptions = ref([
  { label: 'Semua Stok', value: '' },
  { label: 'Tersedia (>5)', value: 'in_stock' },
  { label: 'Menipis (1–5)', value: 'low' },
  { label: 'Habis (0)', value: 'out' },
  { label: 'Kritis (≤5)', value: 'critical' },
]);
const orderingOptions = ref([
  { label: 'Terbaru Dibuat', value: 'created_desc' },
  { label: 'Terlama Dibuat', value: 'created_asc' },
  { label: 'Nama (A – Z)', value: 'name_asc' },
  { label: 'Nama (Z – A)', value: 'name_desc' },
  { label: 'Harga: Termurah', value: 'price_asc' },
  { label: 'Harga: Termahal', value: 'price_desc' },
  { label: 'Stok: Paling Sedikit', value: 'stock_asc' },
  { label: 'Stok: Paling Banyak', value: 'stock_desc' },
  { label: 'Terakhir Diperbarui', value: 'updated_desc' },
  { label: 'Terlama Diperbarui', value: 'updated_asc' },
]);

const loading = ref(false);
const productsLoadFailed = ref(false);
let productsRequestId = 0;

const errorMessage = ref('');
const successMessage = ref('');

const showProductForm = ref(false);
const editingProduct = ref(null);

const showDetailModal = ref(false);
const detailProduct = ref(null);
const detailLoading = ref(false);
const detailError = ref('');
let detailRequestId = 0;

const showDeleteModal = ref(false);
const productToDelete = ref(null);
const deleting = ref(false);
const statusUpdating = ref(null);

const showImportModal = ref(false);
const exporting = ref(false);

const searchInput = ref('');
const search = ref('');

const categoryFilter = ref('');
const statusFilter = ref('');
const stockFilter = ref('');
const favoriteOnly = ref(false);
const ordering = ref('created_desc');
const favoriteUpdating = ref(null);

const route = useRoute();

const currentPage = ref(1);

const pagination = ref({
  count: 0,
  next: null,
  previous: null,
});

// Product

async function fetchProducts(page = 1) {
  const requestId = ++productsRequestId;
  loading.value = true;
  productsLoadFailed.value = false;
  errorMessage.value = '';

  try {
    const params = {
      page,
    };

    if (search.value.trim()) {
      params.search = search.value.trim();
    }

    if (categoryFilter.value) {
      params.category = categoryFilter.value;
    }

    if (statusFilter.value) {
      params.status = statusFilter.value;
    }

    if (stockFilter.value) {
      params.stock_status = stockFilter.value;
    }

    if (favoriteOnly.value) {
      params.is_favorite = 'true';
    }

    if (ordering.value) {
      params.ordering = ordering.value;
    }

    const response = await getProducts(params);
    if (requestId !== productsRequestId) return;

    const responseData = response.data?.data;
    if (
      response.data?.success !== true ||
      !responseData ||
      !Array.isArray(responseData.results) ||
      !Number.isInteger(responseData.count) ||
      responseData.count < 0 ||
      (typeof responseData.next !== 'string' && responseData.next !== null) ||
      (typeof responseData.previous !== 'string' && responseData.previous !== null)
    ) {
      throw new Error('Respons daftar produk tidak valid.');
    }

    products.value = responseData.results;

    pagination.value = {
      count: responseData.count,
      next: responseData.next,
      previous: responseData.previous,
    };

    currentPage.value = page;
  } catch (error) {
    console.error('Failed to fetch products:', error);
    if (requestId !== productsRequestId) return;

    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail;
    } else {
      errorMessage.value = 'Gagal memuat produk.';
    }

    products.value = [];
    productsLoadFailed.value = true;

    pagination.value = {
      count: 0,
      next: null,
      previous: null,
    };
  } finally {
    if (requestId === productsRequestId) {
      loading.value = false;
    }
  }
}

// Categories

async function fetchCategories() {
  try {
    const response = await getCategories();
    if (response.data?.success !== true || !Array.isArray(response.data.data)) {
      throw new Error('Respons daftar kategori tidak valid.');
    }

    categories.value = response.data.data;
    // Populate options for CustomSelect
    categoryOptions.value = [
      { label: 'Semua Kategori', value: '' },
      ...categories.value.map((cat) => ({ label: cat.name, value: cat.id })),
    ];
  } catch (error) {
    console.error('Failed to fetch categories:', error);

    if (!error.response) {
      errorMessage.value = error.message || 'Gagal memuat kategori.';
    } else {
      errorMessage.value = error.response.data?.detail || 'Gagal memuat kategori.';
    }
  }
}



function handleSearch() {
  search.value = searchInput.value.trim();

  fetchProducts(1);
}

function resetFilters() {
  searchInput.value = '';
  search.value = '';

  categoryFilter.value = '';
  statusFilter.value = '';
  stockFilter.value = '';
  favoriteOnly.value = false;
  ordering.value = 'created_desc';

  fetchProducts(1);
}

function toggleFavoriteFilter() {
  favoriteOnly.value = !favoriteOnly.value;
  fetchProducts(1);
}

function handleOrderingChange() {
  fetchProducts(1);
}

function handleHeaderSort(field) {
  if (field === 'name') {
    ordering.value = ordering.value === 'name_asc' ? 'name_desc' : 'name_asc';
  } else if (field === 'price') {
    ordering.value = ordering.value === 'price_asc' ? 'price_desc' : 'price_asc';
  } else if (field === 'stock') {
    ordering.value = ordering.value === 'stock_asc' ? 'stock_desc' : 'stock_asc';
  }
  fetchProducts(1);
}

function handleFilterChange() {
  search.value = searchInput.value.trim();
  fetchProducts(1);
}

async function handleToggleFavorite(product) {
  if (favoriteUpdating.value === product.id) return;

  favoriteUpdating.value = product.id;
  const originalState = product.is_favorite;
  // Optimistic UI update
  product.is_favorite = !originalState;

  try {
    const response = await toggleProductFavorite(product.id);
    if (response.data?.success && response.data?.data) {
      product.is_favorite = response.data.data.is_favorite;
      successMessage.value = response.data.message || (product.is_favorite ? 'Produk berhasil ditandai sebagai favorit.' : 'Produk berhasil dihapus dari favorit.');
      window.setTimeout(() => {
        if (successMessage.value) successMessage.value = '';
      }, 3000);

      // If viewing only favorites and seller unfavorited an item, refresh page
      if (favoriteOnly.value && !product.is_favorite) {
        fetchProducts(currentPage.value);
      }
    } else {
      throw new Error();
    }
  } catch (error) {
    product.is_favorite = originalState;
    console.error('Failed to toggle favorite:', error);
    errorMessage.value = error.response?.data?.detail || 'Gagal mengubah status favorit produk.';
  } finally {
    favoriteUpdating.value = null;
  }
}

// Pagination

function goToPage(page) {
  if (page < 1) {
    return;
  }

  fetchProducts(page);
}

// Product detail

async function openProductDetail(product) {
  const requestId = ++detailRequestId;
  showDetailModal.value = true;
  detailProduct.value = null;
  detailError.value = '';
  detailLoading.value = true;

  try {
    const response = await getProduct(product.id);
    if (response.data?.success === false) {
      throw new Error(response.data.detail || 'Gagal memuat detail produk.');
    }
    if (requestId === detailRequestId) {
      detailProduct.value = response.data?.data || response.data;
    }
  } catch (error) {
    console.error('Failed to fetch product details:', error);
    if (requestId === detailRequestId) {
      detailError.value = error.response?.data?.detail || error.message || 'Gagal memuat detail produk.';
    }
  } finally {
    if (requestId === detailRequestId) {
      detailLoading.value = false;
    }
  }
}

function closeProductDetail() {
  detailRequestId += 1;
  showDetailModal.value = false;
  detailProduct.value = null;
  detailError.value = '';
}

// Add/edit product

function openCreateProduct() {
  errorMessage.value = '';
  successMessage.value = '';
  editingProduct.value = null;
  showProductForm.value = true;
}

function closeProductForm() {
  showProductForm.value = false;
}

async function handleProductCreated() {
  showProductForm.value = false;
  successMessage.value = 'Produk berhasil dibuat.';

  await fetchProducts(1);

  window.setTimeout(() => {
    successMessage.value = '';
  }, 3000);
}

function openEditProduct(product) {
  errorMessage.value = '';
  successMessage.value = '';

  editingProduct.value = product;
  showProductForm.value = true;
}

async function toggleProductStatus(product) {
  if (statusUpdating.value === product.id) return;
  const previousStatus = product.status;
  const nextStatus = previousStatus === 'active' ? 'inactive' : 'active';
  statusUpdating.value = product.id;
  product.status = nextStatus;
  try {
    await patchProduct(product.id, { status: nextStatus });
  } catch (error) {
    product.status = previousStatus;
    errorMessage.value = error.response?.data?.detail || 'Gagal mengubah status produk.';
  } finally {
    statusUpdating.value = null;
  }
}

function closeProductEditor() {
  showProductForm.value = false;
  editingProduct.value = null;
}

async function handleProductUpdated() {
  showProductForm.value = false;
  editingProduct.value = null;

  successMessage.value = 'Produk berhasil diperbarui.';

  await fetchProducts(currentPage.value);

  window.setTimeout(() => {
    successMessage.value = '';
  }, 3000);
}

// Delete product

function confirmDelete(product) {
  productToDelete.value = product;
  showDeleteModal.value = true;
}

function cancelDelete() {
  if (deleting.value) return;
  showDeleteModal.value = false;
  productToDelete.value = null;
}

async function handleDelete() {
  if (!productToDelete.value) return;

  deleting.value = true;
  errorMessage.value = '';

  try {
    await deleteProduct(productToDelete.value.id);

    showDeleteModal.value = false;
    successMessage.value = 'Produk berhasil dihapus.';

    if (products.value.length === 1 && currentPage.value > 1) {
      await fetchProducts(currentPage.value - 1);
    } else {
      await fetchProducts(currentPage.value);
    }

    window.setTimeout(() => {
      successMessage.value = '';
    }, 3000);
  } catch (error) {
    console.error('Failed to delete product:', error);

    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail;
    } else {
      errorMessage.value = 'Gagal menghapus produk.';
    }

    showDeleteModal.value = false;
  } finally {
    deleting.value = false;
    productToDelete.value = null;
  }
}

// CSV Import & Export Actions

function openImportModal() {
  showImportModal.value = true;
}

function closeImportModal() {
  showImportModal.value = false;
}

function handleImportSuccess(message) {
  successMessage.value = message;
  errorMessage.value = '';
  fetchProducts(1);
}

async function handleExportCSV() {
  if (exporting.value) return;
  exporting.value = true;
  errorMessage.value = '';

  try {
    const params = {};
    if (search.value.trim()) params.search = search.value.trim();
    if (categoryFilter.value) params.category = categoryFilter.value;
    if (statusFilter.value) params.status = statusFilter.value;
    if (stockFilter.value) params.stock_status = stockFilter.value;
    if (favoriteOnly.value) params.is_favorite = 'true';
    if (ordering.value) params.ordering = ordering.value;

    const response = await exportProductsCSV(params);
    triggerFileDownload(response.data, generateCSVFilename('produk'));
  } catch (err) {
    console.error('Failed to export products:', err);
    errorMessage.value = 'Gagal mengekspor data produk ke CSV. Silakan coba lagi.';
  } finally {
    exporting.value = false;
  }
}

// Lifecycle

watch(
  () => route.query.stock_status,
  (newStatus) => {
    stockFilter.value = newStatus ? String(newStatus) : '';
    fetchProducts(1);
  }
);

onMounted(async () => {
  if (route.query.stock_status) {
    stockFilter.value = String(route.query.stock_status);
  }

  await Promise.all([
    fetchProducts(1),
    fetchCategories(),
  ]);
});
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <div class="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">

      <!-- Page header -->
      <div
        class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Produk
          </h1>

          <p class="mt-1 text-sm text-slate-500 sm:text-base">
            Kelola produk Anda
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-2.5 sm:gap-3">
          <!-- Tombol Ekspor CSV -->
          <button
            type="button"
            @click="handleExportCSV"
            :disabled="exporting || loading"
            class="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm font-semibold text-slate-700 shadow-xs transition duration-200 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
            title="Ekspor daftar produk saat ini ke file CSV"
          >
            <svg
              v-if="!exporting"
              class="h-4 w-4 text-slate-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            <svg
              v-else
              class="h-4 w-4 animate-spin text-indigo-600"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{{ exporting ? 'Mengekspor...' : 'Ekspor CSV' }}</span>
          </button>

          <!-- Tombol Impor Produk -->
          <button
            type="button"
            @click="openImportModal"
            class="inline-flex items-center justify-center gap-2 rounded-xl border border-indigo-200 bg-indigo-50 px-3.5 py-2.5 text-sm font-semibold text-indigo-700 shadow-xs transition duration-200 hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            title="Impor produk dari file CSV"
          >
            <svg class="h-4 w-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            <span>Impor Produk</span>
          </button>

          <!-- Tombol Tambah Produk -->
          <button
            type="button"
            @click="openCreateProduct"
            class="inline-flex items-center justify-center gap-1.5 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition duration-200 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            <span class="text-base leading-none">+</span>
            <span>Tambah Produk</span>
          </button>
        </div>
      </div>

      <!-- Success message -->
      <div
        v-if="successMessage"
        class="mb-6 flex items-center rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700"
      >
        {{ successMessage }}
      </div>

      <!-- Error message -->
      <div
        v-if="errorMessage"
        class="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700"
      >
        {{ errorMessage }}
      </div>

      <!-- Add/edit product form -->
      <div
        v-if="showProductForm"
        class="mx-auto mb-6 w-full max-w-4xl"
      >
        <ProductForm
          :product="editingProduct"
          @success="
            editingProduct
              ? handleProductUpdated()
              : handleProductCreated()
          "
          @cancel="editingProduct ? closeProductEditor() : closeProductForm()"
        />
      </div>

      <!-- Product detail modal -->
      <ProductDetailModal
        v-if="showDetailModal"
        :product="detailProduct"
        :loading="detailLoading"
        :error="detailError"
        @close="closeProductDetail"
      />

      <!-- Delete confirmation modal -->
      <ProductDeleteConfirmation
        v-if="showDeleteModal"
        :product="productToDelete"
        :deleting="deleting"
        @cancel="cancelDelete"
        @confirm="handleDelete"
      />

      <!-- Product import modal -->
      <ProductImportModal
        v-if="showImportModal"
        @close="closeImportModal"
        @success="handleImportSuccess"
      />

      <!-- Search and filter -->
      <div
        class="mb-6 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5"
      >
        <div class="mb-5">
          <h2 class="text-lg font-semibold text-slate-900">
            Cari & Filter
          </h2>

          <p class="mt-1 text-sm text-slate-500">
            Cari produk berdasarkan nama atau SKU dan filter berdasarkan kategori atau status.
          </p>
        </div>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <div class="sm:col-span-2 lg:col-span-2 xl:col-span-2">
            <label
              for="search"
              class="mb-2 block text-sm font-semibold text-slate-700"
            >
              Cari
            </label>

            <input
              id="search"
              v-model="searchInput"
              type="text"
              placeholder="Cari berdasarkan nama atau SKU..."
              class="block w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 shadow-sm outline-none transition duration-200 hover:border-slate-400 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100"
              @keyup.enter="handleSearch"
            />
          </div>

          <div>
            <label
              for="category"
              class="mb-2 block text-sm font-semibold text-slate-700"
            >
              Kategori
            </label>

            <CustomSelect
              id="category"
              v-model="categoryFilter"
              :options="categoryOptions"
              placeholder="Semua Kategori"
              class="w-full"
              @change="handleFilterChange"
            />
          </div>

          <div>
            <label
              for="status"
              class="mb-2 block text-sm font-semibold text-slate-700"
            >
              Status
            </label>

            <CustomSelect
              id="status"
              v-model="statusFilter"
              :options="statusOptions"
              placeholder="Semua Status"
              class="w-full"
              @change="handleFilterChange"
            />
          </div>

          <div>
            <label
              for="stock"
              class="mb-2 block text-sm font-semibold text-slate-700"
            >
              Stok
            </label>

            <CustomSelect
              id="stock"
              v-model="stockFilter"
              :options="stockOptions"
              placeholder="Semua Stok"
              class="w-full"
              @change="handleFilterChange"
            />
          </div>

          <div>
            <label
              for="ordering"
              class="mb-2 block text-sm font-semibold text-slate-700"
            >
              Urutkan
            </label>

            <CustomSelect
              id="ordering"
              v-model="ordering"
              :options="orderingOptions"
              placeholder="Urutkan"
              class="w-full"
              @change="handleOrderingChange"
            />
          </div>
        </div>

        <div class="mt-5 flex flex-wrap items-center gap-3">
          <div class="flex flex-wrap items-center gap-3">
            <button
              type="button"
              @click="handleSearch"
              :disabled="loading"
              class="inline-flex items-center justify-center rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Cari
            </button>

            <button
              type="button"
              @click="resetFilters"
              :disabled="loading"
              class="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Reset
            </button>
          </div>

          <!-- Filter Hanya Favorit -->
          <button
            type="button"
            @click="toggleFavoriteFilter"
            :disabled="loading"
            :class="favoriteOnly ? 'border-amber-400 bg-amber-50 text-amber-800 ring-2 ring-amber-200' : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'"
            class="inline-flex items-center gap-2 rounded-xl border px-4 py-2.5 text-sm font-semibold shadow-xs transition duration-200 focus:outline-none disabled:opacity-50"
            title="Filter hanya menampilkan produk yang ditandai favorit"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4 transition duration-150"
              :class="favoriteOnly ? 'text-amber-500 fill-amber-400' : 'text-slate-400'"
              viewBox="0 0 24 24"
              stroke="currentColor"
              fill="none"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
            <span>{{ favoriteOnly ? 'Hanya Favorit (Aktif)' : 'Hanya Favorit' }}</span>
          </button>
        </div>
      </div>

      <!-- Product table -->
      <div
        class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
      >
        <div
          v-if="loading"
          class="flex min-h-75 items-center justify-center px-4"
        >
          <div class="flex flex-col items-center">
            <div
              class="mb-4 h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-indigo-600"
            ></div>

            <p class="text-sm font-medium text-slate-500">
              Memuat produk...
            </p>
          </div>
        </div>

        <div
          v-else-if="productsLoadFailed"
          class="flex min-h-75 items-center justify-center px-6 py-12 text-center text-sm text-slate-600"
          role="status"
        >
          Data produk tidak dapat ditampilkan. Periksa koneksi dan coba cari kembali.
        </div>

        <div
          v-else-if="products.length === 0"
          class="flex min-h-75 items-center justify-center px-6 py-12"
        >
          <div class="max-w-md text-center">
            <div
              class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-slate-100"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-7 w-7 text-slate-400"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0H4"
                />
              </svg>
            </div>

            <h2 class="text-lg font-semibold text-slate-900">
              Tidak ada produk ditemukan
            </h2>

            <p class="mt-2 text-sm leading-6 text-slate-500">
              Tidak ada produk yang cocok dengan pencarian atau filter Anda saat ini.
            </p>

            <button
              type="button"
              @click="openCreateProduct"
              class="mt-5 inline-flex items-center justify-center rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700"
            >
              + Tambah Produk
            </button>
          </div>
        </div>

        <BaseTable v-else>
            <thead class="bg-slate-50">
              <tr>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  <button
                    type="button"
                    @click="handleHeaderSort('name')"
                    class="group inline-flex items-center gap-1.5 uppercase tracking-[0.08em] transition hover:text-slate-900 focus:outline-none"
                    title="Klik untuk mengurutkan Nama (A-Z / Z-A)"
                  >
                    <span>Produk</span>
                    <span class="inline-flex flex-col text-slate-300">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-3 w-3 -mb-1 transition-colors"
                        :class="ordering === 'name_asc' ? 'text-indigo-600 font-bold' : 'group-hover:text-slate-500'"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path fill-rule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd" />
                      </svg>
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-3 w-3 transition-colors"
                        :class="ordering === 'name_desc' ? 'text-indigo-600 font-bold' : 'group-hover:text-slate-500'"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                      </svg>
                    </span>
                  </button>
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  SKU
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  Kategori
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  <button
                    type="button"
                    @click="handleHeaderSort('price')"
                    class="group inline-flex items-center gap-1.5 uppercase tracking-[0.08em] transition hover:text-slate-900 focus:outline-none"
                    title="Klik untuk mengurutkan Harga (Termurah / Termahal)"
                  >
                    <span>Harga</span>
                    <span class="inline-flex flex-col text-slate-300">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-3 w-3 -mb-1 transition-colors"
                        :class="ordering === 'price_asc' ? 'text-indigo-600 font-bold' : 'group-hover:text-slate-500'"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path fill-rule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd" />
                      </svg>
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-3 w-3 transition-colors"
                        :class="ordering === 'price_desc' ? 'text-indigo-600 font-bold' : 'group-hover:text-slate-500'"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                      </svg>
                    </span>
                  </button>
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  <button
                    type="button"
                    @click="handleHeaderSort('stock')"
                    class="group inline-flex items-center gap-1.5 uppercase tracking-[0.08em] transition hover:text-slate-900 focus:outline-none"
                    title="Klik untuk mengurutkan Stok (Paling Sedikit / Paling Banyak)"
                  >
                    <span>Stok</span>
                    <span class="inline-flex flex-col text-slate-300">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-3 w-3 -mb-1 transition-colors"
                        :class="ordering === 'stock_asc' ? 'text-indigo-600 font-bold' : 'group-hover:text-slate-500'"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path fill-rule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd" />
                      </svg>
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-3 w-3 transition-colors"
                        :class="ordering === 'stock_desc' ? 'text-indigo-600 font-bold' : 'group-hover:text-slate-500'"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                      </svg>
                    </span>
                  </button>
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  Status
                </th>
                <th scope="col" class="px-4 py-3 text-right text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  Aksi
                </th>
              </tr>
            </thead>

            <tbody class="divide-y divide-slate-200 bg-white">
              <tr v-for="product in products" :key="product.id" class="transition hover:bg-slate-50">
                <td class="px-4 py-4 sm:px-5 lg:px-6">
                  <div class="flex items-start gap-2.5 min-w-55">
                    <button
                      type="button"
                      @click.stop="handleToggleFavorite(product)"
                      :disabled="favoriteUpdating === product.id"
                      :title="product.is_favorite ? 'Hapus dari favorit' : 'Tandai sebagai favorit'"
                      class="inline-flex shrink-0 rounded-lg p-1 pt-0 text-slate-400 transition hover:bg-amber-50 hover:text-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-300 disabled:opacity-50"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-5 w-5 transition duration-150"
                        :class="product.is_favorite ? 'text-amber-400 fill-amber-400' : 'text-slate-300 hover:text-amber-400'"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        fill="none"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                      </svg>
                    </button>

                    <div>
                      <button
                        type="button"
                        @click="openProductDetail(product)"
                        class="text-left text-sm font-semibold text-slate-900 underline-offset-4 transition hover:text-indigo-700 hover:underline focus:outline-none focus:ring-2 focus:ring-indigo-300 sm:text-base"
                      >
                        {{ product.name }}
                      </button>

                      <p
                        v-if="product.description"
                        class="mt-1 max-w-xs truncate text-xs text-slate-500 sm:text-sm"
                      >
                        {{ product.description }}
                      </p>
                    </div>
                  </div>
                </td>

                <td class="whitespace-nowrap px-4 py-4 text-sm font-medium text-slate-700 sm:px-5 lg:px-6">
                  {{ product.sku }}
                </td>

                <td class="whitespace-nowrap px-4 py-4 text-sm text-slate-700 sm:px-5 lg:px-6">
                  {{ product.category?.name || '-' }}
                </td>

                <td class="whitespace-nowrap px-4 py-4 text-sm font-semibold text-slate-800 sm:px-5 lg:px-6">
                  {{ formatCurrency(product.price) }}
                </td>

                <td class="whitespace-nowrap px-4 py-4 text-sm sm:px-5 lg:px-6">
                  <div class="flex items-center gap-2">
                    <span class="font-medium text-slate-800 tabular-nums">{{ product.stock }}</span>
                    <span
                      v-if="product.stock === 0"
                      class="inline-flex items-center rounded-md bg-red-50 px-2 py-0.5 text-xs font-semibold text-red-700 ring-1 ring-inset ring-red-600/10"
                    >
                      Habis
                    </span>
                    <span
                      v-else-if="product.stock <= 5"
                      class="inline-flex items-center rounded-md bg-amber-50 px-2 py-0.5 text-xs font-semibold text-amber-700 ring-1 ring-inset ring-amber-600/20"
                    >
                      Menipis
                    </span>
                  </div>
                </td>

                <td class="whitespace-nowrap px-4 py-4 sm:px-5 lg:px-6">
                  <button type="button" role="switch" :aria-checked="product.status === 'active'"
                    :disabled="statusUpdating === product.id" @click="toggleProductStatus(product)"
                    class="inline-flex items-center gap-2 text-xs font-semibold disabled:opacity-50">
                    <span class="relative h-6 w-11 rounded-full transition"
                      :class="product.status === 'active' ? 'bg-emerald-500' : 'bg-slate-300'">
                      <span class="absolute top-1 h-4 w-4 rounded-full bg-white shadow transition"
                        :class="product.status === 'active' ? 'left-6' : 'left-1'" />
                    </span>
                    {{ product.status === 'active' ? 'Aktif' : 'Tidak Aktif' }}
                  </button>
                </td>

                <td class="px-4 py-4 text-right sm:px-5 lg:px-6">
                  <div class="flex flex-wrap items-center justify-end gap-2">
                    <button
                      type="button"
                      @click="openProductDetail(product)"
                      class="rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50 hover:text-slate-900 sm:px-3 sm:text-sm"
                    >
                      Lihat
                    </button>
                    <button
                      type="button"
                      @click="openEditProduct(product)"
                      class="rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50 hover:text-slate-900 sm:px-3 sm:text-sm"
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      @click="confirmDelete(product)"
                      class="rounded-lg border border-red-200 bg-red-50 px-2.5 py-2 text-xs font-semibold text-red-700 transition hover:bg-red-100 hover:text-red-800 sm:px-3 sm:text-sm"
                    >
                      Hapus
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
        </BaseTable>

        <div
          v-if="!loading && pagination.count > 0"
          class="flex flex-col gap-3 border-t border-slate-200 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-5 lg:px-6"
        >
          <p class="text-sm text-slate-500">
            Total produk:
            <span class="font-semibold text-slate-800">
              {{ pagination.count }}
            </span>
          </p>

          <div class="flex items-center gap-2 self-start sm:self-auto">
            <button
              type="button"
              @click="goToPage(currentPage - 1)"
              :disabled="!pagination.previous || loading"
              class="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Sebelumnya
            </button>

            <span class="rounded-xl bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700">
              Halaman {{ currentPage }}
            </span>

            <button
              type="button"
              @click="goToPage(currentPage + 1)"
              :disabled="!pagination.next || loading"
              class="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Selanjutnya
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
