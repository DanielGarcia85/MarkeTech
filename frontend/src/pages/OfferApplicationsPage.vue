<!--
  frontend/src/pages/OfferApplicationsPage.vue

  Offer applications page — the applications to one offer of the employer
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/employer/offers/<id>/applications", to an
  employer only (the router sends anyone else away); another employer's
  offer is "not found". The offer as a heading, then the applications as
  cards (ApplicationCard), newest first, with the moves of their state
  carried out by the shared composable, the two decisions after a
  confirmation.
-->

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

import { listApplications, type Application } from "../api/applications";
import { getOffer, type Offer } from "../api/offers";
import { useApplicationMoves } from "../applications";
import ApplicationCard from "../components/ApplicationCard.vue";

const { t } = useI18n();
const route = useRoute();

const offerId = Number(route.params.id);
const offer = ref<Offer | null>(null);
const notFound = ref(false);
const applications = ref<Application[] | null>(null);
const loadFailed = ref(false);

const { busy, errors, move } = useApplicationMoves(applications);

async function load(): Promise<void> {
  notFound.value = false;
  loadFailed.value = false;
  try {
    offer.value = await getOffer(offerId);
  } catch {
    // 404 for another employer's offer, or no such offer
    notFound.value = true;
    return;
  }
  try {
    applications.value = await listApplications({ offer: offerId });
  } catch {
    loadFailed.value = true;
  }
}

onMounted(load);
</script>

<template>
  <!-- Two ways back, one arrow: the list of the offers, the list of all
       the applications -->
  <p class="back">
    ← <RouterLink :to="{ name: 'myOffers' }">{{ t("offerApplications.back") }}</RouterLink>
    ·
    <RouterLink :to="{ name: 'receivedApplications' }">{{ t("offerApplications.backToReceived") }}</RouterLink>
  </p>

  <p v-if="notFound" class="notice">{{ t("offerApplications.notFound") }}</p>

  <template v-else-if="offer">
    <h1>{{ t("offerApplications.title") }}</h1>
    <p class="offer">
      <RouterLink :to="{ name: 'offer', params: { id: offer.id } }">{{ offer.title }}</RouterLink>
      · {{ offer.city }}
      <span class="pill" :class="offer.status">{{ t("offers.status." + offer.status) }}</span>
      <RouterLink :to="{ name: 'offerEdit', params: { id: offer.id } }">{{ t("offers.editLink") }}</RouterLink>
    </p>

    <p v-if="loadFailed" class="error">{{ t("offerApplications.loadFailed") }}</p>

    <template v-else-if="applications">
      <p class="count">{{ t("offerApplications.count", applications.length) }}</p>
      <ul v-if="applications.length" class="cards">
        <li v-for="application in applications" :key="application.id">
          <ApplicationCard
            :application="application"
            :busy="busy === application.id"
            :error="errors[application.id]"
            @move="move(application, $event)"
          />
        </li>
      </ul>
    </template>
  </template>
</template>

<style scoped>
/* The arrow and the dot in the colour of the links, like the other pages */
.back {
  margin: 0 0 16px;
  color: var(--mt-blue);
}

.back a {
  text-decoration: none;
}

.back a:hover {
  text-decoration: underline;
}

/* The offer under the title, with its state */
.offer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin: -8px 0 20px;
  color: var(--mt-muted);
}

.count {
  margin: 0;
  color: var(--mt-muted);
}

.cards {
  margin: 8px 0 0;
  padding: 0;
  list-style: none;
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
</style>
