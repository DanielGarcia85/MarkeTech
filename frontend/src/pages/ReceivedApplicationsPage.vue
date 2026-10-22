<!--
  frontend/src/pages/ReceivedApplicationsPage.vue

  Received applications page — every application to the employer's offers
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/employer/applications", to an employer only
  (the router sends anyone else away). All the applications to all their
  offers on one page, grouped by offer under a heading that names it, the
  offer with the newest application first and, within a group, the newest
  application first, so that nothing has to be looked for offer by offer.
  Two filters, kept in the address so that the back button and a reload
  keep them: the state (?status=, a select) and the offer (?offer=, set by
  the links of "My offers", of the page of an offer and of its form; the
  offer is then named under the title, with its state and the way to its
  form, and a line above the title leads back to every application).
  Another employer's offer is "not found". The moves of the state are the
  same for every card (ApplicationCard, shared composable); each card leads
  to its conversation, with its unread messages, read with the list, and
  its appointments that bring news.
-->

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";

import { listApplications, type Application, type ApplicationStatus } from "../api/applications";
import { listConversations } from "../api/messaging";
import { getOffer, type Offer } from "../api/offers";
import { useApplicationMoves, useApplicationText } from "../applications";
import { newsOf, refreshNotifications } from "../notifications";
import ApplicationCard from "../components/ApplicationCard.vue";
import EmptyState from "../components/EmptyState.vue";

const STATUSES: ApplicationStatus[] = ["received", "in_progress", "accepted", "rejected"];

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const text = useApplicationText();

const applications = ref<Application[] | null>(null);
const loadFailed = ref(false);
// The offer asked for in the address, once read; "not found" when it is
// not one of the employer's
const offer = ref<Offer | null>(null);
const notFound = ref(false);

// The unread messages of each application that has a conversation
const unread = ref<Record<number, number>>({});

async function loadConversations(): Promise<void> {
  try {
    const conversations = await listConversations();
    unread.value = Object.fromEntries(conversations.map((c) => [c.application, c.unread]));
  } catch {
    // The cards show the way to the conversations in progress anyway
  }
}

const { busy, errors, move } = useApplicationMoves(applications, loadConversations);

// The filters, as the address says them: a state among the four or "" for
// all, an offer by its number or 0 for all
const status = computed<ApplicationStatus | "">(() => {
  const asked = route.query.status;
  return typeof asked === "string" && (STATUSES as string[]).includes(asked) ? (asked as ApplicationStatus) : "";
});
const offerId = computed(() => {
  const asked = route.query.offer;
  return typeof asked === "string" && /^\d+$/.test(asked) ? Number(asked) : 0;
});

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

async function load(): Promise<void> {
  loadFailed.value = false;
  notFound.value = false;
  offer.value = null;
  if (offerId.value) {
    try {
      offer.value = await getOffer(offerId.value);
    } catch {
      // 404 for another employer's offer, or no such offer
      notFound.value = true;
      return;
    }
  }
  loadConversations();
  try {
    applications.value = await listApplications({
      ...(offerId.value ? { offer: offerId.value } : {}),
      ...(status.value ? { status: status.value } : {}),
    });
    // The news listed are seen now: the side bar counts again
    refreshNotifications();
  } catch {
    loadFailed.value = true;
  }
}

// A new state chosen: into the address, next to the offer if any, which
// reloads the list
function choose(event: Event): void {
  const value = (event.target as HTMLSelectElement).value;
  router.replace({ query: { ...(offerId.value ? { offer: String(offerId.value) } : {}), ...(value ? { status: value } : {}) } });
}

watch(() => [route.query.status, route.query.offer], load);

onMounted(load);
</script>

<template>
  <!-- Narrowed to one offer: the way back to every application, the state
       chosen kept -->
  <p v-if="offerId" class="back">
    <RouterLink :to="{ query: status ? { status } : {} }">← {{ t("receivedApplications.allApplications") }}</RouterLink>
  </p>

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

  <p v-if="notFound" class="notice">{{ t("receivedApplications.notFound") }}</p>

  <template v-else>
    <!-- Narrowed to one offer: the offer named as a group heading would
         name it, with its state and the way to its form -->
    <h2 v-if="offer" class="title offer">
      <RouterLink :to="{ name: 'offer', params: { id: offer.id } }">{{ offer.title }}</RouterLink>
      <span class="muted">· {{ offer.city }}</span>
      <span class="pill" :class="offer.status">{{ t("offers.status." + offer.status) }}</span>
      <RouterLink :to="{ name: 'offerEdit', params: { id: offer.id } }" class="edit">{{ t("offers.editLink") }}</RouterLink>
    </h2>

    <p v-if="loadFailed" class="error">{{ t("receivedApplications.loadFailed") }}</p>

    <template v-else-if="applications">
      <EmptyState v-if="applications.length === 0" icon="inbox" :text="t('receivedApplications.none')" />
      <p v-else class="count">{{ t("receivedApplications.count", applications.length) }}</p>
      <!-- One section per offer: its title as a link to the offer, its
           city, its state, how many, then its applications; narrowed to
           one offer, the heading would repeat the line above -->
      <section v-for="group in groups" :key="group.offer.id" class="group">
        <h2 v-if="!offerId" class="title">
          <RouterLink :to="{ name: 'offer', params: { id: group.offer.id } }">{{ group.offer.title }}</RouterLink>
          <span class="muted">· {{ group.offer.city }}</span>
          <span class="pill" :class="group.offer.status">{{ t("offers.status." + group.offer.status) }}</span>
          <span class="muted">{{ t("receivedApplications.count", group.items.length) }}</span>
        </h2>
        <ul class="cards">
          <li v-for="application in group.items" :key="application.id">
            <ApplicationCard
              :application="application"
              :busy="busy === application.id"
              :error="errors[application.id]"
              :unread="newsOf(unread[application.id], application.id)"
              @move="move(application, $event)"
            />
          </li>
        </ul>
      </section>
    </template>
  </template>
</template>

<style scoped>
.back {
  margin: 0 0 16px;
}

.back a {
  text-decoration: none;
}

.back a:hover {
  text-decoration: underline;
}

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

/* The offer the page is narrowed to, under the title: a group heading */
.offer {
  margin-top: 12px;
}

.edit {
  font-size: 0.95rem;
  font-weight: normal;
}

.count {
  margin: 16px 0 0;
  color: var(--mt-muted);
}

/* The groups, one per offer, each under a rule, its heading above its
   boxes */
.group {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--mt-border);
}

.title {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px;
  font-size: 1.15rem;
}

.title a {
  text-decoration: none;
}

.title a:hover {
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
</style>
