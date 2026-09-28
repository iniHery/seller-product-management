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
            Categories
          </h1>

          <p class="mt-1 text-sm text-slate-500 sm:text-base">
            Manage your product categories
          </p>
        </div>

        <button
          type="button"
          @click="openCreateForm"
          class="inline-flex items-center justify-center rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2"
        >
          <span class="mr-2 text-lg leading-none">+</span>
          Add Category
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
           ADD / EDIT CATEGORY FORM
      ========================================= -->
      <div
        v-if="showForm"
        class="mb-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <h2 class="mb-4 text-lg font-semibold text-slate-900">
          {{ editingCategory ? 'Edit Category' : 'Add Category' }}
        </h2>

        <form @submit.prevent="handleSubmit">
          <!-- Category Name -->
          <div class="mb-4">
            <label
              for="categoryName"
              class="mb-2 block text-sm font-semibold text-slate-700"
            >
              Category Name
            </label>

            <input
              id="categoryName"
              v-model="formName"
              type="text"
              placeholder="Enter category name..."
              class="block w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 shadow-sm outline-none transition duration-200 hover:border-slate-400 focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
              :class="{ 'border-red-400': formError }"
            />

            <p
              v-if="formError"
              class="mt-2 text-sm text-red-600"
            >
              {{ formError }}
            </p>
          </div>

          <!-- Form Buttons -->
          <div class="flex flex-wrap gap-3">
            <button
              type="submit"
              :disabled="submitting"
              class="inline-flex items-center justify-center rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {{ submitting
                ? 'Saving...'
                : editingCategory
                  ? 'Save Changes'
                  : 'Save Category'
              }}
            </button>

            <button
              type="button"
              @click="closeForm"
              :disabled="submitting"
              class="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>

      <!-- ========================================
           DELETE CONFIRMATION MODAL
      ========================================= -->
      <div
        v-if="showDeleteModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-0"
      >
        <!-- Backdrop -->
        <div
          class="fixed inset-0 bg-slate-900/50 transition-opacity"
          @click="!deleting && cancelDelete()"
        ></div>

        <!-- Modal Panel -->
        <div
          class="relative w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left shadow-xl transition-all sm:my-8"
        >
          <div class="mb-4">
            <h3 class="text-lg font-bold text-slate-900">
              Delete Category?
            </h3>
            <p class="mt-2 text-sm text-slate-500">
              Are you sure you want to delete <span class="font-semibold text-slate-900">{{ categoryToDelete?.name }}</span>? This action cannot be undone.
            </p>
          </div>

          <div class="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <button
              type="button"
              @click="cancelDelete"
              :disabled="deleting"
              class="inline-flex w-full justify-center rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:ring-offset-2 sm:w-auto disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              type="button"
              @click="handleDelete"
              :disabled="deleting"
              class="inline-flex w-full justify-center rounded-xl border border-transparent bg-red-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 sm:w-auto disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ deleting ? 'Deleting...' : 'Delete Category' }}
            </button>
          </div>
        </div>
      </div>

      <!-- ========================================
           CATEGORY TABLE
      ========================================= -->
      <div
        class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
      >

        <!-- Loading State -->
        <div
          v-if="loading"
          class="flex min-h-[300px] items-center justify-center"
        >
          <div class="flex flex-col items-center">
            <div
              class="mb-4 h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900"
            ></div>

            <p class="text-sm font-medium text-slate-500">
              Loading categories...
            </p>
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-else-if="categories.length === 0"
          class="flex min-h-[300px] items-center justify-center px-6 py-12"
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
                  d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
                />
              </svg>
            </div>

            <h2 class="text-lg font-semibold text-slate-900">
              No categories found
            </h2>

            <p class="mt-2 text-sm leading-6 text-slate-500">
              Get started by creating your first category.
            </p>

            <button
              type="button"
              @click="openCreateForm"
              class="mt-5 inline-flex items-center justify-center rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
            >
              + Add Category
            </button>
          </div>
        </div>

        <!-- Table -->
        <div
          v-else
          class="overflow-x-auto"
        >
          <table class="min-w-full divide-y divide-slate-200">

            <!-- Table Head -->
            <thead class="bg-slate-50">
              <tr>
                <th
                  scope="col"
                  class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
                >
                  Category Name
                </th>

                <th
                  scope="col"
                  class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
                >
                  Created At
                </th>

                <th
                  scope="col"
                  class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
                >
                  Updated At
                </th>

                <th
                  scope="col"
                  class="px-6 py-4 text-right text-xs font-semibold uppercase tracking-wide text-slate-500"
                >
                  Actions
                </th>
              </tr>
            </thead>

            <!-- Table Body -->
            <tbody class="divide-y divide-slate-200 bg-white">
              <tr
                v-for="category in categories"
                :key="category.id"
                class="transition hover:bg-slate-50"
              >

                <!-- Name -->
                <td class="whitespace-nowrap px-6 py-4 text-sm font-semibold text-slate-900">
                  {{ category.name }}
                </td>

                <!-- Created At -->
                <td class="whitespace-nowrap px-6 py-4 text-sm text-slate-500">
                  {{ formatDate(category.created_at) }}
                </td>

                <!-- Updated At -->
                <td class="whitespace-nowrap px-6 py-4 text-sm text-slate-500">
                  {{ formatDate(category.updated_at) }}
                </td>

                <!-- Actions -->
                <td class="whitespace-nowrap px-6 py-4 text-right">
                  <div class="flex flex-wrap items-center justify-end gap-2">
                    <button
                      type="button"
                      @click="openEditForm(category)"
                      class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 hover:text-slate-900"
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      @click="confirmDelete(category)"
                      class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-100 hover:text-red-800"
                    >
                      Delete
                    </button>
                  </div>
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
import { onMounted, ref } from 'vue';

