<!--
  frontend/src/components/ApiStatus.vue

  API status — shows whether the backend can be reached
  ───────────────────────────────────────────────────────────────────────────
  Calls the health endpoint once, when the component is displayed, and shows
  the result in the current language.
-->

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";

import { getJson } from "../api/http";

// The three situations the component can be in
type Status = "checking" | "online" | "offline";

// Shape of the answer sent by /api/health/
type HealthAnswer = { status: string };

const { t } = useI18n();

// Starts as "checking" until the backend has answered
const status = ref<Status>("checking");

// Runs once, as soon as the component is on the page
onMounted(async () => {
  try {
    const answer = await getJson<HealthAnswer>("/api/health/");
    status.value = answer.status === "ok" ? "online" : "offline";
  } catch {
    // Backend stopped, network down or error status: all mean unavailable
    status.value = "offline";
  }
});
</script>

<template>
  <p>
    {{ t("health.label") }}
    <strong>{{ t(`health.${status}`) }}</strong>
  </p>
</template>
