<!--
  frontend/src/components/StarRating.vue

  Star rating — a score from 0 to 5, drawn as five stars
  ───────────────────────────────────────────────────────────────────────────
  Used by the reviews to show a score: the stars of a review (whole ones)
  and the averages (4.2 fills four stars and a fifth of the last). Two
  rows of the same five stars, one over the other: the grey row below,
  the row of the accent above, cut at the width of the score. Read aloud
  as "4.2 out of 5": the drawing is hidden from screen readers.
-->

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const props = withDefaults(
  defineProps<{
    value: number;
    // The side of one star, in pixels
    size?: number;
  }>(),
  { size: 16 },
);

const { t, locale } = useI18n();

// The part of the row of the accent that shows, from 0 to 100 %
const filled = computed(() => `${(Math.max(0, Math.min(5, props.value)) / 5) * 100}%`);

const label = computed(() =>
  t("reviews.outOfFive", {
    value: new Intl.NumberFormat(locale.value, { maximumFractionDigits: 1 }).format(props.value),
  }),
);

// One star of the side asked, its five points on a 24 × 24 grid
const STAR = "M12 2.5l2.9 5.9 6.5.9-4.7 4.6 1.1 6.5L12 17.3l-5.8 3.1 1.1-6.5-4.7-4.6 6.5-.9z";
</script>

<template>
  <span class="stars" role="img" :aria-label="label">
    <span class="layer empty" aria-hidden="true">
      <svg v-for="n in 5" :key="n" :width="size" :height="size" viewBox="0 0 24 24"><path :d="STAR" /></svg>
    </span>
    <span class="layer full" :style="{ width: filled }" aria-hidden="true">
      <svg v-for="n in 5" :key="n" :width="size" :height="size" viewBox="0 0 24 24"><path :d="STAR" /></svg>
    </span>
  </span>
</template>

<style scoped>
/* The two rows stacked: the one of the accent over the grey one */
.stars {
  position: relative;
  display: inline-block;
  line-height: 0;
  vertical-align: -2px;
}

.layer {
  display: inline-flex;
  gap: 2px;
  white-space: nowrap;
}

.empty {
  color: var(--mt-border);
}

/* Cut at the width of the score */
.full {
  position: absolute;
  top: 0;
  left: 0;
  overflow: hidden;
  color: var(--mt-accent);
}

svg {
  flex: none;
  fill: currentColor;
}
</style>