import {
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
} from '@/api/categoryService';

/*
|--------------------------------------------------------------------------
| State
|--------------------------------------------------------------------------
*/

const categories = ref([]);

const loading = ref(false);

const errorMessage = ref('');
const successMessage = ref('');

// Form state
const showForm = ref(false);
const editingCategory = ref(null);
const formName = ref('');
const formError = ref('');
const submitting = ref(false);

// Delete state
const showDeleteModal = ref(false);
const categoryToDelete = ref(null);
const deleting = ref(false);

/*
|--------------------------------------------------------------------------
| Fetch Categories
|--------------------------------------------------------------------------
*/

async function fetchCategories() {
  loading.value = true;
  errorMessage.value = '';

  try {
    const response = await getCategories();

    categories.value = response.data?.data || [];
  } catch (error) {
    console.error('Failed to fetch categories:', error);

    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail;
    } else {
      errorMessage.value = 'Failed to load categories.';
    }

    categories.value = [];
  } finally {
    loading.value = false;
  }
}

/*
|--------------------------------------------------------------------------
| Add / Edit Category
|--------------------------------------------------------------------------
*/

function openCreateForm() {
  errorMessage.value = '';
  successMessage.value = '';
  editingCategory.value = null;
  formName.value = '';
  formError.value = '';
  showForm.value = true;
}

function openEditForm(category) {
  errorMessage.value = '';
  successMessage.value = '';
  editingCategory.value = category;
  formName.value = category.name;
  formError.value = '';
  showForm.value = true;
}

function closeForm() {
  if (submitting.value) return;
  showForm.value = false;
  editingCategory.value = null;
  formName.value = '';
  formError.value = '';
}

async function handleSubmit() {
  formError.value = '';

  // Validate
  const trimmedName = formName.value.trim();
  if (!trimmedName) {
    formError.value = 'Category name is required.';
    return;
  }

  submitting.value = true;
  errorMessage.value = '';

  try {
    if (editingCategory.value) {
      // Update
      await updateCategory(editingCategory.value.id, { name: trimmedName });

      showForm.value = false;
      editingCategory.value = null;
      formName.value = '';

      successMessage.value = 'Category updated successfully.';
    } else {
      // Create
      await createCategory({ name: trimmedName });

      showForm.value = false;
      formName.value = '';

      successMessage.value = 'Category created successfully.';
    }

    await fetchCategories();

    window.setTimeout(() => {
      successMessage.value = '';
    }, 3000);
  } catch (error) {
    console.error('Failed to save category:', error);

    // Try to extract API error message
    const data = error.response?.data;
    if (data?.detail) {
      errorMessage.value = data.detail;
    } else if (data?.name) {
      // DRF field-level error for 'name'
      const nameErrors = Array.isArray(data.name) ? data.name : [data.name];
      formError.value = nameErrors.join(' ');
    } else {
      errorMessage.value = 'Failed to save category.';
    }
  } finally {
    submitting.value = false;
  }
}

/*
|--------------------------------------------------------------------------
| Delete Category
|--------------------------------------------------------------------------
*/

function confirmDelete(category) {
  categoryToDelete.value = category;
  showDeleteModal.value = true;
}

function cancelDelete() {
  if (deleting.value) return;
  showDeleteModal.value = false;
  categoryToDelete.value = null;
}

async function handleDelete() {
  if (!categoryToDelete.value) return;

  deleting.value = true;
  errorMessage.value = '';

  try {
    await deleteCategory(categoryToDelete.value.id);

    showDeleteModal.value = false;
    successMessage.value = 'Category deleted successfully.';

    await fetchCategories();

    window.setTimeout(() => {
      successMessage.value = '';
    }, 3000);
  } catch (error) {
    console.error('Failed to delete category:', error);

    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail;
    } else {
      errorMessage.value = 'Failed to delete category.';
    }

    showDeleteModal.value = false;
  } finally {
    deleting.value = false;
    categoryToDelete.value = null;
  }
}

/*
|--------------------------------------------------------------------------
| Helpers
|--------------------------------------------------------------------------
*/

function formatDate(dateString) {
  if (!dateString) return '-';

  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '-';

  return date.toLocaleDateString('en-US', {
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
  await fetchCategories();
});
</script>
