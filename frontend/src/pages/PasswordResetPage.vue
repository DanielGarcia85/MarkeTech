<!--
  frontend/src/pages/PasswordResetPage.vue

  Password reset page — asks for the e-mail with the link to a new password
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/account/password/reset". Sends the address to the
  authentication API, which answers 200 whether an account exists or not
  (the e-mail says which, the page never does). A 400 shows the error of
  the field, a 429 that the requests come too fast.
-->

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";

import { requestPasswordReset } from "../api/account";
import { errorsByParam } from "../api/http";

const { t } = useI18n();

// What the visitor types
const email = ref("");

// What the page shows: the errors by field, a request in flight, the e-mail
// sent
const errors = ref<Record<string, string>>({});
const sending = ref(false);
const sent = ref(false);

async function submit(): Promise<void> {
  sending.value = true;
  errors.value = {};
  try {
    const answer = await requestPasswordReset(email.value);
    if (answer.status === 200) {
      sent.value = true;
    } else if (answer.status === 429) {
      errors.value = { "": t("form.tooMany") };
    } else {
      // 400: the error of the field; anything else: a general message
      errors.value = answer.errors
        ? errorsByParam(answer.errors)
        : { "": t("form.failed") };
    }
  } catch {
    errors.value = { "": t("form.unreachable") };
  } finally {
    sending.value = false;
  }
}
</script>

<template>
  <h1>{{ t("passwordReset.title") }}</h1>

  <p v-if="sent" class="notice">{{ t("passwordReset.sent", { email }) }}</p>

  <!-- novalidate: the backend checks the field and answers in the language
       of the interface, so the browser's own messages are not wanted -->
  <form v-else novalidate @submit.prevent="submit">
    <p>{{ t("passwordReset.intro") }}</p>
    <p v-if="errors['']" class="error">{{ errors[""] }}</p>

    <div class="field">
      <label for="email">{{ t("passwordReset.email") }}</label>
      <input id="email" v-model="email" type="email" autocomplete="email" />
      <p v-if="errors.email" class="error">{{ errors.email }}</p>
    </div>

    <button type="submit" class="primary" :disabled="sending">
      {{ t("passwordReset.submit") }}
    </button>
  </form>
</template>
