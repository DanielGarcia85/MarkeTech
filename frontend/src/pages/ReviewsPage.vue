<!--
  frontend/src/pages/ReviewsPage.vue

  Reviews page — every review of the platform, for anyone
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/reviews", to everyone, logged in or not.
  At the top, the summary of all the reviews: the average rating with its
  stars and their number, how many gave each rating (a bar per rating),
  the average of each of the four detailed scores. Then the reviews,
  newest first, ten at a time, with a button for ten more. A candidate or
  an employer finds the way to write theirs, or to change it.
-->

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import { CRITERIA, getMyReview, listReviews, type Review, type Summary } from "../api/reviews";
import EmptyState from "../components/EmptyState.vue";
import ReviewCard from "../components/ReviewCard.vue";
import StarRating from "../components/StarRating.vue";
import { useReviewText } from "../reviews";
import { useSession } from "../session";

const { t } = useI18n();
const session = useSession();
const text = useReviewText();

const summary = ref<Summary | null>(null);
const reviews = ref<Review[]>([]);
const page = ref(0);
const more = ref(false);
const loading = ref(false);
const loadFailed = ref(false);

// The next ten; the summary comes with every page
async function loadMore(): Promise<void> {
  loading.value = true;
  loadFailed.value = false;
  try {
    const answer = await listReviews(page.value + 1);
    page.value += 1;
    summary.value = answer.summary;
    reviews.value = [...reviews.value, ...answer.results];
    more.value = answer.next !== null;
  } catch {
    loadFailed.value = true;
  } finally {
    loading.value = false;
  }
}

// The share of each rating, for the width of its bar
function share(rating: number): string {
  const count = summary.value?.count ?? 0;
  return count ? `${((summary.value?.ratings[rating] ?? 0) / count) * 100}%` : "0%";
}

// Whether the user wrote theirs already: the button then says "change"
const hasMine = ref(false);

async function loadMine(): Promise<void> {
  hasMine.value = false;
  if (!session.user?.role) return;
  try {
    hasMine.value = (await getMyReview()) !== null;
  } catch {
    // The button keeps its first words
  }
}

watch(() => session.user?.id, loadMine, { immediate: true });

onMounted(loadMore);
</script>

<template>
  <h1>{{ t("reviews.title") }}</h1>
  <p class="intro">{{ t("reviews.intro") }}</p>

  <p v-if="loadFailed && !summary" class="error">{{ t("reviews.loadFailed") }}</p>

  <template v-if="summary">
    <section v-if="summary.count" class="summary" :aria-label="t('reviews.summary')">
      <div class="overall">
        <span class="average">{{ text.average(summary.averages.rating) }}</span>
        <StarRating :value="summary.averages.rating ?? 0" :size="22" />
        <span class="count">{{ t("reviews.count", summary.count) }}</span>
      </div>
      <ul class="ratings">
        <li v-for="rating in [5, 4, 3, 2, 1]" :key="rating">
          <span class="label">{{ t("reviews.stars", rating) }}</span>
          <span class="bar"><span :style="{ width: share(rating) }" /></span>
          <span class="number">{{ summary.ratings[rating] ?? 0 }}</span>
        </li>
      </ul>
      <dl class="criteria">
        <div v-for="criterion in CRITERIA" :key="criterion">
          <dt>{{ t(`reviews.criteria.${criterion}`) }}</dt>
          <dd>
            <StarRating :value="summary.averages[criterion] ?? 0" :size="14" />
            <span class="value">{{ text.average(summary.averages[criterion]) }}</span>
          </dd>
        </div>
      </dl>
    </section>

    <p v-if="session.user?.role" class="write">
      <RouterLink :to="{ name: 'myReview' }" class="primary">
        {{ hasMine ? t("reviews.changeYours") : t("reviews.giveYours") }}
      </RouterLink>
    </p>

    <EmptyState v-if="!reviews.length" icon="star" :text="t('reviews.none')" />
    <ul v-else class="list">
      <li v-for="review in reviews" :key="review.id">
        <ReviewCard :review="review" />
      </li>
    </ul>

    <p v-if="loadFailed" class="error">{{ t("reviews.loadFailed") }}</p>
    <p v-if="more" class="more">
      <button type="button" class="secondary" :disabled="loading" @click="loadMore">
        {{ t("reviews.more") }}
      </button>
    </p>
  </template>
</template>

<style scoped>
.intro {
  margin-top: 0;
  color: var(--mt-muted);
}

/* The summary: the average, the bars of the ratings, the four scores, side
   by side while the width allows */
.summary {
  display: grid;
  grid-template-columns: auto minmax(220px, 1fr) minmax(280px, 1.2fr);
  gap: 24px 40px;
  align-items: center;
  margin: 20px 0;
  padding: 20px 24px;
  border: 1px solid var(--mt-border);
  border-radius: 12px;
  background: var(--mt-surface);
}

.overall {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.average {
  font-size: 3rem;
  font-weight: 600;
  line-height: 1;
}

.count {
  color: var(--mt-muted);
  font-size: 0.9rem;
}

.ratings {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.ratings li {
  display: grid;
  grid-template-columns: 76px 1fr 24px;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
}

.ratings .label,
.ratings .number {
  color: var(--mt-muted);
}

.ratings .number {
  text-align: right;
}

/* A bar per rating: its share of the reviews in the accent */
.bar {
  height: 8px;
  border-radius: 999px;
  background: var(--mt-border);
  overflow: hidden;
}

.bar span {
  display: block;
  height: 100%;
  background: var(--mt-accent);
}

.criteria {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 0;
}

.criteria div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

dt {
  font-size: 0.9rem;
}

dd {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.value {
  min-width: 2em;
  color: var(--mt-muted);
  font-size: 0.85rem;
  text-align: right;
}

.write {
  margin: 0 0 16px;
}

.write .primary {
  display: inline-block;
  text-decoration: none;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.more {
  margin: 20px 0 0;
  text-align: center;
}

.secondary {
  padding: 8px 16px;
  border: 1px solid var(--mt-border);
  border-radius: 6px;
  background: var(--mt-background);
  color: var(--mt-text);
  font: inherit;
  cursor: pointer;
}

.secondary:hover {
  background: var(--mt-border);
}

/* Narrower: the parts of the summary one under the other */
@media (max-width: 1100px) {
  .summary {
    grid-template-columns: 1fr;
    justify-items: stretch;
  }
}
</style>
