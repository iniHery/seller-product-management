<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';

const props = defineProps({
  id: {
    type: String,
    default: undefined,
  },
  modelValue: {
    type: [String, Number],
    default: '',
  },
  options: {
    type: Array,
    required: true,
    default: () => [],
  },
  placeholder: {
    type: String,
    default: 'Pilih...',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:modelValue', 'change']);

const rootRef = ref(null);
const optionsRef = ref(null);
const isOpen = ref(false);
const highlightIndex = ref(-1);

const selectedOption = computed(() => {
  const currentVal = props.modelValue ?? '';
  return props.options.find((opt) => String(opt.value ?? '') === String(currentVal));
});

const displayLabel = computed(() => {
  if (selectedOption.value) {
    return selectedOption.value.label;
  }
  return props.placeholder;
});

const isPlaceholder = computed(() => {
  const currentVal = props.modelValue ?? '';
  return !selectedOption.value || currentVal === '';
});

function toggleOpen() {
  if (props.disabled) return;
  if (isOpen.value) {
    close();
  } else {
    open();
  }
}

function open() {
  if (props.disabled) return;
  isOpen.value = true;
  const currentVal = props.modelValue ?? '';
  const currentIdx = props.options.findIndex((opt) => String(opt.value ?? '') === String(currentVal));
  highlightIndex.value = currentIdx >= 0 ? currentIdx : 0;

  nextTick(() => {
    scrollToHighlighted();
  });
}

function close() {
  isOpen.value = false;
  highlightIndex.value = -1;
}

function selectOption(option) {
  if (props.disabled) return;
  emit('update:modelValue', option.value);
  emit('change', option.value);
  close();
}

function scrollToHighlighted() {
  if (!optionsRef.value || highlightIndex.value < 0) return;
  const items = optionsRef.value.querySelectorAll('[role="option"]');
  if (items[highlightIndex.value]) {
    items[highlightIndex.value].scrollIntoView({ block: 'nearest' });
  }
}

function handleKeydown(event) {
  if (props.disabled) return;

  if (!isOpen.value) {
    if (['ArrowDown', 'ArrowUp', 'Enter', ' '].includes(event.key)) {
      event.preventDefault();
      open();
    }
    return;
  }

  const max = props.options.length - 1;

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault();
      highlightIndex.value = highlightIndex.value < max ? highlightIndex.value + 1 : 0;
      scrollToHighlighted();
      break;

    case 'ArrowUp':
      event.preventDefault();
      highlightIndex.value = highlightIndex.value > 0 ? highlightIndex.value - 1 : max;
      scrollToHighlighted();
      break;

    case 'Enter':
    case ' ':
      event.preventDefault();
      if (highlightIndex.value >= 0 && props.options[highlightIndex.value]) {
        selectOption(props.options[highlightIndex.value]);
      }
      break;

    case 'Escape':
      event.preventDefault();
      close();
      break;

    case 'Tab':
      close();
      break;
  }
}

function onClickOutside(event) {
  if (isOpen.value && rootRef.value && !rootRef.value.contains(event.target)) {
    close();
  }
}

watch(
  () => props.disabled,
  (isDisabled) => {
    if (isDisabled && isOpen.value) {
      close();
    }
  }
);

onMounted(() => {
  document.addEventListener('click', onClickOutside, true);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', onClickOutside, true);
});
</script>

<template>
  <div
    ref="rootRef"
    class="relative inline-block w-full text-left"
    :class="{ 'z-30': isOpen, 'z-10': !isOpen }"
  >
    <!-- Trigger Button -->
    <button
      :id="id"
      type="button"
      :disabled="disabled"
      class="group flex w-full items-center justify-between gap-2 rounded-xl border bg-white px-4 py-3 text-sm font-medium shadow-xs transition duration-200 outline-none focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400 disabled:border-slate-200"
      :class="[
        isOpen
          ? 'border-indigo-600 ring-2 ring-indigo-100'
          : 'border-slate-300 hover:border-slate-400 text-slate-900',
      ]"
      @click="toggleOpen"
      @keydown="handleKeydown"
      :aria-expanded="isOpen"
      :aria-haspopup="'listbox'"
    >
      <span
        class="truncate text-left"
        :class="isPlaceholder ? 'text-slate-500 font-normal' : 'text-slate-900 font-medium'"
      >
        {{ displayLabel }}
      </span>

      <!-- Chevron Icon -->
      <svg
        class="h-5 w-5 shrink-0 text-slate-400 transition-transform duration-200 group-hover:text-slate-600"
        :class="{ 'rotate-180 text-indigo-600 group-hover:text-indigo-600': isOpen }"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        fill="currentColor"
        aria-hidden="true"
      >
        <path
          fill-rule="evenodd"
          d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
          clip-rule="evenodd"
        />
      </svg>
    </button>

    <!-- Options Panel Dropdown -->
    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="transform scale-95 opacity-0 -translate-y-1"
      enter-to-class="transform scale-100 opacity-100 translate-y-0"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="transform scale-100 opacity-100 translate-y-0"
      leave-to-class="transform scale-95 opacity-0 -translate-y-1"
    >
      <div
        v-if="isOpen"
        ref="optionsRef"
        class="absolute left-0 mt-1.5 w-full max-h-60 overflow-y-auto rounded-xl border border-slate-200 bg-white p-1.5 shadow-xl ring-1 ring-black/5 focus:outline-none"
        role="listbox"
        :aria-activedescendant="highlightIndex >= 0 ? `option-${id || 'select'}-${highlightIndex}` : undefined"
        tabindex="-1"
      >
        <div
          v-if="options.length === 0"
          class="px-3 py-2.5 text-center text-xs text-slate-400"
        >
          Tidak ada pilihan
        </div>

        <div
          v-for="(option, idx) in options"
          :key="option.value"
          :id="`option-${id || 'select'}-${idx}`"
          role="option"
          :aria-selected="String(option.value ?? '') === String(modelValue ?? '')"
          class="group/item flex cursor-pointer items-center justify-between rounded-lg px-3 py-2.5 text-sm transition-colors duration-150 select-none"
          :class="[
            String(option.value ?? '') === String(modelValue ?? '')
              ? 'bg-indigo-50 text-indigo-700 font-semibold'
              : highlightIndex === idx
                ? 'bg-slate-100 text-slate-900 font-medium'
                : 'text-slate-700 hover:bg-slate-50 hover:text-slate-900 font-medium',
          ]"
          @click="selectOption(option)"
          @mouseenter="highlightIndex = idx"
        >
          <span class="truncate">{{ option.label }}</span>

          <!-- Checkmark Icon for Active Selection -->
          <svg
            v-if="String(option.value ?? '') === String(modelValue ?? '')"
            class="ml-2 h-4 w-4 shrink-0 text-indigo-600"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true"
          >
            <path
              fill-rule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
      </div>
    </Transition>
  </div>
</template>
