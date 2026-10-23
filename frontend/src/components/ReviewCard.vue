<!--
  frontend/src/components/ReviewCard.vue

  Review card — one review of the platform
  ───────────────────────────────────────────────────────────────────────────
  Used by ReviewsPage, one card per review, and by ReviewsAside, smaller.
  The stars of the overall rating and the day it was written; who wrote it
  (first name and initial, then the company of an employer or the role);
  the comment, its line breaks kept; on the page, the four detailed scores
  under it. The review of the user says so. In the bar (compact), the
  comment stops after four lines and the detailed scores are left out.
-->

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import { CRITERIA, type Review } from "../api/reviews";
import { useReviewText } from "../reviews";
import StarRating from "./StarRating.vue";

const props = defineProps<{
  review: Review;
  compact?: boolean;
}>();

const { t } = useI18n();
const text = useReviewText();

// Changed after it was written: a minute apart at least
const changed = computed(
  () => new Date(props.review.updated_at).getTime() - new Date(props.review.created_at).getTime() > 60_000,
);
</script>

<template>
  <article class="review" :class="{ compact, mine: review.mine }">
    <p class="top">
      <StarRating :value="review.rating" :size="compact ? 14 : 16" />
      <span class="day">
        {{ text.day(review.created_at) }}
        <template v-if="changed && !compact">· {{ t("reviews.changed", { date: text.day(review.updated_at) }) }}</template>
      </span>
    </p>
    <p class="author">
      <strong>{{ text.name(review) }}</strong>
      <span class="from">{{ text.from(review) }}</span>
      <span v-if="review.mine" class="yours">{{ t("reviews.yours") }}</span>
    </p>
    <p class="comment">{{ review.comment }}</p>
    <dl v-if="!compact" class="details">
      <div v-for="criterion in CRITERIA" :key="criterion">
        <dt>{{ t(`reviews.criteria.${criterion}`) }}</dt>
        <dd><StarRating :value="review[criterion]" :size="13" /></dd>
      </div>
    </dl>
  </article>
</template>

<style scoped>
.review {
  padding: 14px 18px;
  border: 1px solid var(--mt-border);
  border-radius: 10px;
  background: var(--mt-background);
}

/* One's own review: the band of the brand on the left */
.review.mine {
  border-left: 4px solid var(--mt-blue);
}

.top {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 10px;
  margin: 0;
}

.day {
  color: var(--mt-muted);
  font-size: 0.8rem;
}

.author {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 2px 8px;
  margin: 6px 0 0;
}

.from {
  color: var(--mt-muted);
  font-size: 0.9rem;
}

.yours {
  padding: 0 8px;
  border-radius: 999px;
  background: var(--mt-blue-surface);
  color: var(--mt-blue-dark);
  font-size: 0.75rem;
  font-weight: 600;
}

.comment {
  margin: 8px 0 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

/* The four scores, two by two on a wide card */
.details {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 4px 24px;
  margin: 12px 0 0;
  padding-top: 10px;
  border-top: 1px solid var(--mt-border);
}

.details div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

dt {
  color: var(--mt-muted);
  font-size: 0.85rem;
}

dd {
  margin: 0;
}

/* In the bar: tighter, the comment cut after four lines */
.compact {
  padding: 10px 12px;
}

.compact .author {
  font-size: 0.9rem;
}

.compact .from {
  font-size: 0.8rem;
}

.compact .comment {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 4;
  line-clamp: 4;
  overflow: hidden;
  font-size: 0.85rem;
  white-space: normal;
}
</style>
