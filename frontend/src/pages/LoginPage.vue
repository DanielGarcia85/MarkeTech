<!--
  frontend/src/pages/LoginPage.vue

  Login page — opens the session of an existing account
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/account/login". Sends the address and the password to the
  authentication API through the session module, which keeps the user on
  success. A 400 shows its errors under the fields, a 401 means the address
  has not been verified yet, a 429 that the attempts come too fast. Once
  logged in, by this page or already before, the visitor goes to the home
  page.
-->

<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";

import { errorsByParam } from "../api/http";
import { login, useSession } from "../session";

const { t } = useI18n();
const router = useRouter();
const session = useSession();

// What the visitor types
const email = ref("");
const password = ref("");

// What the page shows: the errors by field, a request in flight, the
// address still to verify
const errors = ref<Record<string, string>>({});
const sending = ref(false);
const unverified = ref(false);

// Leaves as soon as someone is logged in: now, when the session loads, or
// right after a successful login
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
  unverified.value = false;
  try {
    const answer = await login(email.value, password.value);
    if (answer.status === 401) {
      // The only step the API can still ask for here: verify the address
      unverified.value = true;
    } else if (answer.status === 429) {
      errors.value = { "": t("form.tooMany") };
    } else if (answer.status !== 200) {
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
  <h1>{{ t("login.title") }}</h1>

  <p v-if="unverified" class="notice">{{ t("login.unverified") }}</p>

  <!-- novalidate: the backend checks the fields and answers in the language
       of the interface, so the browser's own messages are not wanted -->
  <form novalidate @submit.prevent="submit">
    <p v-if="errors['']" class="error">{{ errors[""] }}</p>

    <div class="field">
      <label for="email">{{ t("login.email") }}</label>
      <input id="email" v-model="email" type="email" autocomplete="email" />
      <p v-if="errors.email" class="error">{{ errors.email }}</p>
    </div>

    <div class="field">
      <label for="password">{{ t("login.password") }}</label>
      <input
        id="password"
        v-model="password"
        type="password"
        autocomplete="current-password"
      />
      <p v-if="errors.password" class="error">{{ errors.password }}</p>
    </div>

    <button type="submit" class="primary" :disabled="sending">
      {{ t("login.submit") }}
    </button>
  </form>

  <p>
    {{ t("login.noAccount") }}
    <RouterLink :to="{ name: 'signup' }">{{ t("login.signupLink") }}</RouterLink>
  </p>
</template>
