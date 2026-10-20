<!--
  frontend/src/components/OfferCard.vue

  Offer card — one job offer in a list
  ───────────────────────────────────────────────────────────────────────────
  Used by the public list, and later by the list of an employer. The logo
  of the company (or its initial), the company, the title as a link to the
  page of the offer, the place and the conditions, the salary when given,
  the date of publication.
-->

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import type { Offer } from "../api/offers";
import type { Country } from "../api/profile";
import { useOfferText } from "../offers";

const props = defineProps<{
  offer: Offer;
  // The countries, to write the name of the country of the offer
  countries: Country[];
}>();

const { t } = useI18n();
const text = useOfferText();

// Without a logo, the first letter of the company in a square
const initial = computed(() => props.offer.company.name.trim().charAt(0).toUpperCase() || "?");
</script>

<template>
  <article class="card">
    <div class="logo-box">
      <img v-if="offer.company.logo" :src="offer.company.logo" alt="" class="logo" />
      <span v-else class="logo-empty" aria-hidden="true">{{ initial }}</span>
    </div>
    <div class="body">
      <p class="company">{{ offer.company.name }}</p>
      <h2 class="title">
        <RouterLink :to="{ name: 'offer', params: { id: offer.id } }">{{ offer.title }}</RouterLink>
      </h2>
      <p class="line">{{ text.place(offer, countries) }} · {{ text.conditions(offer) }}</p>
      <p v-if="text.salary(offer)" class="line">{{ text.salary(offer) }}</p>
      <p class="date">{{ t("offers.publishedOn", { date: text.published(offer) }) }}</p>
    </div>
  </article>
</template>

<style scoped>
/* The logo on the left, the text on the right, a rule under each card */
.card {
  display: flex;
  gap: 20px;
  padding: 20px 0;
  border-bottom: 1px solid var(--mt-border);
}

.logo-box {
  flex: 0 0 72px;
}

/* The logo in a square, kept whole, like on the profile page */
.logo,
.logo-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border: 1px solid var(--mt-border);
  border-radius: 8px;
  background: var(--mt-background);
}

.logo {
  padding: 6px;
  object-fit: contain;
}

.logo-empty {
  background: var(--mt-surface);
  color: var(--mt-muted);
  font-size: 1.5rem;
  font-weight: 600;
}

.body {
  min-width: 0;
}

.company {
  margin: 0;
  color: var(--mt-muted);
  font-size: 0.9rem;
}

.title {
  margin: 2px 0 6px;
  font-size: 1.15rem;
}

.title a {
  text-decoration: none;
}

.title a:hover {
  text-decoration: underline;
}

.line {
  margin: 0 0 2px;
}

.date {
  margin: 6px 0 0;
  color: var(--mt-muted);
  font-size: 0.85rem;
}
</style>
