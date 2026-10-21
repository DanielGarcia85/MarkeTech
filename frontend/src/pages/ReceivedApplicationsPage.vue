<!--
  frontend/src/pages/ReceivedApplicationsPage.vue

  Received applications page — every application to the employer's offers
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/employer/applications", to an employer only
  (the router sends anyone else away). All the applications to all their
  offers on one page, grouped by offer under a heading that names it, the
  offer with the newest application first and, within a group, the newest
  application first, so that nothing has to be looked for offer by offer;
  narrowed by state with a select, kept in the address (?status=) so that
  the back button and a reload keep it. The moves of the state are the same
  as on the page of one offer (ApplicationCard, shared composable).
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

// The applications by offer, in the order they come (newest first): an
// offer appears with its first application met, and keeps its rank
const groups = computed(() => {
  const byOffer = new Map<number, { offer: Application["offer"]; items: Application[] }>();
  for (const application of applications.value ?? []) {
    const group = byOffer.get(application.offer.id) ?? { offer: application.offer, items: [] };
    group.items.push(application);
    byOffer.set(application.offer.id, group);
  }
  return [...byOffer.values()];
});

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
    <!-- One section per offer: its title as a link to its own page of
         applications, its city, its state, then its applications -->
    <section v-for="group in groups" :key="group.offer.id" class="group">
      <h2 class="offer">
        <RouterLink :to="{ name: 'offerApplications', params: { id: group.offer.id } }">
          {{ group.offer.title }}
        </RouterLink>
        <span class="muted">· {{ group.offer.city }}</span>
        <span class="pill" :class="group.offer.status">{{ t("offers.status." + group.offer.status) }}</span>
        <span class="muted">{{ t("offerApplications.count", group.items.length) }}</span>
      </h2>
      <ul class="cards">
        <li v-for="application in group.items" :key="application.id">
          <ApplicationCard
            :application="application"
            :busy="busy === application.id"
            :error="errors[application.id]"
            @move="move(application, $event)"
          />
        </li>
      </ul>
    </section>
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

/* The groups, one per offer, each under a heavier rule than the cards */
.group {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 3px solid var(--mt-border);
}

.offer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 1.15rem;
}

.offer a {
  text-decoration: none;
}

.offer a:hover {
  text-decoration: underline;
}

.muted {
  color: var(--mt-muted);
  font-size: 0.95rem;
  font-weight: normal;
}

/* The state of the offer: grey for a draft, green once published, dark
   grey when closed */
.pill {
  display: inline-block;
  padding: 1px 10px;
  border: 1px solid var(--mt-border);
  border-radius: 999px;
  background: var(--mt-surface);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.pill.published {
  border-color: var(--mt-success-surface);
  background: var(--mt-success-surface);
  color: var(--mt-success);
}

.pill.closed {
  background: var(--mt-border);
  color: var(--mt-text);
}

.cards {
  margin: 0;
  padding: 0;
  list-style: none;
}

/* The last card of a group needs no rule: the next group brings its own */
.cards li:last-child :deep(.card) {
  border-bottom: none;
}
</style>
