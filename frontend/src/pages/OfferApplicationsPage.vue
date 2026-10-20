<!--
  frontend/src/pages/OfferApplicationsPage.vue

  Offer applications page — the applications to one offer of the employer
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/employer/offers/<id>/applications", to an
  employer only (the router sends anyone else away); another employer's
  offer is "not found". The offer as a heading, then the applications as
  cards, newest first: the candidate and their contact details, the date,
  the state as a pill and the states gone through, the files as links, and
  the three moves of the state (in progress, accepted, rejected), the two
  decisions after a confirmation.
-->

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

import {
  EMPLOYER_STATUSES,
  listApplications,
  setStatus,
  type Application,
  type ApplicationStatus,
} from "../api/applications";
import { firstErrorOf, getOffer, type Offer } from "../api/offers";
import { useApplicationText } from "../applications";
import { confirm } from "../confirm";

const { t } = useI18n();
const route = useRoute();
const text = useApplicationText();

const offerId = Number(route.params.id);
const offer = ref<Offer | null>(null);
const notFound = ref(false);
const applications = ref<Application[] | null>(null);
const loadFailed = ref(false);

// The application whose move is in flight: its buttons are disabled meanwhile
const busy = ref<number | null>(null);
// The reason of a refused move, by application
const errors = ref<Record<number, string>>({});

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

function name(application: Application): string {
  return `${application.candidate.first_name} ${application.candidate.last_name}`.trim();
}

// One move of the state: a decision is confirmed first; the answer
// replaces the application in the list, or its reason is shown under it
async function move(application: Application, status: ApplicationStatus): Promise<void> {
  if (status !== "in_progress") {
    const question = t(`offerApplications.confirm.${status}`, { name: name(application) });
    if (!(await confirm(question, t(`offerApplications.set.${status}`)))) return;
  }
  delete errors.value[application.id];
  busy.value = application.id;
  try {
    const answer = await setStatus(application.id, status);
    if (answer.status === 200 && answer.data) {
      applications.value = (applications.value ?? []).map((item) =>
        item.id === application.id ? answer.data! : item,
      );
    } else {
      errors.value[application.id] = firstErrorOf(answer.data) || t("form.failed");
    }
  } catch {
    errors.value[application.id] = t("form.unreachable");
  } finally {
    busy.value = null;
  }
}

onMounted(load);
</script>

<template>
  <p class="back">
    <RouterLink :to="{ name: 'myOffers' }">← {{ t("offerApplications.back") }}</RouterLink>
  </p>

  <p v-if="notFound" class="notice">{{ t("offerApplications.notFound") }}</p>

  <template v-else-if="offer">
    <h1>{{ t("offerApplications.title") }}</h1>
    <p class="offer">
      <RouterLink :to="{ name: 'offer', params: { id: offer.id } }">{{ offer.title }}</RouterLink>
      · {{ offer.city }}
      <span class="pill" :class="offer.status">{{ t("offers.status." + offer.status) }}</span>
    </p>

    <p v-if="loadFailed" class="error">{{ t("offerApplications.loadFailed") }}</p>

    <template v-else-if="applications">
      <p class="count">{{ t("offerApplications.count", applications.length) }}</p>
      <ul v-if="applications.length" class="cards">
        <li v-for="application in applications" :key="application.id" class="card">
          <p class="head">
            <strong class="name">{{ name(application) }}</strong>
            <span class="pill" :class="application.status">{{ text.status(application.status) }}</span>
          </p>
          <!-- The contact details, read on the profile of the candidate -->
          <p class="line">
            <a :href="'mailto:' + application.candidate.email">{{ application.candidate.email }}</a>
            <template v-if="application.candidate.phone"> · {{ application.candidate.phone }}</template>
            <template v-if="application.candidate.city"> · {{ application.candidate.city }}</template>
          </p>
          <p class="line">{{ t("applications.sentOn", { date: text.date(application.created_at) }) }}</p>
          <p v-if="application.history.length > 1" class="history">{{ text.history(application) }}</p>
          <p class="files">
            <a :href="application.cv.url" target="_blank" rel="noopener">{{ t("applications.cv") }}</a>
            <a v-if="application.cover_letter" :href="application.cover_letter.url" target="_blank" rel="noopener">
              {{ t("applications.coverLetter") }}
            </a>
            <a
              v-for="attachment in application.attachments"
              :key="attachment.id"
              :href="attachment.url"
              target="_blank"
              rel="noopener"
            >
              {{ attachment.name }}
            </a>
          </p>
          <div class="actions">
            <button
              v-for="status in EMPLOYER_STATUSES.filter((s) => s !== application.status)"
              :key="status"
              type="button"
              :class="status === 'accepted' ? 'primary' : 'secondary'"
              :disabled="busy === application.id"
              @click="move(application, status)"
            >
              {{ t("offerApplications.set." + status) }}
            </button>
            <p v-if="errors[application.id]" class="error reason">{{ errors[application.id] }}</p>
          </div>
        </li>
      </ul>
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

.card {
  padding: 20px 0;
  border-bottom: 1px solid var(--mt-border);
}

.head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 4px;
}

.name {
  font-size: 1.1rem;
}

/* The states: of the offer (draft, published, closed) and of an
   application (received, in progress, accepted, rejected) */
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

.pill.published,
.pill.accepted {
  border-color: var(--mt-success-surface);
  background: var(--mt-success-surface);
  color: var(--mt-success);
}

.pill.closed {
  background: var(--mt-border);
  color: var(--mt-text);
}

.pill.in_progress {
  border-color: var(--mt-blue);
  color: var(--mt-blue);
}

.pill.rejected {
  border-color: var(--mt-error);
  color: var(--mt-error);
}

.line {
  margin: 0 0 2px;
}

.history {
  margin: 0 0 6px;
  color: var(--mt-muted);
  font-size: 0.85rem;
}

.files {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 16px;
  margin: 0;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 16px;
  margin-top: 12px;
}

.secondary {
  padding: 8px 16px;
  border: 1px solid var(--mt-border);
  border-radius: 4px;
  background: var(--mt-surface);
  color: var(--mt-text);
  font: inherit;
  cursor: pointer;
}

.secondary:hover {
  background: var(--mt-border);
}

.secondary:disabled {
  opacity: 0.6;
  cursor: default;
}

.reason {
  flex-basis: 100%;
  margin: 0;
}
</style>
