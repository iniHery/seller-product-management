<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <div class="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">

      <!-- ========================================
           PAGE HEADER
      ========================================= -->
      <div
        class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Products
          </h1>

          <p class="mt-1 text-sm text-slate-500 sm:text-base">
            Manage your products
          </p>
        </div>

        <button
          type="button"
          @click="openCreateProduct"
          class="inline-flex w-full items-center justify-center rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition duration-200 hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 sm:w-auto sm:px-5"
        >
          <span class="mr-2 text-base leading-none">+</span>
          Add Product
        </button>
      </div>

      <!-- ========================================
           SUCCESS MESSAGE
      ========================================= -->
      <div
        v-if="successMessage"
        class="mb-6 flex items-center rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700"
      >
        {{ successMessage }}
      </div>

      <!-- ========================================
           ERROR MESSAGE
      ========================================= -->
      <div
        v-if="errorMessage"
        class="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700"
      >
        {{ errorMessage }}
      </div>

      <!-- ========================================
           ADD PRODUCT FORM
      ========================================= -->
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

      <!-- ========================================
           PRODUCT DETAIL MODAL
      ========================================= -->
      <div
        v-if="showDetailModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <div
          class="fixed inset-0 bg-slate-900/50 backdrop-blur-[1px]"
          @click="closeProductDetail"
        ></div>

        <section
          role="dialog"
          aria-modal="true"
          aria-labelledby="product-detail-title"
          class="relative max-h-[calc(100vh-2rem)] w-full max-w-2xl overflow-y-auto rounded-2xl border border-slate-200 bg-white p-5 shadow-xl sm:p-6"
        >
          <div class="mb-5 flex items-start justify-between gap-4">
            <div>
              <h2
                id="product-detail-title"
                class="text-xl font-bold text-slate-900"
              >
                Product Details
              </h2>
              <p class="mt-1 text-sm text-slate-500">
                Product information
              </p>
            </div>
            <button
              type="button"
              @click="closeProductDetail"
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
            v-if="detailLoading"
            class="flex min-h-48 flex-col items-center justify-center gap-3"
            role="status"
            aria-live="polite"
          >
            <div
              class="h-9 w-9 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900"
              aria-hidden="true"
            ></div>
            <p class="text-sm font-medium text-slate-500">
              Loading product details...
            </p>
          </div>

          <div
            v-else-if="detailError"
            role="alert"
            class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-700"
          >
            {{ detailError }}
          </div>

          <dl
            v-else-if="detailProduct"
            class="grid grid-cols-1 gap-4 sm:grid-cols-2"
          >
            <div class="min-w-0 rounded-xl bg-slate-50 p-4">
              <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Name
              </dt>
              <dd class="mt-1 wrap-break-word text-sm font-semibold text-slate-900">
                {{ detailProduct.name || '-' }}
              </dd>
            </div>
            <div class="min-w-0 rounded-xl bg-slate-50 p-4">
              <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
                SKU
              </dt>
              <dd class="mt-1 wrap-break-word text-sm font-medium text-slate-900">
                {{ detailProduct.sku || '-' }}
              </dd>
            </div>
            <div class="min-w-0 rounded-xl bg-slate-50 p-4">
              <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Category
              </dt>
              <dd class="mt-1 wrap-break-word text-sm text-slate-900">
                {{ detailProduct.category?.name || '-' }}
              </dd>
            </div>
            <div class="min-w-0 rounded-xl bg-slate-50 p-4">
              <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Price
              </dt>
              <dd class="mt-1 text-sm font-semibold text-slate-900">
                {{ formatPrice(detailProduct.price) }}
              </dd>
            </div>
            <div class="min-w-0 rounded-xl bg-slate-50 p-4">
              <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Stock
              </dt>
              <dd class="mt-1 text-sm text-slate-900">
                {{ detailProduct.stock ?? '-' }}
              </dd>
            </div>
            <div class="min-w-0 rounded-xl bg-slate-50 p-4">
              <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Status
              </dt>
              <dd class="mt-1">
                <span
                  class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold"
                  :class="detailProduct.status === 'active'
                    ? 'bg-emerald-100 text-emerald-700'
                    : 'bg-slate-200 text-slate-700'"
                >
                  {{ detailProduct.status || '-' }}
                </span>
              </dd>
            </div>
            <div class="rounded-xl bg-slate-50 p-4 sm:col-span-2">
              <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Description
              </dt>
              <dd class="mt-1 whitespace-pre-wrap wrap-break-word text-sm leading-6 text-slate-700">
                {{ detailProduct.description || '-' }}
              </dd>
            </div>
            <div class="min-w-0 rounded-xl bg-slate-50 p-4">
              <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Created At
              </dt>
              <dd class="mt-1 wrap-break-word text-sm text-slate-700">
                {{ formatDate(detailProduct.created_at) }}
              </dd>
            </div>
            <div class="min-w-0 rounded-xl bg-slate-50 p-4">
              <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Updated At
              </dt>
              <dd class="mt-1 wrap-break-word text-sm text-slate-700">
                {{ formatDate(detailProduct.updated_at) }}
              </dd>
            </div>
          </dl>

          <div class="mt-6 flex justify-end border-t border-slate-100 pt-4">
            <button
              type="button"
              @click="closeProductDetail"
              class="inline-flex w-full justify-center rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-300 sm:w-auto"
            >
              Close
            </button>
          </div>
        </section>
      </div>

      <!-- ========================================
           DELETE CONFIRMATION MODAL
      ========================================= -->
      <div
        v-if="showDeleteModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <!-- Backdrop -->
        <div
          class="fixed inset-0 bg-slate-900/50 backdrop-blur-[1px] transition-opacity"
          @click="!deleting && cancelDelete()"
        ></div>

        <!-- Modal Panel -->
        <div
          class="relative max-h-[calc(100vh-2rem)] w-full max-w-md transform overflow-y-auto rounded-2xl bg-white p-5 text-left shadow-xl transition-all sm:p-6"
        >
          <div class="mb-5">
            <h3 class="text-lg font-bold text-slate-900">
              Delete Product?
            </h3>
            <p class="mt-2 text-sm leading-6 text-slate-500">
              Are you sure you want to delete <span class="font-semibold text-slate-900">{{ productToDelete?.name }}</span>? This action cannot be undone.
            </p>
          </div>

          <div class="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <button
              type="button"
              @click="cancelDelete"
              :disabled="deleting"
              class="inline-flex w-full justify-center rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:ring-offset-2 sm:w-auto disabled:cursor-not-allowed disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="button"
              @click="handleDelete"
              :disabled="deleting"
              class="inline-flex w-full justify-center rounded-xl border border-transparent bg-red-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 sm:w-auto disabled:cursor-not-allowed disabled:opacity-50"
            >
              {{ deleting ? 'Deleting...' : 'Delete Product' }}
            </button>
          </div>
        </div>
      </div>

      <!-- ========================================
           SEARCH & FILTER
      ========================================= -->
      <div
        class="mb-6 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5"
      >
        <!-- Section Header -->
        <div class="mb-5">
          <h2 class="text-lg font-semibold text-slate-900">
            Search & Filter
          </h2>

          <p class="mt-1 text-sm text-slate-500">
            Search products by name or SKU and filter by category or status.
          </p>
        </div>

        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <!-- Search -->
          <div class="md:col-span-2 xl:col-span-2">
            <label
              for="search"
              class="mb-2 block text-sm font-semibold text-slate-700"
            >
              Search
            </label>

            <input
              id="search"
              v-model="searchInput"
              type="text"
              placeholder="Search by name or SKU..."
              class="block w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 shadow-sm outline-none transition duration-200 hover:border-slate-400 focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
              @keyup.enter="handleSearch"
            />
          </div>

          <!-- Category -->
          <div>
            <label
              for="category"
              class="mb-2 block text-sm font-semibold text-slate-700"
            >
              Category
            </label>

            <div class="relative">
              <select
                id="category"
                v-model="categoryFilter"
                @change="handleSearch"
                class="block w-full appearance-none rounded-xl border border-slate-300 bg-white px-4 py-3 pr-10 text-sm font-medium text-slate-900 shadow-sm outline-none transition duration-200 hover:border-slate-400 focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
              >
                <option
                  value=""
                  class="bg-white text-slate-900"
                >
                  All Categories
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

          <!-- Status -->
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
                class="block w-full appearance-none rounded-xl border border-slate-300 bg-white px-4 py-3 pr-10 text-sm font-medium text-slate-900 shadow-sm outline-none transition duration-200 hover:border-slate-400 focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
              >
                <option
                  value=""
                  class="bg-white text-slate-900"
                >
                  All Status
                </option>

                <option
                  value="active"
                  class="bg-white text-slate-900"
                >
                  Active
                </option>

                <option
                  value="inactive"
                  class="bg-white text-slate-900"
                >
                  Inactive
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

        <!-- Filter Buttons -->
        <div class="mt-5 flex flex-wrap gap-3">
          <button
            type="button"
            @click="handleSearch"
            :disabled="loading"
            class="inline-flex items-center justify-center rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Search
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

      <!-- ========================================
           PRODUCT TABLE
      ========================================= -->
      <div
        class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
      >
        <!-- Loading State -->
        <div
          v-if="loading"
          class="flex min-h-75 items-center justify-center px-4"
        >
          <div class="flex flex-col items-center">
            <div
              class="mb-4 h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900"
            ></div>

            <p class="text-sm font-medium text-slate-500">
              Loading products...
            </p>
          </div>
        </div>

        <!-- Empty State -->
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
              No products found
            </h2>

            <p class="mt-2 text-sm leading-6 text-slate-500">
              There are no products matching your current search or filter.
            </p>

            <button
              type="button"
              @click="openCreateProduct"
              class="mt-5 inline-flex items-center justify-center rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
            >
              + Add Product
            </button>
          </div>
        </div>

        <!-- Table -->
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200">
            <thead class="bg-slate-50">
              <tr>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  Product
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  SKU
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  Category
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  Price
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  Stock
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  Status
                </th>
                <th scope="col" class="px-4 py-3 text-right text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 sm:px-5 lg:px-6">
                  Actions
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
                      class="text-left text-sm font-semibold text-slate-900 underline-offset-4 transition hover:text-slate-600 hover:underline focus:outline-none focus:ring-2 focus:ring-slate-300 sm:text-base"
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
                  {{ formatPrice(product.price) }}
                </td>

                <td class="whitespace-nowrap px-4 py-4 text-sm text-slate-700 sm:px-5 lg:px-6">
                  {{ product.stock }}
                </td>

                <td class="whitespace-nowrap px-4 py-4 sm:px-5 lg:px-6">
                  <span
                    v-if="product.status === 'active'"
                    class="inline-flex rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700"
                  >
                    Active
                  </span>

                  <span
                    v-else
                    class="inline-flex rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600"
                  >
                    Inactive
                  </span>
                </td>

                <td class="px-4 py-4 text-right sm:px-5 lg:px-6">
                  <div class="flex flex-wrap items-center justify-end gap-2">
                    <button
                      type="button"
                      @click="openProductDetail(product)"
                      class="rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50 hover:text-slate-900 sm:px-3 sm:text-sm"
                    >
                      View
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
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          v-if="!loading && pagination.count > 0"
          class="flex flex-col gap-3 border-t border-slate-200 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-5 lg:px-6"
        >
          <p class="text-sm text-slate-500">
            Total products:
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
              Previous
            </button>

            <span class="rounded-xl bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700">
              Page {{ currentPage }}
            </span>

            <button
              type="button"
              @click="goToPage(currentPage + 1)"
              :disabled="!pagination.next || loading"
              class="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';

