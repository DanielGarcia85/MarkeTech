<!--
  frontend/src/pages/LoginPage.vue

  Login page — opens the session of an existing account
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/account/login". Sends the address and the password to the
  authentication API through the session module, which keeps the user on
  success. A 400 shows its errors under the fields, a 401 means the address
  has not been verified yet, a 429 that the attempts come too fast. Once
  logged in, the visitor goes to the page they were asking for, given in
  the address as ?next= by the router or by a link, or to the home page (a
  user already logged in never reaches this page: the router sends them
  home). Beside the form, on its right, a box to try the site without an
  account (above it on a narrow window): two buttons open the demo
  candidate or the demo employer (api/demo.ts), shared accounts made again
  every night. The link "Demo" of the header leads here.
-->

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";

import type { Role } from "../api/account";
import { demoLogin } from "../api/demo";
import { errorsByParam } from "../api/http";
import { loadSession, login } from "../session";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

// Where to go once logged in: the address asked for, when it is one of
// this site (a path, not an address of another site), else the home page
function next(): string {
  const asked = route.query.next;
  const path = typeof asked === "string" ? asked : "";
  return path.startsWith("/") && !path.startsWith("//") ? path : "/";
}

// What the visitor types
const email = ref("");
const password = ref("");

// What the page shows: the errors by field, a request in flight, the
// address still to verify
const errors = ref<Record<string, string>>({});
const sending = ref(false);
const unverified = ref(false);

// The demo account being opened, and the reason it could not be
const demoSending = ref(false);
const demoError = ref("");

async function tryDemo(role: Role): Promise<void> {
  demoSending.value = true;
  demoError.value = "";
  try {
    const answer = await demoLogin(role);
    if (answer.status === 200) {
      // The session is open on the server: the header and the side bar
      // learn who is logged in
      await loadSession();
      router.replace(next());
    } else {
      demoError.value = t("demo.unavailable");
    }
  } catch {
    demoError.value = t("form.unreachable");
  } finally {
    demoSending.value = false;
  }
}

async function submit(): Promise<void> {
  sending.value = true;
  errors.value = {};
  unverified.value = false;
  try {
    const answer = await login(email.value, password.value);
    if (answer.status === 200) {
      router.replace(next());
    } else if (answer.status === 401) {
      // The only step the API can still ask for here: verify the address
      unverified.value = true;
    } else if (answer.status === 429) {
      errors.value = { "": t("form.tooMany") };
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
  <h1>{{ t("login.title") }}</h1>

  <p v-if="unverified" class="notice">{{ t("login.unverified") }}</p>

  <!-- The form on the left, the demo on the right; one under the other
       on a narrow window, the demo first -->
  <div class="layout">
    <div class="login">
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
    <RouterLink :to="{ name: 'passwordReset' }">{{ t("login.forgotLink") }}</RouterLink>
  </p>
  <p>
    {{ t("login.noAccount") }}
    <RouterLink :to="{ name: 'signup' }">{{ t("login.signupLink") }}</RouterLink>
  </p>
    </div>

    <!-- Trying the site without an account: the two demo accounts -->
    <section class="demo">
      <h2>{{ t("demo.title") }}</h2>
      <p>{{ t("demo.text") }}</p>
      <p class="buttons">
        <button type="button" class="primary" :disabled="demoSending" @click="tryDemo('candidate')">
          {{ t("demo.candidate") }}
        </button>
        <button type="button" class="primary" :disabled="demoSending" @click="tryDemo('employer')">
          {{ t("demo.employer") }}
        </button>
      </p>
      <p v-if="demoError" class="error">{{ demoError }}</p>
    </section>
  </div>
</template>

<style scoped>
/* The form and the demo side by side, the form on the left */
.layout {
  display: grid;
  grid-template-columns: minmax(0, 420px) minmax(0, 440px);
  gap: 24px 64px;
  align-items: start;
}

/* The demo, in a box of the light blue */
.demo {
  margin: 0;
  padding: 16px 20px;
  border: 1px solid var(--mt-blue-border);
  border-radius: 12px;
  background: var(--mt-blue-surface);
}

.demo h2 {
  margin: 0 0 6px;
  color: var(--mt-blue-dark);
  font-size: 1.15rem;
}

.demo p {
  margin: 0;
}

.buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px !important;
}

/* Narrow window: one column, the demo first, above the form. Last, so
   that it wins over the rules above */
@media (max-width: 900px) {
  .layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .demo {
    order: -1;
  }
}
</style>
