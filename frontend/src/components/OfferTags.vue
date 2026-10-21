<!--
  frontend/src/components/OfferTags.vue

  Offer tags — the contract, the workload and the remote work as labels
  ───────────────────────────────────────────────────────────────────────────
  Used by the offer cards and by the facts of the page of an offer. Small
  rounded labels side by side: the contract in a colour of its own (a
  permanent position in blue, a fixed term in grey, an internship in
  green, a student job in amber), then the workload when the offer gives
  one, then the remote work, both in grey. The words are those of the
  translations and of useOfferText, so that the lists and the page say
  the same.
-->

<script setup lang="ts">
import { useI18n } from "vue-i18n";

import type { Offer } from "../api/offers";
import { useOfferText } from "../offers";

defineProps<{ offer: Offer }>();

const { t } = useI18n();
const text = useOfferText();
</script>

<template>
  <span class="tags">
    <span class="tag" :class="offer.contract">{{ t("offers.contract." + offer.contract) }}</span>
    <span v-if="text.workload(offer)" class="tag">{{ text.workload(offer) }}</span>
    <span class="tag">{{ t("offers.remote." + offer.remote) }}</span>
  </span>
</template>

<style scoped>
.tags {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px;
  vertical-align: middle;
}

/* A label: grey by default, the contract in its colour */
.tag {
  display: inline-block;
  padding: 2px 10px;
  border: 1px solid var(--mt-border);
  border-radius: 999px;
  background: var(--mt-surface);
  color: var(--mt-text);
  font-size: 0.8rem;
  font-weight: 500;
  line-height: 1.4;
  white-space: nowrap;
}

.tag.permanent {
  border-color: var(--mt-blue-border);
  background: var(--mt-blue-surface);
  color: var(--mt-blue-dark);
}

.tag.fixed_term {
  border-color: var(--mt-border);
  background: var(--mt-border);
  color: var(--mt-text);
}

.tag.internship {
  border-color: var(--mt-success-surface);
  background: var(--mt-success-surface);
  color: var(--mt-success);
}

.tag.student {
  border-color: var(--mt-accent-surface);
  background: var(--mt-accent-surface);
  color: var(--mt-accent-dark);
}
</style>
