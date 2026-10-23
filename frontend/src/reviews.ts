// frontend/src/reviews.ts
//
// Reviews — the latest reviews shared by the pages, and their words
// ─────────────────────────────────────────────────────────────────────────────
// The summary of all the reviews and the three newest, read once by the bar
// on the right of the pages (ReviewsAside) and read again when the user
// writes, rewrites or deletes their review, so that the bar follows at
// once. Then what the pages say about a review: who wrote it, the average
// as the language writes a number ("4,2" in French), the day.

import { reactive, readonly } from "vue";
import { useI18n } from "vue-i18n";

import { listReviews, type Review, type Summary } from "./api/reviews";

// How many reviews the bar on the right shows
const LATEST = 3;

const state = reactive({
  summary: null as Summary | null,
  latest: [] as Review[],
  failed: false,
});

// Read-only view for the components
export function useLatestReviews() {
  return readonly(state);
}

// Reads the summary and the newest reviews again; the bar stays as it was
// if the server cannot be reached
export async function loadLatestReviews(): Promise<void> {
  try {
    const page = await listReviews(1, LATEST);
    state.summary = page.summary;
    state.latest = page.results;
    state.failed = false;
  } catch {
    state.failed = true;
  }
}

// What the pages write about a review
export function useReviewText() {
  const { t, locale } = useI18n();

  return {
    // "Marc R.", or "A user" without a first name
    name(review: Review): string {
      return review.author.name ?? t("reviews.someone");
    },
    // The company of an employer, else the role ("Candidat·e")
    from(review: Review): string {
      const { role, company } = review.author;
      return role === "employer" && company ? company : t(`reviews.role.${role}`);
    },
    // "4,2" in French, "4.2" in English
    average(value: number | null): string {
      if (value === null) return "–";
      return new Intl.NumberFormat(locale.value, {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1,
      }).format(value);
    },
    // "21 oct. 2026"
    day(iso: string): string {
      return new Intl.DateTimeFormat(locale.value, {
        day: "numeric",
        month: "short",
        year: "numeric",
      }).format(new Date(iso));
    },
  };
}
