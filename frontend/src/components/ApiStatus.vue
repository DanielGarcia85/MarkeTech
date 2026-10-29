<!--
  frontend/src/components/ApiStatus.vue

  API status — shows whether the backend can be reached
  ───────────────────────────────────────────────────────────────────────────
  Calls the health endpoint once, when the component is displayed, and shows
  the result in the current language, as a span: it sits in the left
  column of the footer, after the technologies, which gives it lighter
  colours for its dark background. The state is told by its colour too: a dot and the word in
  green when the backend answers, in red when it does not, in grey while
  it is being asked.
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
  <span>
    {{ t("health.label") }}
    <strong class="state" :class="status">{{ t(`health.${status}`) }}</strong>
  </span>
</template>

<style scoped>
/* The state, preceded by a dot of the same colour */
.state {
  white-space: nowrap;
}

.state::before {
  content: "";
  display: inline-block;
  width: 8px;
  height: 8px;
  margin-right: 5px;
  border-radius: 50%;
  background: currentColor;
  vertical-align: 1px;
}

.checking {
  color: var(--mt-muted);
}

.online {
  color: var(--mt-success);
}

.offline {
  color: var(--mt-error);
}
</style>
