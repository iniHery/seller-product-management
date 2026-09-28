// src/views/ProductView.vue
<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="mx-auto max-w-7xl">

      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">
          Products
        </h1>

        <p class="mt-1 text-sm text-gray-500">
          Manage your seller products
        </p>
      </div>

      <!-- Loading -->
      <div
        v-if="loading"
        class="rounded-lg bg-white p-6 text-center shadow-sm"
      >
        <p class="text-gray-500">Loading products...</p>
      </div>

      <!-- Error -->
      <div
        v-else-if="error"
        class="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700"
      >
        {{ error }}
      </div>

      <!-- Empty -->
      <div
        v-else-if="products.length === 0"
        class="rounded-lg bg-white p-10 text-center shadow-sm"
      >
        <h2 class="text-lg font-semibold text-gray-800">
          No Products
        </h2>

        <p class="mt-2 text-sm text-gray-500">
          You don't have any products yet.
        </p>
      </div>

      <!-- Table -->
      <div
        v-else
        class="overflow-hidden rounded-lg bg-white shadow-sm"
      >
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">

            <thead class="bg-gray-100">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-600">
                  Name
                </th>

                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-600">
                  SKU
                </th>

                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-600">
                  Category
                </th>

                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-600">
                  Price
                </th>

                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-600">
                  Stock
                </th>

                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-600">
                  Status
                </th>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-200">
              <tr
                v-for="product in products"
                :key="product.id"
                class="hover:bg-gray-50"
              >
                <td class="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900">
                  {{ product.name }}
                </td>

                <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-600">
                  {{ product.sku }}
                </td>

                <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-600">
                  {{ product.category?.name || '-' }}
                </td>

                <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-600">
                  Rp {{ Number(product.price).toLocaleString('id-ID') }}
                </td>

                <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-600">
                  {{ product.stock }}
                </td>

                <td class="whitespace-nowrap px-6 py-4">
                  <span
                    class="inline-flex rounded-full px-2.5 py-1 text-xs font-medium"
                    :class="
                      product.status === 'active'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-600'
                    "
                  >
                    {{ product.status }}
                  </span>
                </td>
              </tr>
            </tbody>

          </table>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { getProducts } from '@/api/productService';

const authStore = useAuthStore();
// Optional: if you want to guard this view, you could redirect when not authenticated.
// For now we just keep the store reference.

const products = ref([]);
const loading = ref(false);
const errorMessage = ref('');

async function fetchProducts() {
  loading.value = true;
  errorMessage.value = '';
  try {
    const response = await getProducts();
    // Expected: { success:true, data:{ results:[...] } }
    if (response.data && response.data.success) {
      products.value = response.data.data.results || [];
    } else {
      errorMessage.value = 'Failed to load products.';
    }
  } catch (e) {
    errorMessage.value = 'Error loading products.';
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchProducts();
});
</script>

<style scoped>
/* Tailwind provides most styling – keep this block for future tweaks */
</style>
