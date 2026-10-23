<!--
  frontend/src/components/StarInput.vue

  Star input — a score from 1 to 5, chosen by clicking a star
  ───────────────────────────────────────────────────────────────────────────
  Used by MyReviewPage for each score of the review. Five radio buttons of
  the browser, hidden, each with a star as its label: the keyboard works
  as for any group of radio buttons (Tab to the group, the arrows to move),
  and a screen reader reads "3 out of 5". The stars up to the one chosen
  are filled; under the pointer, those up to the one pointed at. The word
  of the score follows ("Good"), and the error of the field, if any.
-->

<script setup lang="ts">
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps<{
  // The score chosen, 0 before any
  modelValue: number;
  // The radio buttons of one score share a name, unique in the page
  name: string;
  legend: string;
  error?: string;
  // The overall rating: bigger stars
  large?: boolean;
}>();

const emit = defineEmits<{ "update:modelValue": [value: number] }>();

const { t } = useI18n();

// The star under the pointer, 0 when none
const pointed = ref(0);
const shown = computed(() => pointed.value || props.modelValue);

// Under the pointer, unless the form is disabled (a demo account)
function point(event: MouseEvent, n: number): void {
  if (!(event.currentTarget as HTMLElement).closest("fieldset:disabled")) pointed.value = n;
}

const STAR = "M12 2.5l2.9 5.9 6.5.9-4.7 4.6 1.1 6.5L12 17.3l-5.8 3.1 1.1-6.5-4.7-4.6 6.5-.9z";
</script>

<template>
  <fieldset class="star-input" :class="{ large }">
    <legend>{{ legend }}</legend>
    <div class="line">
      <span class="stars" @mouseleave="pointed = 0">
        <template v-for="n in 5" :key="n">
          <input
            :id="`${name}-${n}`"
            type="radio"
            :name="name"
            :value="n"
            :checked="modelValue === n"
            @change="emit('update:modelValue', n)"
          />
          <label :for="`${name}-${n}`" :class="{ on: n <= shown }" @mouseenter="point($event, n)">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path :d="STAR" /></svg>
            <span class="hidden">{{ t("reviews.outOfFive", { value: n }) }}</span>
          </label>
        </template>
      </span>
      <span class="word">{{ shown ? t(`reviews.word.${shown}`) : t("reviews.choose") }}</span>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
  </fieldset>
</template>

<style scoped>
.star-input {
  margin: 0;
  padding: 0;
  border: none;
}

legend {
  margin-bottom: 4px;
  padding: 0;
  font-weight: 600;
}

.line {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stars {
  display: inline-flex;
}

/* The radio buttons stay in the page for the keyboard, out of sight */
input,
.hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}

label {
  padding: 2px;
  border-radius: 4px;
  color: var(--mt-border);
  line-height: 0;
  cursor: pointer;
}

label svg {
  width: 26px;
  height: 26px;
  fill: currentColor;
}

.large label svg {
  width: 34px;
  height: 34px;
}

label.on {
  color: var(--mt-accent);
}

/* The star reached with the keyboard: the ring of the site */
input:focus-visible + label {
  outline: 2px solid var(--mt-blue);
  outline-offset: 1px;
}

/* A demo account: nothing to choose */
fieldset:disabled label {
  cursor: not-allowed;
}

.word {
  color: var(--mt-muted);
  font-size: 0.9rem;
}
</style>
