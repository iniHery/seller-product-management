<script setup>
import { reactive, ref } from 'vue';

import { changePassword } from '@/api/authService';
import BaseButton from '@/components/BaseButton.vue';
import BaseInput from '@/components/BaseInput.vue';

const emit = defineEmits(['saved', 'cancel']);
const submitting = ref(false);
const errorMessage = ref('');
const fieldErrors = reactive({});
const form = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
});

function clearErrors() {
  errorMessage.value = '';
  Object.keys(fieldErrors).forEach((key) => delete fieldErrors[key]);
}

function firstMessage(value) {
  return Array.isArray(value) ? value[0] : value;
}

async function handleSubmit() {
  clearErrors();
  if (form.new_password !== form.confirm_password) {
    fieldErrors.confirm_password = 'Konfirmasi password baru tidak cocok.';
    return;
  }

  submitting.value = true;
  try {
    const response = await changePassword({
      current_password: form.current_password,
      new_password: form.new_password,
    });
    if (!response.data?.success) {
      throw new Error('Server tidak mengonfirmasi perubahan password.');
    }
    emit('saved');
  } catch (error) {
    console.error('Failed to change password:', error);
    const data = error.response?.data;
    if (data && typeof data === 'object') {
      Object.entries(data).forEach(([key, value]) => {
        if (key in fieldErrors) fieldErrors[key] = firstMessage(value);
      });
    }
    errorMessage.value = data?.detail || data?.message || '';
    if (!errorMessage.value && Object.keys(fieldErrors).every((key) => !fieldErrors[key])) {
      errorMessage.value = 'Gagal mengubah password.';
    }
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="handleSubmit">
    <div
      v-if="errorMessage"
      role="alert"
      class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
    >
      {{ errorMessage }}
    </div>

    <div>
      <label for="current-password" class="mb-2 block text-sm font-semibold text-slate-700">
        Password saat ini <span class="text-red-600">* Wajib</span>
      </label>
      <BaseInput
        id="current-password"
        v-model="form.current_password"
        type="password"
        required
        autocomplete="current-password"
        :error="fieldErrors.current_password"
      />
      <p v-if="fieldErrors.current_password" id="current-password-error" class="mt-1 text-xs text-red-600">
        {{ fieldErrors.current_password }}
      </p>
    </div>

    <div>
      <label for="new-password" class="mb-2 block text-sm font-semibold text-slate-700">
        Password baru <span class="text-red-600">* Wajib</span>
      </label>
      <BaseInput
        id="new-password"
        v-model="form.new_password"
        type="password"
        required
        autocomplete="new-password"
        :error="fieldErrors.new_password"
      />
      <p v-if="fieldErrors.new_password" id="new-password-error" class="mt-1 text-xs text-red-600">
        {{ fieldErrors.new_password }}
      </p>
    </div>

    <div>
      <label for="confirm-password" class="mb-2 block text-sm font-semibold text-slate-700">
        Konfirmasi password baru <span class="text-red-600">* Wajib</span>
      </label>
      <BaseInput
        id="confirm-password"
        v-model="form.confirm_password"
        type="password"
        required
        autocomplete="new-password"
        :error="fieldErrors.confirm_password"
      />
      <p v-if="fieldErrors.confirm_password" id="confirm-password-error" class="mt-1 text-xs text-red-600">
        {{ fieldErrors.confirm_password }}
      </p>
    </div>

    <div class="flex flex-col-reverse gap-3 border-t border-slate-200 pt-4 sm:flex-row sm:justify-end">
      <BaseButton variant="secondary" :disabled="submitting" @click="emit('cancel')">
        Batal
      </BaseButton>
      <BaseButton type="submit" :disabled="submitting">
        {{ submitting ? 'Menyimpan...' : 'Ubah Password' }}
      </BaseButton>
    </div>
  </form>
</template>
