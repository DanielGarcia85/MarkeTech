<!--
  frontend/src/pages/MyOffersPage.vue

  My offers page — the offers of the logged-in employer, in any state
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/employer/offers", to an employer only (the
  router sends anyone else away). The offers as cards, newest first, with
  their state and the moves allowed from it: a draft is edited, published
  or deleted; a published offer is edited or closed; a closed offer is
  published again or deleted. A deletion asks for a confirmation, and is
  not offered once candidates applied: the offer is closed instead. Each
  card links to the applications received. A refused move shows the reason
  under the card; the usual one, a company without a name, links to the
  profile.
-->

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import {
  closeOffer,
  deleteOffer,
  firstErrorOf,
  myOffers,
  publishOffer,
  type Offer,
} from "../api/offers";
import { getCountries, type Country } from "../api/profile";
import OfferCard from "../components/OfferCard.vue";
import { confirm } from "../confirm";

const { t, locale } = useI18n();

const offers = ref<Offer[] | null>(null);
const loadFailed = ref(false);
const countries = ref<Country[]>([]);

// The offer whose move is in flight: its buttons are disabled meanwhile
const busy = ref<number | null>(null);
// The reason of a refused move, by offer; "company" means the profile has
// no company name yet, shown with a link to the profile
const errors = ref<Record<number, string>>({});
const needsCompany = ref<Record<number, boolean>>({});

async function load(): Promise<void> {
  loadFailed.value = false;
  try {
    offers.value = await myOffers();
  } catch {
    loadFailed.value = true;
  }
}

async function loadCountries(): Promise<void> {
  try {
    countries.value = await getCountries();
  } catch {
    // The codes show instead of the names
  }
}

// One move of the state (publish, close): the answer replaces the offer in
// the list, or its reason is kept to be shown under the card
async function move(offer: Offer, call: (id: number) => ReturnType<typeof publishOffer>): Promise<void> {
  delete errors.value[offer.id];
  delete needsCompany.value[offer.id];
  busy.value = offer.id;
  try {
    const answer = await call(offer.id);
    if (answer.status === 200 && answer.data) {
      offers.value = (offers.value ?? []).map((item) => (item.id === offer.id ? answer.data! : item));
    } else {
      // The usual refusal, a company without a name, in the language of
      // the page; any other reason as the backend words it
      const message = firstErrorOf(answer.data);
      needsCompany.value[offer.id] = /company/i.test(message);
      errors.value[offer.id] = needsCompany.value[offer.id] ? t("myOffers.needsCompany") : message || t("form.failed");
    }
  } catch {
    errors.value[offer.id] = t("form.unreachable");
  } finally {
    busy.value = null;
  }
}

async function remove(offer: Offer): Promise<void> {
  if (!(await confirm(t("myOffers.confirmDelete", { title: offer.title }), t("myOffers.delete")))) return;
  delete errors.value[offer.id];
  busy.value = offer.id;
  try {
    const answer = await deleteOffer(offer.id);
    if (answer.status === 204) {
      offers.value = (offers.value ?? []).filter((item) => item.id !== offer.id);
    } else {
      errors.value[offer.id] = t("form.failed");
    }
  } catch {
    errors.value[offer.id] = t("form.unreachable");
  } finally {
    busy.value = null;
  }
}

watch(locale, loadCountries);

onMounted(() => {
  load();
  loadCountries();
});
</script>

<template>
  <div class="head">
    <h1>{{ t("myOffers.title") }}</h1>
    <RouterLink :to="{ name: 'offerNew' }" class="primary new">{{ t("myOffers.new") }}</RouterLink>
  </div>

  <p v-if="loadFailed" class="error">{{ t("myOffers.loadFailed") }}</p>

  <template v-else-if="offers">
    <p v-if="offers.length === 0" class="muted">{{ t("myOffers.none") }}</p>
    <ul v-else class="cards">
      <li v-for="offer in offers" :key="offer.id">
        <OfferCard :offer="offer" :countries="countries" show-status>
          <!-- The applications received: a link when there are some, a
               word when none; a draft cannot have any -->
          <RouterLink
            v-if="offer.applications_count"
            :to="{ name: 'offerApplications', params: { id: offer.id } }"
            class="secondary"
          >
            {{ t("myOffers.applications", offer.applications_count) }}
          </RouterLink>
          <span v-else-if="offer.status !== 'draft'" class="none">{{ t("myOffers.applications", 0) }}</span>
          <RouterLink :to="{ name: 'offerEdit', params: { id: offer.id } }" class="secondary">
            {{ t("myOffers.edit") }}
          </RouterLink>
          <button
            v-if="offer.status !== 'published'"
            type="button"
            class="primary"
            :disabled="busy === offer.id"
            @click="move(offer, publishOffer)"
          >
            {{ offer.status === "closed" ? t("myOffers.republish") : t("myOffers.publish") }}
          </button>
          <button
            v-if="offer.status === 'published'"
            type="button"
            class="secondary"
            :disabled="busy === offer.id"
            @click="move(offer, closeOffer)"
          >
            {{ t("myOffers.close") }}
          </button>
          <button
            v-if="offer.status !== 'published' && !offer.applications_count"
            type="button"
            class="as-link danger"
            :disabled="busy === offer.id"
            @click="remove(offer)"
          >
            {{ t("myOffers.delete") }}
          </button>
          <p v-if="errors[offer.id]" class="error reason">
            {{ errors[offer.id] }}
            <RouterLink v-if="needsCompany[offer.id]" :to="{ name: 'profile' }">{{ t("myOffers.companyLink") }}</RouterLink>
          </p>
        </OfferCard>
      </li>
    </ul>
  </template>
</template>

<style scoped>
/* The title on the left, the button for a new offer on the right */
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

/* A link dressed as the main button */
.new {
  text-decoration: none;
}

.muted {
  color: var(--mt-muted);
}

.cards {
  margin: 16px 0 0;
  padding: 0;
  list-style: none;
}

.secondary {
  padding: 8px 16px;
  border: 1px solid var(--mt-border);
  border-radius: 4px;
  background: var(--mt-surface);
  color: var(--mt-text);
  font: inherit;
  text-decoration: none;
  cursor: pointer;
}

.secondary:hover {
  background: var(--mt-border);
}

.secondary:disabled {
  opacity: 0.6;
  cursor: default;
}

/* Deleting, in the colour of the errors */
.danger {
  color: var(--mt-error);
}

/* No application yet: a word in the place of the link */
.none {
  color: var(--mt-muted);
}

/* The reason of a refused move takes a whole line under the buttons */
.reason {
  flex-basis: 100%;
  margin: 0;
}

.reason a {
  margin-left: 6px;
}
</style>
