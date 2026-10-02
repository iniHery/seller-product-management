<template>
  <div
    class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"
  >
    <div class="mb-6 border-b border-slate-200 pb-4">
      <h2 class="text-xl font-bold text-slate-900">
        {{ isEditMode ? 'Edit Produk' : 'Tambah Produk' }}
      </h2>

      <p class="mt-1 text-sm text-slate-500">
        {{
          isEditMode
            ? 'Perbarui informasi produk Anda.'
            : 'Buat produk baru untuk akun penjual Anda.'
        }}
      </p>
    </div>

    <div
      v-if="errorMessage"
      class="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700"
    >
      {{ errorMessage }}
    </div>

    <form
      class="space-y-5"
      @submit.prevent="handleSubmit"
    >
      <div>
        <label
          for="product-name"
          class="mb-2 block text-sm font-semibold text-slate-700"
        >
          Nama Produk
        </label>

        <input
          id="product-name"
          v-model="form.name"
          type="text"
          placeholder="Masukkan nama produk"
          class="block w-full rounded-xl border bg-white px-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 shadow-sm outline-none transition focus:ring-2"
          :class="
            fieldErrors.name
              ? 'border-red-400 focus:border-red-400 focus:ring-red-100'
              : 'border-slate-300 hover:border-slate-400 focus:border-slate-900 focus:ring-slate-200'
          "
        />

        <p
          v-if="fieldErrors.name"
          class="mt-1 text-xs font-medium text-red-600"
        >
          {{ fieldErrors.name }}
        </p>
      </div>

      <div>
        <label
          for="product-sku"
          class="mb-2 block text-sm font-semibold text-slate-700"
        >
          SKU
        </label>

        <input
          id="product-sku"
          v-model="form.sku"
          type="text"
          placeholder="Masukkan SKU produk"
          class="block w-full rounded-xl border bg-white px-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 shadow-sm outline-none transition focus:ring-2"
          :class="
            fieldErrors.sku
              ? 'border-red-400 focus:border-red-400 focus:ring-red-100'
              : 'border-slate-300 hover:border-slate-400 focus:border-slate-900 focus:ring-slate-200'
          "
        />

        <p
          v-if="fieldErrors.sku"
          class="mt-1 text-xs font-medium text-red-600"
        >
          {{ fieldErrors.sku }}
        </p>
      </div>

      <div>
        <label
          for="product-category"
          class="mb-2 block text-sm font-semibold text-slate-700"
        >
          Kategori
        </label>

        <div class="relative">
          <select
            id="product-category"
            v-model="form.category_id"
            :disabled="categoriesLoading"
            class="block w-full appearance-none rounded-xl border bg-white px-4 py-3 pr-10 text-sm font-medium text-slate-900 shadow-sm outline-none transition focus:ring-2 disabled:cursor-not-allowed disabled:bg-slate-100"
            :class="
              fieldErrors.category_id
                ? 'border-red-400 focus:border-red-400 focus:ring-red-100'
                : 'border-slate-300 hover:border-slate-400 focus:border-slate-900 focus:ring-slate-200'
            "
          >
            <option value="">
              {{
                categoriesLoading
                  ? 'Memuat kategori...'
                  : 'Pilih kategori'
              }}
            </option>

            <option
              v-for="category in categories"
              :key="category.id"
              :value="category.id"
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
            >
              <path
                fill-rule="evenodd"
                d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25-4.51a.75.75 0 01-1.08 1.04l-4.25-4.51a.75.75 0 01.02-1.06z"
                clip-rule="evenodd"
              />
            </svg>
          </div>
        </div>

        <p
          v-if="fieldErrors.category_id"
          class="mt-1 text-xs font-medium text-red-600"
        >
          {{ fieldErrors.category_id }}
        </p>
      </div>

      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <div>
          <label
            for="product-price"
            class="mb-2 block text-sm font-semibold text-slate-700"
          >
            Harga
          </label>

          <input
            id="product-price"
            v-model.number="form.price"
            type="number"
            min="0"
            step="0.01"
            placeholder="0"
            class="block w-full rounded-xl border bg-white px-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 shadow-sm outline-none transition focus:ring-2"
            :class="
              fieldErrors.price
                ? 'border-red-400 focus:border-red-400 focus:ring-red-100'
                : 'border-slate-300 hover:border-slate-400 focus:border-slate-900 focus:ring-slate-200'
            "
          />

          <p
            v-if="fieldErrors.price"
            class="mt-1 text-xs font-medium text-red-600"
          >
            {{ fieldErrors.price }}
          </p>
        </div>

        <div>
          <label
            for="product-stock"
            class="mb-2 block text-sm font-semibold text-slate-700"
          >
            Stok
          </label>

          <input
            id="product-stock"
            v-model.number="form.stock"
            type="number"
            min="0"
            step="1"
            placeholder="0"
            class="block w-full rounded-xl border bg-white px-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 shadow-sm outline-none transition focus:ring-2"
            :class="
              fieldErrors.stock
                ? 'border-red-400 focus:border-red-400 focus:ring-red-100'
                : 'border-slate-300 hover:border-slate-400 focus:border-slate-900 focus:ring-slate-200'
            "
          />

          <p
            v-if="fieldErrors.stock"
            class="mt-1 text-xs font-medium text-red-600"
          >
            {{ fieldErrors.stock }}
          </p>
        </div>
      </div>

      <div>
        <label
          for="product-status"
          class="mb-2 block text-sm font-semibold text-slate-700"
        >
          Status
        </label>

        <select
          id="product-status"
          v-model="form.status"
          class="block w-full appearance-none rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-medium text-slate-900 shadow-sm outline-none transition hover:border-slate-400 focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
        >
          <option value="active">
            Aktif
          </option>

          <option value="inactive">
            Tidak Aktif
          </option>
        </select>
      </div>

      <div>
        <label
          for="product-description"
          class="mb-2 block text-sm font-semibold text-slate-700"
        >
          Deskripsi
        </label>

        <textarea
          id="product-description"
          v-model="form.description"
          rows="4"
          placeholder="Masukkan deskripsi produk"
          class="block w-full resize-none rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 shadow-sm outline-none transition hover:border-slate-400 focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
        ></textarea>
      </div>

      <div
        class="flex flex-col-reverse gap-3 border-t border-slate-200 pt-5 sm:flex-row sm:justify-end"
      >
        <button
          type="button"
          :disabled="submitting"
          class="rounded-xl border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
          @click="handleCancel"
        >
          Batal
        </button>

        <button
          type="submit"
          :disabled="submitting || categoriesLoading"
          class="rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {{ submitting ? 'Menyimpan...' : isEditMode ? 'Simpan Perubahan' : 'Simpan Produk' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from 'vue';

