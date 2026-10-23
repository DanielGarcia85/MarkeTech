<!--
  frontend/src/components/ReviewsAside.vue

  Reviews bar — what the users think of the platform, on the right of the pages
  ───────────────────────────────────────────────────────────────────────────
  Displayed by App.vue on the right of every page but the list of the
  reviews itself, for everyone (decisions of 23.10.2026): the average
  rating with its stars and the number of reviews, the three newest
  reviews, the way to all of them and, for a candidate or an employer
  (not a demo account) whose review is not among them, the way to write
  one. Only on a wide window: below
  the width of the media query, the page keeps all the room, and the
  reviews stay one link away in the side bar. Read once, and again when
  the user changes their review (reviews.ts), or logs in or out (the
  reviews then say which one is theirs). It stays in view while the page
  scrolls, as the side bar on the left.
-->

<script setup lang="ts">
import { computed, watch } from "vue";
import { useI18n } from "vue-i18n";

import { loadLatestReviews, useLatestReviews, useReviewText } from "../reviews";
import { useSession } from "../session";
import ReviewCard from "./ReviewCard.vue";
import StarRating from "./StarRating.vue";

const { t } = useI18n();
const session = useSession();
const reviews = useLatestReviews();
const text = useReviewText();

// A candidate or an employer whose review is not among the newest: the
// way to write one (or to find theirs: the page shows it). Not a demo
// account, which may not publish one
const mayReview = computed(
  () =>
    Boolean(session.user?.role) &&
    !session.user?.is_demo &&
    !reviews.latest.some((review) => review.mine),
);

watch(() => session.user?.id, loadLatestReviews, { immediate: true });
</script>

<template>
  <aside class="reviews-aside" :aria-label="t('reviews.asideTitle')">
    <div class="inner">
      <p class="group">{{ t("reviews.asideTitle") }}</p>
      <template v-if="reviews.summary">
        <div class="score">
          <span class="average">{{ text.average(reviews.summary.averages.rating) }}</span>
          <span class="of">
            <StarRating :value="reviews.summary.averages.rating ?? 0" :size="18" />
            <span class="count">{{ t("reviews.count", reviews.summary.count) }}</span>
          </span>
        </div>
        <ul v-if="reviews.latest.length" class="latest">
          <li v-for="review in reviews.latest" :key="review.id">
            <ReviewCard :review="review" compact />
          </li>
        </ul>
        <p v-else class="none">{{ t("reviews.none") }}</p>
        <p class="links">
          <RouterLink :to="{ name: 'reviews' }">{{ t("reviews.seeAll") }}</RouterLink>
          <RouterLink v-if="mayReview" :to="{ name: 'myReview' }">{{ t("reviews.giveYours") }}</RouterLink>
        </p>
      </template>
    </div>
  </aside>
</template>

<style scoped>
/* A column as the side bar, on the other side */
.reviews-aside {
  flex: none;
  width: 300px;
  padding: 20px 16px;
  border-left: 1px solid var(--mt-border);
  background: var(--mt-surface);
}

/* In view while the page scrolls, as the side bar on the left */
.inner {
  position: sticky;
  top: calc(var(--mt-top, 64px) + 20px);
  max-height: calc(100dvh - var(--mt-top, 64px) - 40px);
  overflow-y: auto;
}

/* The title, as the groups of the side bar */
.group {
  margin: 0 0 10px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--mt-muted);
}

.score {
  display: flex;
  align-items: center;
  gap: 12px;
}

.average {
  font-size: 2.2rem;
  font-weight: 600;
  line-height: 1;
}

.of {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.count {
  color: var(--mt-muted);
  font-size: 0.85rem;
}

.latest {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 16px 0 0;
  padding: 0;
  list-style: none;
}

.none {
  color: var(--mt-muted);
}

.links {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 14px 0 0;
  font-size: 0.9rem;
}

/* Too narrow for a third column: the page keeps the room */
@media (max-width: 1439px) {
  .reviews-aside {
    display: none;
  }
}
</style>
