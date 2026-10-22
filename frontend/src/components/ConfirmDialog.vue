<!--
  frontend/src/components/ConfirmDialog.vue

  Confirmation dialog — the box that asks the question of confirm.ts
  ───────────────────────────────────────────────────────────────────────────
  Placed once by App.vue, invisible until a page calls confirm(). Built on
  the browser's <dialog> element, opened as a modal: the page behind is
  greyed and cannot be clicked, the focus stays in the box, and Escape
  closes it. The box itself is styled like the rest of the site. When the
  question asks for a text (confirmWithText), a text area under it, the
  focus in it; the box is then wider. A text required keeps the action
  disabled until something is typed.
-->

<script setup lang="ts">
import { nextTick, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import { answer, draft, useConfirm } from "../confirm";

const { t } = useI18n();
const state = useConfirm();

// The <dialog> element, to open and close it
const box = ref<HTMLDialogElement | null>(null);

// Opens the box when a question arrives, closes it when it is answered.
// nextTick: the element exists only once Vue has rendered the question
watch(
  () => state.question,
  async (question) => {
    await nextTick();
    if (question) {
      box.value?.showModal();
    } else if (box.value?.open) {
      box.value.close();
    }
  },
);

// A click on the greyed page lands on the <dialog> itself, not on the box
// inside it: that counts as a cancel, like Escape
function clickOutside(event: MouseEvent): void {
  if (event.target === box.value) answer(false);
}
</script>

<template>
  <dialog
    v-if="state.question"
    ref="box"
    class="confirm"
    @cancel.prevent="answer(false)"
    @click="clickOutside"
  >
    <div class="box" :class="{ wide: state.question.textLabel }">
      <p class="question">{{ state.question.message }}</p>
      <div v-if="state.question.textLabel" class="field">
        <label for="confirm-text">{{ state.question.textLabel }}</label>
        <textarea id="confirm-text" v-model="draft" rows="5" maxlength="2000" autofocus></textarea>
      </div>
      <p class="choices">
        <button type="button" class="secondary" @click="answer(false)">
          {{ t("dialog.cancel") }}
        </button>
        <button
          type="button"
          class="primary"
          :autofocus="!state.question.textLabel"
          :disabled="state.question.required && !draft.trim()"
          @click="answer(true)"
        >
          {{ state.question.action }}
        </button>
      </p>
    </div>
  </dialog>
</template>

<style scoped>
/* The <dialog> fills the window and carries the grey veil; the box sits
   in its middle */
.confirm {
  width: 100%;
  max-width: none;
  height: 100%;
  max-height: none;
  margin: 0;
  padding: 16px;
  border: none;
  background: transparent;
}

.confirm::backdrop {
  background: rgba(30, 41, 59, 0.45);
}

.box {
  max-width: 420px;
  margin: 20vh auto 0;
  padding: 20px 24px;
  border: 1px solid var(--mt-border);
  border-radius: 8px;
  background: var(--mt-background);
  box-shadow: 0 16px 40px rgba(30, 41, 59, 0.2);
}

.box.wide {
  max-width: 560px;
  margin-top: 12vh;
}

.question {
  margin: 0 0 20px;
  font-size: 1.05rem;
}

.field textarea {
  display: block;
  width: 100%;
  padding: 8px;
  border: 1px solid var(--mt-border);
  border-radius: 6px;
  color: var(--mt-text);
  font: inherit;
  resize: vertical;
}

/* The two buttons on the right, cancel first, the action last */
.choices {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin: 0;
}

.secondary {
  padding: 8px 16px;
  border: 1px solid var(--mt-border);
  border-radius: 4px;
  background: var(--mt-surface);
  color: var(--mt-text);
  font: inherit;
  cursor: pointer;
}
</style>
