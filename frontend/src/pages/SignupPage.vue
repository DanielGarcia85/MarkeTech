<!--
  frontend/src/pages/SignupPage.vue

  Sign-up page — creates an account, then asks to confirm the address
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/account/signup". Sends the address, the password and the
  role to the authentication API. A 400 shows its errors under the fields; a
  401 means the account is there and the confirmation e-mail is on its way,
  whether the account is new or already existed (the API never tells which).
  A logged-in user has nothing to do here and is sent to the home page.
-->

<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";

import { signUp, type Role } from "../api/account";
import { errorsByParam } from "../api/http";
import { useSession } from "../session";

const { t } = useI18n();
const router = useRouter();
const session = useSession();

// What the visitor types; candidate is preselected, the most common case
const email = ref("");
const password = ref("");
const role = ref<Role>("candidate");

// What the page shows: the errors by field, a request in flight, the e-mail
// sent
const errors = ref<Record<string, string>>({});
const sending = ref(false);
const sent = ref(false);

// Leaves as soon as someone is logged in: now, or when the session loads
watch(
  () => session.user,
  (user) => {
    if (user) router.replace({ name: "home" });
  },
  { immediate: true },
);

async function submit(): Promise<void> {
  sending.value = true;
  errors.value = {};
  try {
    const answer = await signUp(email.value, password.value, role.value);
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

    <button type="submit" class="primary" :disabled="sending">
      {{ t("signup.submit") }}
    </button>
  </form>

  <p v-if="!sent">
    {{ t("signup.haveAccount") }}
    <RouterLink :to="{ name: 'login' }">{{ t("signup.loginLink") }}</RouterLink>
  </p>
</template>
