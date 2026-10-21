<!--
  frontend/src/pages/VerifyEmailPage.vue

  Address verification page — target of the link in the confirmation e-mail
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/account/verify-email/:key". Sends the key read from the
  address to the authentication API as soon as the session is known, then
  says whether the address is confirmed or the link is invalid or expired
  (400). Two cases: a visitor confirming the address of a new account (401:
  confirmed, nobody is logged in yet), and a logged-in user confirming a new
  address for their account (200: it replaces the old one). No form:
  everything the API needs is in the address.
-->

<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

import { verifyEmail } from "../api/account";
import { loadSession, useSession } from "../session";

const { t } = useI18n();
const route = useRoute();
const session = useSession();

// Outcome of the verification, pending until the API has answered
const state = ref<"pending" | "confirmed" | "invalid" | "failed">("pending");
// Whether a user was logged in when the link was opened: the texts differ
const loggedIn = ref(false);
// What the API says of a refused link, beyond the usual expiry: for
// instance, an address that another account uses already
const reason = ref("");

async function verify(): Promise<void> {
  loggedIn.value = session.user !== null;
  try {
    const answer = await verifyEmail(String(route.params.key));
    if (answer.status === 401 || answer.status === 200) {
      // Confirmed. A new account is not logged in by this; a logged-in user
      // now has the new address, and the header shows it
      if (loggedIn.value) await loadSession();
      state.value = "confirmed";
    } else if (answer.status === 400) {
      state.value = "invalid";
      reason.value =
        answer.errors?.find((error) => error.code !== "invalid_or_expired_key")?.message ?? "";
    } else {
      state.value = "failed";
    }
  } catch {
    state.value = "failed";
  }
}

// Runs once the session is known, so that the right case is told apart
watch(
  () => session.loaded,
  (loaded) => {
    if (loaded) verify();
  },
  { immediate: true },
);
</script>

<template>
  <h1>{{ t("verify.title") }}</h1>

  <p v-if="state === 'pending'">{{ t("verify.pending") }}</p>
  <p v-else-if="state === 'confirmed'" class="notice">
    <template v-if="loggedIn">
      {{ t("verify.changed") }}
      <RouterLink :to="{ name: 'credentials' }">{{ t("verify.credentialsLink") }}</RouterLink>
    </template>
    <template v-else>
      {{ t("verify.confirmed") }}
      <RouterLink :to="{ name: 'login' }">{{ t("verify.loginLink") }}</RouterLink>
    </template>
  </p>
  <p v-else-if="state === 'invalid'" class="error">
    <template v-if="loggedIn">
      {{ t("verify.invalidLoggedIn") }} {{ reason }}
      <RouterLink :to="{ name: 'credentials' }">{{ t("verify.credentialsLink") }}</RouterLink>
    </template>
    <template v-else>
      {{ t("verify.invalid") }} {{ reason }}
      <RouterLink :to="{ name: 'login' }">{{ t("verify.loginLink") }}</RouterLink>
    </template>
  </p>
  <p v-else class="error">{{ t("form.unreachable") }}</p>
</template>
