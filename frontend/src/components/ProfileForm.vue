<script setup>
import { reactive, ref, watch } from 'vue';

import BaseButton from '@/components/BaseButton.vue';
import BaseInput from '@/components/BaseInput.vue';
import { useAuthStore } from '@/stores/auth';

const props = defineProps({
  user: { type: Object, required: true },
});

const emit = defineEmits(['saved', 'cancel']);
const authStore = useAuthStore();
const submitting = ref(false);
const errorMessage = ref('');
const fieldErrors = reactive({});
const form = reactive({ username: '', email: '' });

watch(
  () => props.user,
  (user) => {
    form.username = user?.username || '';
    form.email = user?.email || '';
  },
  { immediate: true },
);

function clearErrors() {
  errorMessage.value = '';
  Object.keys(fieldErrors).forEach((key) => delete fieldErrors[key]);
}

function firstMessage(value) {
  return Array.isArray(value) ? value[0] : value;
}

async function handleSubmit() {
  clearErrors();
  submitting.value = true;

  try {
    const user = await authStore.updateProfile({
      username: form.username.trim(),
      email: form.email.trim(),
    });
    emit('saved', user);
  } catch (error) {
    console.error('Failed to update profile:', error);
    const data = error.response?.data;
    if (data && typeof data === 'object') {
      Object.entries(data).forEach(([key, value]) => {
        if (key in fieldErrors) fieldErrors[key] = firstMessage(value);
      });
    }
    errorMessage.value = data?.detail || data?.message || '';
    if (!errorMessage.value && Object.keys(fieldErrors).every((key) => !fieldErrors[key])) {
      errorMessage.value = 'Gagal memperbarui profil.';
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
      <label for="profile-username" class="mb-2 block text-sm font-semibold text-slate-700">
        Username <span class="text-red-600">* Wajib</span>
      </label>
      <BaseInput
        id="profile-username"
        v-model="form.username"
        required
        :error="fieldErrors.username"
        autocomplete="username"
      />
      <p v-if="fieldErrors.username" id="profile-username-error" class="mt-1 text-xs text-red-600">
        {{ fieldErrors.username }}
      </p>
    </div>

    <div>
      <label for="profile-email" class="mb-2 block text-sm font-semibold text-slate-700">
        Email <span class="text-red-600">* Wajib</span>
      </label>
      <BaseInput
        id="profile-email"
        v-model="form.email"
        type="email"
        required
        :error="fieldErrors.email"
        autocomplete="email"
      />
      <p v-if="fieldErrors.email" id="profile-email-error" class="mt-1 text-xs text-red-600">
        {{ fieldErrors.email }}
      </p>
    </div>

    <div class="flex flex-col-reverse gap-3 border-t border-slate-200 pt-4 sm:flex-row sm:justify-end">
      <BaseButton variant="secondary" :disabled="submitting" @click="emit('cancel')">
        Batal
      </BaseButton>
      <BaseButton type="submit" :disabled="submitting">
        {{ submitting ? 'Menyimpan...' : 'Simpan Profil' }}
      </BaseButton>
    </div>
  </form>
</template>
