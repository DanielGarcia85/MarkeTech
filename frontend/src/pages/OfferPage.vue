<!--
  frontend/src/pages/OfferPage.vue

  Offer page — one job offer in full
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/offers/<id>", to anyone: the backend serves
  a published offer to all, and an unpublished one to its employer only;
  anything else is "not found" here, with a way back to the list. The
  company, the title, the facts in a list, then the description as it was
  typed, line breaks kept.
-->

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

import { getOffer, type Offer } from "../api/offers";
import { getCountries, type Country } from "../api/profile";
import { useOfferText } from "../offers";

const { t, locale } = useI18n();
const route = useRoute();
const text = useOfferText();

const offer = ref<Offer | null>(null);
// True once the backend has said there is no such offer for this visitor
const notFound = ref(false);
const countries = ref<Country[]>([]);

const initial = computed(() => offer.value?.company.name.trim().charAt(0).toUpperCase() || "?");

async function load(): Promise<void> {
  notFound.value = false;
  try {
    offer.value = await getOffer(Number(route.params.id));
  } catch {
    // 404 for anyone who may not see it, or no such offer: the same page
    offer.value = null;
    notFound.value = true;
  }
}

async function loadCountries(): Promise<void> {
  try {
    countries.value = await getCountries();
  } catch {
    // The code shows instead of the name
  }
}

watch(locale, loadCountries);
// From one offer to another without leaving the page (a link in a list)
watch(() => route.params.id, load);

onMounted(() => {
  load();
  loadCountries();
});
</script>

<template>
  <p class="back">
    <RouterLink :to="{ name: 'offers' }">← {{ t("offers.back") }}</RouterLink>
  </p>

  <p v-if="notFound" class="notice">{{ t("offers.notFound") }}</p>

  <article v-else-if="offer" class="offer">
    <header class="head">
      <div class="logo-box">
        <img v-if="offer.company.logo" :src="offer.company.logo" alt="" class="logo" />
        <span v-else class="logo-empty" aria-hidden="true">{{ initial }}</span>
      </div>
      <div>
        <p class="company">{{ offer.company.name }}</p>
        <h1 class="title">{{ offer.title }}</h1>
        <p class="date">{{ t("offers.publishedOn", { date: text.published(offer) }) }}</p>
      </div>
    </header>

    <!-- The facts, as a list of terms and values -->
    <section class="section">
      <h2>{{ t("offers.facts") }}</h2>
      <dl class="facts">
        <dt>{{ t("offers.place") }}</dt>
        <dd>{{ text.place(offer, countries) }}</dd>
        <dt>{{ t("offers.contractLabel") }}</dt>
        <dd>{{ text.conditions(offer) }}</dd>
        <template v-if="text.salary(offer)">
          <dt>{{ t("offers.salaryLabel") }}</dt>
          <dd>{{ text.salary(offer) }}</dd>
        </template>
        <template v-if="text.experience(offer)">
          <dt>{{ t("offers.experienceLabel") }}</dt>
          <dd>{{ text.experience(offer) }}</dd>
        </template>
      </dl>
    </section>

    <section class="section">
      <h2>{{ t("offers.description") }}</h2>
      <p class="description">{{ offer.description }}</p>
    </section>
  </article>
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

/* The logo on the left, the company, the title and the date on the right */
.head {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.logo-box {
  flex: 0 0 96px;
}

.logo,
.logo-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 96px;
  height: 96px;
  border: 1px solid var(--mt-border);
  border-radius: 8px;
  background: var(--mt-background);
}

.logo {
  padding: 8px;
  object-fit: contain;
}

.logo-empty {
  background: var(--mt-surface);
  color: var(--mt-muted);
  font-size: 2rem;
  font-weight: 600;
}

.company {
  margin: 0;
  color: var(--mt-muted);
}

.title {
  margin: 2px 0 6px;
  font-size: 1.6rem;
}

.date {
  margin: 0;
  color: var(--mt-muted);
  font-size: 0.9rem;
}

/* The sections, separated by a rule, as on the profile page */
.section {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--mt-border);
}

.section h2 {
  margin: 0 0 12px;
  color: var(--mt-blue);
  font-size: 1.2rem;
}

/* Terms on the left, values on the right */
.facts {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 6px 24px;
  margin: 0;
}

.facts dt {
  font-weight: 600;
}

.facts dd {
  margin: 0;
}

/* The description as typed: paragraphs and line breaks kept */
.description {
  margin: 0;
  max-width: 760px;
  white-space: pre-wrap;
}
</style>