import ProductForm from '@/components/ProductForm.vue';

import { getProducts, getProduct, deleteProduct } from '@/api/productService';
import { getCategories } from '@/api/categoryService';

/*
|--------------------------------------------------------------------------
| State
|--------------------------------------------------------------------------
*/

const products = ref([]);
const categories = ref([]);

const loading = ref(false);
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

/*
|--------------------------------------------------------------------------
| Product
|--------------------------------------------------------------------------
*/

async function fetchProducts(page = 1) {
  const requestId = ++productsRequestId;
  loading.value = true;
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

    products.value = responseData?.results || [];

    pagination.value = {
      count: responseData?.count || 0,
      next: responseData?.next || null,
      previous: responseData?.previous || null,
    };

    currentPage.value = page;
  } catch (error) {
    console.error('Failed to fetch products:', error);
    if (requestId !== productsRequestId) return;

    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail;
    } else {
      errorMessage.value = 'Failed to load products.';
    }

    products.value = [];

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

/*
|--------------------------------------------------------------------------
| Categories
|--------------------------------------------------------------------------
*/

async function fetchCategories() {
  try {
    const response = await getCategories();

    categories.value = response.data?.data || [];
  } catch (error) {
    console.error('Failed to fetch categories:', error);

    categories.value = [];
    errorMessage.value = error.response?.data?.detail || 'Failed to load categories.';
  }
}

