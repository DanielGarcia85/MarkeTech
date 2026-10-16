<!--
  frontend/src/pages/VerifyEmailPage.vue

  Address verification page — target of the link in the confirmation e-mail
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/account/verify-email/:key". Sends the key read from the
  address to the authentication API as soon as the page opens, then says
  whether the address is confirmed (401: it is, and nobody is logged in
  yet) or the link is invalid or expired (400). No form: everything the API
  needs is in the address.
-->

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

import { verifyEmail } from "../api/account";

const { t } = useI18n();
const route = useRoute();

// Outcome of the verification, pending until the API has answered
const state = ref<"pending" | "confirmed" | "invalid" | "failed">("pending");

async function verify(): Promise<void> {
  try {
    const answer = await verifyEmail(String(route.params.key));
    if (answer.status === 401 || answer.status === 200) {
      // Confirmed; with our settings the account is not logged in by this
      state.value = "confirmed";
    } else if (answer.status === 400) {
      state.value = "invalid";
    } else {
      state.value = "failed";
    }
  } catch {
    state.value = "failed";
  }
}

// Runs once, when the page opens
verify();
</script>

<template>
  <h1>{{ t("verify.title") }}</h1>

  <p v-if="state === 'pending'">{{ t("verify.pending") }}</p>
  <p v-else-if="state === 'confirmed'" class="notice">
    {{ t("verify.confirmed") }}
    <RouterLink :to="{ name: 'login' }">{{ t("verify.loginLink") }}</RouterLink>
  </p>
  <p v-else-if="state === 'invalid'" class="error">
    {{ t("verify.invalid") }}
    <RouterLink :to="{ name: 'login' }">{{ t("verify.loginLink") }}</RouterLink>
  </p>
  <p v-else class="error">{{ t("form.unreachable") }}</p>
</template>