import { getCategories } from '@/api/categoryService';

import {
  createProduct,
  updateProduct,
} from '@/api/productService';

const props = defineProps({
  product: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits([
  'success',
  'cancel',
]);

const isEditMode = computed(() => {
  return !!props.product;
});

const categories = ref([]);
const categoriesLoading = ref(false);

const submitting = ref(false);
const errorMessage = ref('');

const fieldErrors = reactive({});

const form = reactive({
  name: '',
  sku: '',
  category_id: '',
  description: '',
  price: 0,
  stock: 0,
  status: 'active',
});

function clearErrors() {
  errorMessage.value = '';

  Object.keys(fieldErrors).forEach((key) => {
    delete fieldErrors[key];
  });
}

function fillFormFromProduct() {
  if (!props.product) {
    form.name = '';
    form.sku = '';
    form.category_id = '';
    form.description = '';
    form.price = 0;
    form.stock = 0;
    form.status = 'active';

    return;
  }

  form.name = props.product.name || '';
  form.sku = props.product.sku || '';

  form.category_id =
    props.product.category?.id ||
    props.product.category_id ||
    '';

  form.description = props.product.description || '';

  form.price = Number(props.product.price || 0);
  form.stock = Number(props.product.stock || 0);

  form.status = props.product.status || 'active';
}

function getFirstErrorMessage(value) {
  if (Array.isArray(value)) {
    return value[0];
  }

  return value;
}

function handleApiError(error) {
  clearErrors();

  const responseData = error.response?.data;

  if (!responseData) {
    errorMessage.value = 'Gagal menyimpan produk.';
    return;
  }

  if (responseData.detail) {
    errorMessage.value = responseData.detail;
    return;
  }

  const data = responseData.data;

  if (
    data &&
    typeof data === 'object' &&
    !Array.isArray(data)
  ) {
    Object.entries(data).forEach(([key, value]) => {
      fieldErrors[key] = getFirstErrorMessage(value);
    });
  }

  if (responseData.message) {
    errorMessage.value = responseData.message;
  }

  if (Object.keys(fieldErrors).length === 0 && !errorMessage.value) {
    errorMessage.value = 'Gagal menyimpan produk.';
  }
}

async function fetchCategories() {
  categoriesLoading.value = true;

  try {
    const response = await getCategories();

    categories.value = response.data?.data || [];
  } catch (error) {
    console.error('Failed to fetch categories:', error);

    errorMessage.value = 'Gagal memuat kategori.';
  } finally {
    categoriesLoading.value = false;
  }
}

function validateForm() {
  clearErrors();

  let valid = true;

  if (!form.name.trim()) {
    fieldErrors.name = 'Nama produk wajib diisi.';
    valid = false;
  }

  if (!form.sku.trim()) {
    fieldErrors.sku = 'SKU wajib diisi.';
    valid = false;
  }

  if (!form.category_id) {
    fieldErrors.category_id = 'Kategori wajib diisi.';
    valid = false;
  }

  if (
    form.price === '' ||
    form.price === null ||
    Number(form.price) < 0
  ) {
    fieldErrors.price = 'Harga harus 0 atau lebih besar.';
    valid = false;
  }

  if (
    form.stock === '' ||
    form.stock === null ||
    Number(form.stock) < 0
  ) {
    fieldErrors.stock = 'Stok harus 0 atau lebih besar.';
    valid = false;
  }

  return valid;
}

async function handleSubmit() {
  if (!validateForm()) {
    return;
  }

  submitting.value = true;

  try {
    const payload = {
      name: form.name.trim(),
      sku: form.sku.trim(),
      description: form.description.trim(),
      price: Number(form.price),
      stock: Number(form.stock),
      status: form.status,
      category_id: form.category_id,
    };

    let response;

    if (isEditMode.value) {
      response = await updateProduct(
        props.product.id,
        payload,
      );
    } else {
      response = await createProduct(payload);
    }

    if (response.data?.success) {
      emit(
        'success',
        response.data.data,
      );

      return;
    }

    errorMessage.value = isEditMode.value
      ? 'Gagal memperbarui produk.'
      : 'Gagal membuat produk.';
  } catch (error) {
    console.error(
      isEditMode.value
        ? 'Update product error:'
        : 'Create product error:',
      error,
    );

    handleApiError(error);
  } finally {
    submitting.value = false;
  }
}

function handleCancel() {
  emit('cancel');
}

onMounted(async () => {
  await fetchCategories();
  fillFormFromProduct();
});
</script>