/*
|--------------------------------------------------------------------------
| Search & Filter
|--------------------------------------------------------------------------
*/

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

/*
|--------------------------------------------------------------------------
| Pagination
|--------------------------------------------------------------------------
*/

function goToPage(page) {
  if (page < 1) {
    return;
  }

  fetchProducts(page);
}

/*
|--------------------------------------------------------------------------
| Product Detail
|--------------------------------------------------------------------------
*/

async function openProductDetail(product) {
  const requestId = ++detailRequestId;
  showDetailModal.value = true;
  detailProduct.value = null;
  detailError.value = '';
  detailLoading.value = true;

  try {
    const response = await getProduct(product.id);
    if (response.data?.success === false) {
      throw new Error(response.data.detail || 'Failed to load product details.');
    }
    if (requestId === detailRequestId) {
      detailProduct.value = response.data?.data || response.data;
    }
  } catch (error) {
    console.error('Failed to fetch product details:', error);
    if (requestId === detailRequestId) {
      detailError.value = error.response?.data?.detail || error.message || 'Failed to load product details.';
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

/*
|--------------------------------------------------------------------------
| Add / Edit Product
|--------------------------------------------------------------------------
*/

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
  successMessage.value = 'Product created successfully.';

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

function closeProductEditor() {
  showProductForm.value = false;
  editingProduct.value = null;
}

async function handleProductUpdated() {
  showProductForm.value = false;
  editingProduct.value = null;

  successMessage.value = 'Product updated successfully.';

  await fetchProducts(currentPage.value);

  window.setTimeout(() => {
    successMessage.value = '';
  }, 3000);
}

/*
|--------------------------------------------------------------------------
| Delete Product
|--------------------------------------------------------------------------
*/

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
    successMessage.value = 'Product deleted successfully.';

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
      errorMessage.value = 'Failed to delete product.';
    }

    showDeleteModal.value = false;
  } finally {
    deleting.value = false;
    productToDelete.value = null;
  }
}

/*
|--------------------------------------------------------------------------
| Helpers
|--------------------------------------------------------------------------
*/

function formatPrice(price) {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(Number(price || 0));
}

function formatDate(dateString) {
  if (!dateString) return '-';

  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) return '-';

  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/*
|--------------------------------------------------------------------------
| Lifecycle
|--------------------------------------------------------------------------
*/

onMounted(async () => {
  await Promise.all([
    fetchProducts(1),
    fetchCategories(),
  ]);
});
</script>