// frontend/src/confirm.ts
//
// Confirmation — one question to the user, answered by yes or no
// ─────────────────────────────────────────────────────────────────────────────
// Replaces the browser's own confirm(), which cannot be styled. A page calls
// confirm(message, action) and awaits the answer; ConfirmDialog.vue, placed
// once in App.vue, shows the question and gives the answer. One question at
// a time: the state below holds the one being asked, or nothing. A question
// may also ask for a text, optional (confirmWithText): the message of the
// employer that goes with a move of an application.

import { reactive, readonly, ref } from "vue";

type Question = {
  // What is asked, and the label of the button that says yes
  message: string;
  action: string;
  // The label of the text asked for, when one is
  textLabel?: string;
  // Settles the promise given to the caller
  resolve: (yes: boolean) => void;
};

const state = reactive<{ question: Question | null }>({ question: null });

// The text typed in the box, written by the dialog component
export const draft = ref("");

// Read-only view for the dialog component
export function useConfirm() {
  return readonly(state);
}

// Asks the question and resolves with the answer: true for the action,
// false for cancel, Escape or a click outside the box
export function confirm(message: string, action: string): Promise<boolean> {
  return new Promise((resolve) => {
    state.question = { message, action, resolve };
  });
}

// Asks the question with a text field under it; resolves with the text
// (possibly empty) for the action, null for cancel
export function confirmWithText(message: string, action: string, textLabel: string): Promise<string | null> {
  draft.value = "";
  return new Promise((resolve) => {
    state.question = {
      message,
      action,
      textLabel,
      resolve: (yes) => resolve(yes ? draft.value.trim() : null),
    };
  });
}

// Called by the dialog component with the answer; closes the question
export function answer(yes: boolean): void {
  state.question?.resolve(yes);
  state.question = null;
}
