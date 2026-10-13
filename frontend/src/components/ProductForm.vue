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
  getProduct,
  updateProduct,
} from '@/api/productService';
import BaseButton from '@/components/BaseButton.vue';
import BaseInput from '@/components/BaseInput.vue';
import BaseSelect from '@/components/BaseSelect.vue';
import { parsePriceInput } from '@/utils/price';

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
const formLoading = ref(false);
const productLoadFailed = ref(false);

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

const priceInput = ref('0');

function clearErrors() {
  errorMessage.value = '';

  Object.keys(fieldErrors).forEach((key) => {
    delete fieldErrors[key];
  });
}

function formatPriceInput(value) {
  const valueString = String(value);
  const decimalSeparator = valueString.includes(',') ? ',' : '.';
  const [integerPart, fractionalPart] = valueString.split(decimalSeparator);
  const groupedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

  return fractionalPart === undefined
    ? groupedInteger
    : `${groupedInteger},${fractionalPart}`;
}

function handlePriceInput(event) {
  const input = event.target;
  const rawValue = input.value;
  const cursorPosition = input.selectionStart ?? rawValue.length;
  const valueBeforeCursor = rawValue.slice(0, cursorPosition);
  const digitsBeforeCursor = (valueBeforeCursor.match(/\d/g) || []).length;
  const negativeSignBeforeCursor = valueBeforeCursor.trimStart().startsWith('-');
  const parsedPrice = parsePriceInput(rawValue);
  const hasDecimalBeforeCursor = parsedPrice.hasDecimalSeparator
    && cursorPosition > parsedPrice.separatorIndex;
  const decimalDigitsBeforeCursor = hasDecimalBeforeCursor
    ? valueBeforeCursor.slice(parsedPrice.separatorIndex + 1).replace(/\D/g, '').length
    : 0;

  priceInput.value = parsedPrice.formattedValue;
  form.price = parsedPrice.numericValue === '' ? '' : Number(parsedPrice.numericValue);
  input.value = parsedPrice.formattedValue;

  let nextCursorPosition = 0;
  if (hasDecimalBeforeCursor && parsedPrice.formattedValue.includes(',')) {
    nextCursorPosition = parsedPrice.formattedValue.indexOf(',') + 1 + decimalDigitsBeforeCursor;
  } else {
    const integerLength = parsedPrice.numericValue.replace('-', '').split('.')[0].length;
    const integerDigitCount = Math.min(digitsBeforeCursor, integerLength);
    nextCursorPosition = rawValue.trimStart().startsWith('-') && negativeSignBeforeCursor ? 1 : 0;
    let matchedDigits = 0;
    for (let index = 0; index < parsedPrice.formattedValue.length; index += 1) {
      if (/\d/.test(parsedPrice.formattedValue[index])) {
        matchedDigits += 1;
        if (matchedDigits === integerDigitCount) {
          nextCursorPosition = index + 1;
          break;
        }
      }
    }
  }
  if (negativeSignBeforeCursor && nextCursorPosition === 0) {
    nextCursorPosition = 1;
  }

  input.setSelectionRange(nextCursorPosition, nextCursorPosition);
}

function handleStockStep(amount) {
  const currentStock = Number(form.stock);
  form.stock = Math.max(0, (Number.isFinite(currentStock) ? currentStock : 0) + amount);
}

