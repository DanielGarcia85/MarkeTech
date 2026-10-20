<!--
  frontend/src/pages/ReceivedApplicationsPage.vue

  Received applications page — every application to the employer's offers
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/employer/applications", to an employer only
  (the router sends anyone else away). All the applications to all their
  offers in one list, newest first, each card naming its offer, so that
  nothing has to be looked for offer by offer; narrowed by state with a
  select, kept in the address (?status=) so that the back button and a
  reload keep it. The moves of the state are the same as on the page of
  one offer (ApplicationCard, shared composable).
-->

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";

import { listApplications, type Application, type ApplicationStatus } from "../api/applications";
import { useApplicationMoves, useApplicationText } from "../applications";
import ApplicationCard from "../components/ApplicationCard.vue";

const STATUSES: ApplicationStatus[] = ["received", "in_progress", "accepted", "rejected"];

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const text = useApplicationText();

const applications = ref<Application[] | null>(null);
const loadFailed = ref(false);

const { busy, errors, move } = useApplicationMoves(applications);

// The state asked for in the address, or "" for all of them
const status = computed<ApplicationStatus | "">(() => {
  const asked = route.query.status;
  return typeof asked === "string" && (STATUSES as string[]).includes(asked) ? (asked as ApplicationStatus) : "";
});

async function load(): Promise<void> {
  loadFailed.value = false;
  try {
    applications.value = await listApplications(status.value ? { status: status.value } : {});
  } catch {
    loadFailed.value = true;
  }
}

// A new state chosen: into the address, which reloads the list
function choose(event: Event): void {
  const value = (event.target as HTMLSelectElement).value;
  router.replace({ query: value ? { status: value } : {} });
}

watch(() => route.query.status, load);

onMounted(load);
</script>

<template>
  <div class="head">
    <h1>{{ t("receivedApplications.title") }}</h1>
    <label class="filter">
      {{ t("receivedApplications.status") }}
      <select :value="status" @change="choose">
        <option value="">{{ t("receivedApplications.allStatuses") }}</option>
        <option v-for="value in STATUSES" :key="value" :value="value">{{ text.status(value) }}</option>
      </select>
    </label>
  </div>

  <p v-if="loadFailed" class="error">{{ t("receivedApplications.loadFailed") }}</p>

  <template v-else-if="applications">
    <p class="count">{{ t("receivedApplications.count", applications.length) }}</p>
    <ul v-if="applications.length" class="cards">
      <li v-for="application in applications" :key="application.id">
        <ApplicationCard
          :application="application"
          show-offer
          :busy="busy === application.id"
          :error="errors[application.id]"
          @move="move(application, $event)"
        />
      </li>
    </ul>
  </template>
</template>

<style scoped>
/* The title on the left, the filter on the right */
.head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.head h1 {
  margin: 0;
}

.filter {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter select {
  padding: 6px 8px;
  border: 1px solid var(--mt-border);
  border-radius: 4px;
  background: var(--mt-background);
  color: var(--mt-text);
  font: inherit;
}

.count {
  margin: 16px 0 0;
  color: var(--mt-muted);
}

.cards {
  margin: 8px 0 0;
  padding: 0;
  list-style: none;
}
</style>
