<script setup>
import { onMounted, ref } from 'vue';

import ProductDeleteConfirmation from '@/components/ProductDeleteConfirmation.vue';
import ProductDetailModal from '@/components/ProductDetailModal.vue';
import ProductForm from '@/components/ProductForm.vue';
import BaseTable from '@/components/BaseTable.vue';

import { getProducts, getProduct, deleteProduct, patchProduct } from '@/api/productService';
import { getCategories } from '@/api/categoryService';
import { formatCurrency } from '@/utils/formatters';

// State

const products = ref([]);
const categories = ref([]);

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

const searchInput = ref('');
const search = ref('');

const categoryFilter = ref('');
const statusFilter = ref('');

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
  } catch (error) {
    console.error('Failed to fetch categories:', error);

    if (!error.response) {
      errorMessage.value = error.message || 'Gagal memuat kategori.';
    } else {
      errorMessage.value = error.response.data?.detail || 'Gagal memuat kategori.';
    }
  }
}

// Search and filter

function handleSearch() {
  search.value = searchInput.value.trim();

  fetchProducts(1);
}

function resetFilters() {
  searchInput.value = '';
  search.value = '';

  categoryFilter.value = '';
  statusFilter.value = '';

  fetchProducts(1);
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

// Lifecycle

onMounted(async () => {
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

        <button
          type="button"
          @click="openCreateProduct"
          class="inline-flex w-full items-center justify-center rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition duration-200 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto sm:px-5"
        >
          <span class="mr-2 text-base leading-none">+</span>
          Tambah Produk
        </button>
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

        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div class="md:col-span-2 xl:col-span-2">
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

            <div class="relative">
              <select
                id="category"
                v-model="categoryFilter"
                @change="handleSearch"
                class="block w-full appearance-none rounded-xl border border-slate-300 bg-white px-4 py-3 pr-10 text-sm font-medium text-slate-900 shadow-sm outline-none transition duration-200 hover:border-slate-400 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100"
              >
                <option
                  value=""
                  class="bg-white text-slate-900"
                >
                  Semua Kategori
                </option>

                <option
                  v-for="category in categories"
                  :key="category.id"
                  :value="category.name"
                  class="bg-white text-slate-900"
                >
                  {{ category.name }}
                </option>
              </select>

              <div
                class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-500"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fill-rule="evenodd"
                    d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25-4.51a.75.75 0 01.02-1.06z"
                    clip-rule="evenodd"
                  />
                </svg>
              </div>
            </div>
          </div>

          <div>
            <label
              for="status"
              class="mb-2 block text-sm font-semibold text-slate-700"
            >
              Status
            </label>

            <div class="relative">
              <select
                id="status"
                v-model="statusFilter"
                @change="handleSearch"
                class="block w-full appearance-none rounded-xl border border-slate-300 bg-white px-4 py-3 pr-10 text-sm font-medium text-slate-900 shadow-sm outline-none transition duration-200 hover:border-slate-400 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100"
              >
                <option
                  value=""
                  class="bg-white text-slate-900"
                >
                  Semua Status
                </option>

                <option
                  value="active"
                  class="bg-white text-slate-900"
                >
                  Aktif
                </option>

                <option
                  value="inactive"
                  class="bg-white text-slate-900"
                >
                  Tidak Aktif
                </option>
              </select>

              <div
                class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-500"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fill-rule="evenodd"
                    d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25-4.51a.75.75 0 01-.02-1.06z"
                    clip-rule="evenodd"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-5 flex flex-wrap gap-3">
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
                  Produk
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  SKU
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  Kategori
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  Harga
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  Stok
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
                  <div class="min-w-55">
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

                <td class="whitespace-nowrap px-4 py-4 text-sm text-slate-700 sm:px-5 lg:px-6">
                  {{ product.stock }}
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