function fillFormFromProduct(product = props.product) {
  if (!product) {
    form.name = '';
    form.sku = '';
    form.category_id = '';
    form.description = '';
    form.price = 0;
    priceInput.value = formatPriceInput(form.price);
    form.stock = 0;
    form.status = 'active';

    return;
  }

  form.name = product.name || '';
  form.sku = product.sku || '';

  form.category_id =
    product.category?.id ||
    product.category_id ||
    '';

  form.description = product.description || '';

  form.price = Number(product.price || 0);
  priceInput.value = formatPriceInput(form.price);
  form.stock = Number(product.stock || 0);

  form.status = product.status || 'active';
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

  const data = responseData.data || responseData;

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

async function fetchProductForEdit() {
  formLoading.value = true;

  try {
    const response = await getProduct(props.product.id);
    if (!response.data?.success || !response.data.data) {
      throw new Error('Respons detail produk tidak valid.');
    }

    fillFormFromProduct(response.data.data);
  } catch (error) {
    console.error('Failed to load product for editing:', error);
    productLoadFailed.value = true;
    errorMessage.value = error.response?.data?.detail
      || 'Gagal memuat data produk untuk diedit.';
  } finally {
    formLoading.value = false;
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
    priceInput.value.trim() === '' ||
    priceInput.value.trim().startsWith('-') ||
    !Number.isFinite(Number(form.price)) ||
    Number(form.price) < 0
  ) {
    fieldErrors.price = 'Harga harus 0 atau lebih besar.';
    valid = false;
  }

  if (
    form.stock === '' ||
    form.stock === null ||
    !Number.isInteger(Number(form.stock)) ||
    Number(form.stock) < 0
  ) {
    fieldErrors.stock = 'Stok harus berupa bilangan bulat 0 atau lebih besar.';
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
  fillFormFromProduct();
  await Promise.all([
    fetchCategories(),
    isEditMode.value ? fetchProductForEdit() : Promise.resolve(),
  ]);
});
</script>

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
      v-if="errorMessage && !productLoadFailed"
      class="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="formLoading"
      class="flex min-h-64 flex-col items-center justify-center gap-3"
      role="status"
      aria-live="polite"
    >
      <div
        class="h-9 w-9 animate-spin rounded-full border-4 border-slate-200 border-t-indigo-600"
        aria-hidden="true"
      ></div>
      <p class="text-sm font-medium text-slate-500">
        Memuat data produk...
      </p>
    </div>

    <div
      v-else-if="productLoadFailed"
      role="alert"
      class="flex flex-col gap-4"
    >
      <p class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
        {{ errorMessage }}
      </p>
      <div class="flex justify-end">
        <BaseButton variant="secondary" @click="handleCancel">
          Tutup
        </BaseButton>
      </div>
    </div>

    <form
      v-else
      class="space-y-5"
      @submit.prevent="handleSubmit"
    >
      <div>
        <label
          for="product-name"
          class="mb-2 block text-sm font-semibold text-slate-700"
        >
          Nama Produk
          <span class="text-red-600">* Wajib</span>
        </label>

        <BaseInput
          id="product-name"
          v-model="form.name"
          type="text"
          placeholder="Masukkan nama produk"
          :required="true"
          :error="fieldErrors.name"
        />

        <p
          v-if="fieldErrors.name"
          id="product-name-error"
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
          <span class="text-red-600">* Wajib</span>
        </label>

        <BaseInput
          id="product-sku"
          v-model="form.sku"
          type="text"
          placeholder="Masukkan SKU produk"
          :required="true"
          :error="fieldErrors.sku"
        />

        <p
          v-if="fieldErrors.sku"
          id="product-sku-error"
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
          <span class="text-red-600">* Wajib</span>
        </label>

        <BaseSelect
          id="product-category"
          v-model="form.category_id"
          :disabled="categoriesLoading"
          required
          :error="fieldErrors.category_id"
        >
          <option value="">
            {{ categoriesLoading ? 'Memuat kategori...' : 'Pilih kategori' }}
          </option>
          <option
            v-for="category in categories"
            :key="category.id"
            :value="category.id"
          >
            {{ category.name }}
          </option>
        </BaseSelect>

          <div
            class="hidden"
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
        <p
          v-if="fieldErrors.category_id"
          id="product-category-error"
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
            Harga (Rp)
            <span class="text-red-600">* Wajib</span>
          </label>

          <div
            class="flex items-center overflow-hidden rounded-xl border bg-white shadow-sm transition focus-within:ring-2"
            :class="fieldErrors.price
              ? 'border-red-400 focus-within:border-red-400 focus-within:ring-red-100'
              : 'border-slate-300 hover:border-slate-400 focus-within:border-indigo-600 focus-within:ring-indigo-100'"
          >
            <span
              class="inline-flex items-center self-stretch border-r bg-slate-50 px-3.5 text-sm font-semibold text-slate-600 select-none"
              :class="fieldErrors.price ? 'border-red-200' : 'border-slate-300'"
            >
              Rp
            </span>
            <input
              id="product-price"
              :value="priceInput"
              type="text"
              inputmode="decimal"
              placeholder="0"
              :required="true"
              :aria-invalid="fieldErrors.price ? 'true' : undefined"
              aria-describedby="product-price-error"
              @input="handlePriceInput"
              class="block min-w-0 flex-1 border-0 bg-transparent px-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 outline-none focus:outline-none focus:ring-0"
            />
          </div>

          <p
            v-if="fieldErrors.price"
            id="product-price-error"
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
            <span class="text-red-600">* Wajib</span>
          </label>

          <div class="flex min-w-0 gap-2">
            <button
              type="button"
              aria-label="Kurangi stok"
              :disabled="submitting || Number(form.stock) <= 0"
              @click="handleStockStep(-1)"
              class="inline-flex min-h-11 min-w-11 items-center justify-center rounded-xl border border-slate-300 bg-white px-3 text-lg font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              -
            </button>

            <BaseInput
              id="product-stock"
              v-model="form.stock"
              type="text"
              inputmode="numeric"
              placeholder="0"
              :required="true"
              :error="fieldErrors.stock"
              input-class="min-w-0 flex-1 text-center"
            />

            <button
              type="button"
              aria-label="Tambah stok"
              :disabled="submitting"
              @click="handleStockStep(1)"
              class="inline-flex min-h-11 min-w-11 items-center justify-center rounded-xl border border-slate-300 bg-white px-3 text-lg font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              +
            </button>
          </div>

          <p
            v-if="fieldErrors.stock"
            id="product-stock-error"
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
          <span class="text-slate-500">Opsional</span>
        </label>

        <BaseSelect
          id="product-status"
          v-model="form.status"
        >
          <option value="active">
            Aktif
          </option>

          <option value="inactive">
            Tidak Aktif
          </option>
        </BaseSelect>
      </div>

      <div>
        <label
          for="product-description"
          class="mb-2 block text-sm font-semibold text-slate-700"
        >
          Deskripsi
          <span class="text-slate-500">Opsional</span>
        </label>

        <textarea
          id="product-description"
          v-model="form.description"
          rows="4"
          placeholder="Masukkan deskripsi produk"
          class="block w-full resize-none rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 shadow-sm outline-none transition hover:border-slate-400 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100"
        ></textarea>
      </div>

      <div
        class="flex flex-col-reverse gap-3 border-t border-slate-200 pt-5 sm:flex-row sm:justify-end"
      >
        <BaseButton
          type="button"
          variant="secondary"
          :disabled="submitting"
          @click="handleCancel"
        >
          Batal
        </BaseButton>

        <BaseButton
          type="submit"
          :disabled="submitting || categoriesLoading"
        >
          {{ submitting ? 'Menyimpan...' : isEditMode ? 'Simpan Perubahan' : 'Simpan Produk' }}
        </BaseButton>
      </div>
    </form>
  </div>
</template>