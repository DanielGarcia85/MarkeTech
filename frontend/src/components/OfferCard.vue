<!--
  frontend/src/components/OfferCard.vue

  Offer card — one job offer in a list
  ───────────────────────────────────────────────────────────────────────────
  Used by the public list, by the favorites of a candidate and by the list
  of an employer. A white box with soft corners, lifted a little under the
  pointer: the mark of the company (CompanyMark: its logo, or its initial
  on a colour), the company, the title as a link to the page of the offer,
  the place, the contract, workload and remote work as tags (OfferTags),
  the salary when given, the date of publication; on the right, the heart
  (FavoriteButton), which tells the parent when the offer is put aside or
  taken back. The list of an employer asks for the state of the offer as a
  pill (a closed offer shows it anyway: it may sit among the favorites),
  and puts its buttons in the slot under the text.
-->

<script setup lang="ts">
import { useI18n } from "vue-i18n";

import type { Offer } from "../api/offers";
import type { Country } from "../api/profile";
import { useOfferText } from "../offers";
import CompanyMark from "./CompanyMark.vue";
import FavoriteButton from "./FavoriteButton.vue";
import OfferTags from "./OfferTags.vue";

defineProps<{
  offer: Offer;
  // The countries, to write the name of the country of the offer
  countries: Country[];
  // Show the state (draft, published, closed): the employer's list only
  showStatus?: boolean;
}>();

// The offer was put aside or taken back: the parent updates its copy
defineEmits<{ favorite: [favorite: boolean] }>();

const { t } = useI18n();
const text = useOfferText();
</script>

<template>
  <article class="card">
    <CompanyMark :name="offer.company.name" :logo="offer.company.logo" :size="72" />
    <div class="body">
      <p class="company">
        {{ offer.company.name }}
        <span v-if="showStatus || offer.status === 'closed'" class="pill" :class="offer.status">
          {{ t("offers.status." + offer.status) }}
        </span>
      </p>
      <h2 class="title">
        <RouterLink :to="{ name: 'offer', params: { id: offer.id } }">{{ offer.title }}</RouterLink>
      </h2>
      <p class="line">{{ text.place(offer, countries) }}</p>
      <p class="line"><OfferTags :offer="offer" /></p>
      <p v-if="text.salary(offer)" class="line salary">{{ text.salary(offer) }}</p>
      <p v-if="offer.published_at" class="date">{{ t("offers.publishedOn", { date: text.published(offer) }) }}</p>
      <!-- The buttons of the employer's list, when there are some -->
      <div v-if="$slots.default" class="actions"><slot /></div>
    </div>
    <!-- The heart: a candidate's, or a visitor's way to the login page -->
    <div class="aside">
      <FavoriteButton :offer="offer" @change="$emit('favorite', $event)" />
    </div>
  </article>
</template>

<style scoped>
/* The mark on the left, the text on the right, in a box; the box comes
   forward a little under the pointer */
.card {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
  padding: 18px 20px;
  border: 1px solid var(--mt-border);
  border-radius: 12px;
  background: var(--mt-background);
  transition:
    box-shadow 0.15s ease,
    border-color 0.15s ease;
}

.card:hover {
  border-color: var(--mt-blue-border);
  box-shadow: 0 6px 18px rgba(31, 80, 106, 0.1);
}

.body {
  flex: 1;
  min-width: 0;
}

.aside {
  flex: none;
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
  margin: 0 0 4px;
}

.salary {
  font-weight: 500;
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
