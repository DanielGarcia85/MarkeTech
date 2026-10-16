<!--
  frontend/src/pages/NewPasswordPage.vue

  New password page — target of the link in the password reset e-mail
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/account/password/reset/:key". Sends the key read from the
  address and the new password to the authentication API. A 401 means the
  password is changed (and nobody is logged in yet), a 400 carries either
  the error of the password or that of the key, when the link is invalid or
  has already been used.
-->

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

import { resetPassword } from "../api/account";
import { errorsByParam } from "../api/http";

const { t } = useI18n();
const route = useRoute();

// What the visitor types
const password = ref("");
const passwordConfirm = ref("");

// What the page shows: the errors by field, a request in flight, the
// password changed, the link refused
const errors = ref<Record<string, string>>({});
const sending = ref(false);
const done = ref(false);
const invalid = ref(false);

async function submit(): Promise<void> {
  errors.value = {};
  // The only check made here: the API receives the password once
  if (password.value !== passwordConfirm.value) {
    errors.value = { passwordConfirm: t("form.passwordMismatch") };
    return;
  }
  sending.value = true;
  try {
    const answer = await resetPassword(
      String(route.params.key),
      password.value,
    );
    if (answer.status === 401 || answer.status === 200) {
      // Changed; with our settings the account is not logged in by this
      done.value = true;
    } else if (answer.status === 429) {
      errors.value = { "": t("form.tooMany") };
    } else if (answer.errors) {
      // 400: an error on the key is about the link, not about a field
      const byParam = errorsByParam(answer.errors);
      invalid.value = "key" in byParam;
      errors.value = byParam;
    } else {
      errors.value = { "": t("form.failed") };
    }
  } catch {
    errors.value = { "": t("form.unreachable") };
  } finally {
    sending.value = false;
  }
}
</script>

<template>
  <h1>{{ t("newPassword.title") }}</h1>

  <p v-if="done" class="notice">
    {{ t("newPassword.done") }}
    <RouterLink :to="{ name: 'login' }">{{ t("newPassword.loginLink") }}</RouterLink>
  </p>
  <p v-else-if="invalid" class="error">
    {{ t("newPassword.invalid") }}
    <RouterLink :to="{ name: 'passwordReset' }">{{ t("newPassword.requestLink") }}</RouterLink>
  </p>

  <!-- novalidate: the backend checks the field and answers in the language
       of the interface, so the browser's own messages are not wanted -->
  <form v-if="!done && !invalid" novalidate @submit.prevent="submit">
    <p v-if="errors['']" class="error">{{ errors[""] }}</p>

    <div class="field">
      <label for="password">{{ t("newPassword.password") }}</label>
      <input
        id="password"
        v-model="password"
        type="password"
        autocomplete="new-password"
      />
      <p v-if="errors.password" class="error">{{ errors.password }}</p>
    </div>

    <div class="field">
      <label for="password-confirm">{{ t("newPassword.passwordConfirm") }}</label>
      <input
        id="password-confirm"
        v-model="passwordConfirm"
        type="password"
        autocomplete="new-password"
      />
      <p v-if="errors.passwordConfirm" class="error">
        {{ errors.passwordConfirm }}
      </p>
    </div>

    <button type="submit" class="primary" :disabled="sending">
      {{ t("newPassword.submit") }}
    </button>
  </form>
</template>
