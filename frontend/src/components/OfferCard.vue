<!--
  frontend/src/components/OfferCard.vue

  Offer card — one job offer in a list
  ───────────────────────────────────────────────────────────────────────────
  Used by the public list and by the list of an employer. The logo of the
  company (or its initial), the company, the title as a link to the page of
  the offer, the place and the conditions, the salary when given, the date
  of publication. The list of an employer asks for the state of the offer
  as a pill, and puts its buttons in the slot under the text.
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
  // Show the state (draft, published, closed): the employer's list only
  showStatus?: boolean;
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
      <p class="company">
        {{ offer.company.name }}
        <span v-if="showStatus" class="pill" :class="offer.status">{{ t("offers.status." + offer.status) }}</span>
      </p>
      <h2 class="title">
        <RouterLink :to="{ name: 'offer', params: { id: offer.id } }">{{ offer.title }}</RouterLink>
      </h2>
      <p class="line">{{ text.place(offer, countries) }} · {{ text.conditions(offer) }}</p>
      <p v-if="text.salary(offer)" class="line">{{ text.salary(offer) }}</p>
      <p v-if="offer.published_at" class="date">{{ t("offers.publishedOn", { date: text.published(offer) }) }}</p>
      <!-- The buttons of the employer's list, when there are some -->
      <div v-if="$slots.default" class="actions"><slot /></div>
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
  flex: 1;
  min-width: 0;
}

.company {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  color: var(--mt-muted);
  font-size: 0.9rem;
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

/* The buttons, side by side, under the text of the card */
.actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 16px;
  margin-top: 12px;
}
</style>
