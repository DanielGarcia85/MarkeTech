<!--
  frontend/src/pages/SignupPage.vue

  Sign-up page — creates an account, then asks to confirm the address
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/account/signup". Sends the names, the address, the
  password, the role and the acceptance of the terms of use to the
  authentication API. A 400 shows its errors under the fields; a 401 means
  the account is there and the confirmation e-mail is on its way, whether
  the account is new or already existed (the API never tells which). A
  logged-in user has nothing to do here: the router sends them home before
  the page is shown.
-->

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";

import { signUp, type Role } from "../api/account";
import { errorsByParam } from "../api/http";

const { t } = useI18n();

// What the visitor types; candidate is preselected, the most common case
const firstName = ref("");
const lastName = ref("");
const email = ref("");
const password = ref("");
const passwordConfirm = ref("");
const role = ref<Role>("candidate");
// The terms of use: the account is not created until the box is ticked
const terms = ref(false);

// What the page shows: the errors by field, a request in flight, the e-mail
// sent
const errors = ref<Record<string, string>>({});
const sending = ref(false);
const sent = ref(false);

async function submit(): Promise<void> {
  errors.value = {};
  // The two checks made here: the API receives the password once, and the
  // box is ticked (the backend refuses too, with a drier message)
  if (password.value !== passwordConfirm.value) {
    errors.value = { passwordConfirm: t("form.passwordMismatch") };
    return;
  }
  if (!terms.value) {
    errors.value = { terms: t("signup.termsRequired") };
    return;
  }
  sending.value = true;
  try {
    const answer = await signUp({
      email: email.value,
      password: password.value,
      firstName: firstName.value,
      lastName: lastName.value,
      role: role.value,
      terms: terms.value,
    });
    if (answer.status === 401) {
      sent.value = true;
    } else {
      // 400: the errors of the fields; anything else: a general message
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
  <h1>{{ t("signup.title") }}</h1>

  <p v-if="sent" class="notice">{{ t("signup.sent", { email }) }}</p>

  <!-- novalidate: the backend checks the fields and answers in the language
       of the interface, so the browser's own messages are not wanted -->
  <form v-else novalidate @submit.prevent="submit">
    <p v-if="errors['']" class="error">{{ errors[""] }}</p>

    <!-- The errors come back under the names the backend uses -->
    <div class="field">
      <label for="first-name">{{ t("signup.firstName") }}</label>
      <input
        id="first-name"
        v-model="firstName"
        type="text"
        autocomplete="given-name"
      />
      <p v-if="errors.first_name" class="error">{{ errors.first_name }}</p>
    </div>

    <div class="field">
      <label for="last-name">{{ t("signup.lastName") }}</label>
      <input
        id="last-name"
        v-model="lastName"
        type="text"
        autocomplete="family-name"
      />
      <p v-if="errors.last_name" class="error">{{ errors.last_name }}</p>
    </div>

    <div class="field">
      <label for="email">{{ t("signup.email") }}</label>
      <input id="email" v-model="email" type="email" autocomplete="email" />
      <p v-if="errors.email" class="error">{{ errors.email }}</p>
    </div>

    <div class="field">
      <label for="password">{{ t("signup.password") }}</label>
      <input
        id="password"
        v-model="password"
        type="password"
        autocomplete="new-password"
      />
      <p v-if="errors.password" class="error">{{ errors.password }}</p>
    </div>

    <div class="field">
      <label for="password-confirm">{{ t("signup.passwordConfirm") }}</label>
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

    <fieldset class="field choices">
      <legend>{{ t("signup.role") }}</legend>
      <label>
        <input v-model="role" type="radio" value="candidate" />
        {{ t("signup.candidate") }}
      </label>
      <label>
        <input v-model="role" type="radio" value="employer" />
        {{ t("signup.employer") }}
      </label>
      <p v-if="errors.role" class="error">{{ errors.role }}</p>
    </fieldset>

    <!-- The terms, with their links: i18n-t puts each link where the text
         says {terms} or {privacy} -->
    <div class="field consent">
      <label>
        <input v-model="terms" type="checkbox" />
        <i18n-t keypath="signup.terms" tag="span">
          <template #terms>
            <RouterLink :to="{ name: 'terms' }" target="_blank">{{ t("signup.termsLink") }}</RouterLink>
          </template>
          <template #privacy>
            <RouterLink :to="{ name: 'privacy' }" target="_blank">{{ t("signup.privacyLink") }}</RouterLink>
          </template>
        </i18n-t>
      </label>
      <p v-if="errors.terms" class="error">{{ errors.terms }}</p>
    </div>

    <button type="submit" class="primary" :disabled="sending">
      {{ t("signup.submit") }}
    </button>
  </form>

  <p v-if="!sent">
    {{ t("signup.haveAccount") }}
    <RouterLink :to="{ name: 'login' }">{{ t("signup.loginLink") }}</RouterLink>
  </p>
</template>

<style scoped>
/* The box and its sentence on one line, the sentence wrapping under itself */
.consent label {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  max-width: 420px;
  font-weight: normal;
}

.consent input {
  flex: none;
  margin-top: 5px;
}
</style>
