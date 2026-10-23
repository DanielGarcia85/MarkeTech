<!--
  frontend/src/pages/MyReviewPage.vue

  My review page — the review of the logged-in user, to write, change or delete
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/review", to a logged-in user. A candidate
  or an employer gives the overall rating, the four detailed scores (stars
  as radio buttons, StarInput) and a comment of 1000 characters at most,
  the count shown as they type; the page says how the review will be
  signed in public (first name and initial, the company of an employer).
  The review written, the same form changes it, and a button deletes it,
  after a confirmation. A demo account sees its review in the form,
  disabled: the reviews are public, and the server refuses the changes
  anyway (reviews/views.py). An administrator, who has no role, has no
  review. The bar on the right follows each change (reviews.ts).
-->

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import { firstErrors } from "../api/http";
import { CRITERIA, deleteMyReview, getMyReview, saveMyReview, type ReviewForm } from "../api/reviews";
import StarInput from "../components/StarInput.vue";
import { confirm } from "../confirm";
import { loadLatestReviews } from "../reviews";
import { useSession } from "../session";

// The longest comment the server accepts (reviews/models.py)
const MAX_LENGTH = 1000;

const { t } = useI18n();
const session = useSession();

const form = reactive<ReviewForm>({
  rating: 0,
  ease_of_use: 0,
  offers_and_applications: 0,
  messaging: 0,
  appointments: 0,
  comment: "",
});
// Whether the review exists on the server; null until read
const written = ref<boolean | null>(null);
const loadFailed = ref(false);
const sending = ref(false);
const errors = ref<Record<string, string>>({});
// The confirmation in a green pill, a new id each time so that it shows again
const badge = ref<{ text: string; id: number } | null>(null);
let badgeId = 0;
let badgeTimer = 0;

const locked = computed(() => session.user?.is_demo === true);
// How the review is signed in public: depends on the role
const signature = computed(() =>
  t(session.user?.role === "employer" ? "reviews.signedEmployer" : "reviews.signedCandidate"),
);

function showBadge(text: string): void {
  badge.value = { text, id: ++badgeId };
  window.clearTimeout(badgeTimer);
  badgeTimer = window.setTimeout(() => (badge.value = null), 3000);
}

async function load(): Promise<void> {
  written.value = null;
  loadFailed.value = false;
  if (!session.user?.role) return;
  try {
    const review = await getMyReview();
    if (review) {
      form.rating = review.rating;
      for (const criterion of CRITERIA) form[criterion] = review[criterion];
      form.comment = review.comment;
    }
    written.value = review !== null;
  } catch {
    loadFailed.value = true;
  }
}

async function save(): Promise<void> {
  sending.value = true;
  errors.value = {};
  try {
    const answer = await saveMyReview({ ...form });
    if (answer.status === 200 || answer.status === 201) {
      showBadge(t(answer.status === 201 ? "reviews.published" : "reviews.saved"));
      written.value = true;
      form.comment = answer.data?.comment ?? form.comment;
      await loadLatestReviews();
    } else {
      errors.value = firstErrors(answer.data as Record<string, string[]> | null);
      if (!Object.keys(errors.value).length) errors.value = { "": t("form.failed") };
    }
  } catch {
    errors.value = { "": t("form.failed") };
  } finally {
    sending.value = false;
  }
}

async function remove(): Promise<void> {
  if (!(await confirm(t("reviews.confirmDelete"), t("reviews.delete")))) return;
  sending.value = true;
  errors.value = {};
  try {
    const answer = await deleteMyReview();
    if (answer.status === 204 || answer.status === 404) {
      Object.assign(form, { rating: 0, ease_of_use: 0, offers_and_applications: 0, messaging: 0, appointments: 0, comment: "" });
      written.value = false;
      showBadge(t("reviews.deleted"));
      await loadLatestReviews();
    } else {
      errors.value = firstErrors(answer.data as Record<string, string[]> | null);
    }
  } catch {
    errors.value = { "": t("form.failed") };
  } finally {
    sending.value = false;
  }
}

watch(() => session.user?.id, load, { immediate: true });
</script>

<template>
  <h1>{{ t("reviews.mineTitle") }}</h1>

  <p v-if="session.user && !session.user.role" class="notice">{{ t("reviews.noRole") }}</p>

  <template v-else-if="session.user">
    <p class="intro">{{ t("reviews.mineIntro") }}</p>
    <p v-if="locked" class="notice">{{ t("reviews.demoLocked") }}</p>
    <p v-if="loadFailed" class="error">{{ t("reviews.loadFailed") }}</p>

    <form v-else-if="written !== null" novalidate class="review-form" @submit.prevent="save">
      <fieldset :disabled="locked || sending">
        <p v-if="errors['']" class="error">{{ errors[""] }}</p>

        <StarInput v-model="form.rating" name="rating" large :legend="t('reviews.overall')" :error="errors.rating" />

        <div class="criteria">
          <StarInput
            v-for="criterion in CRITERIA"
            :key="criterion"
            v-model="form[criterion]"
            :name="criterion"
            :legend="t(`reviews.criteria.${criterion}`)"
            :error="errors[criterion]"
          />
        </div>

        <div class="field">
          <label for="review-comment">{{ t("reviews.comment") }}</label>
          <textarea
            id="review-comment"
            v-model="form.comment"
            rows="6"
            :maxlength="MAX_LENGTH"
            :placeholder="t('reviews.commentHint')"
          />
          <p class="length">{{ t("reviews.length", { count: form.comment.length, max: MAX_LENGTH }) }}</p>
          <p v-if="errors.comment" class="error">{{ errors.comment }}</p>
        </div>

        <p class="signature">{{ signature }}</p>

        <div class="actions">
          <button type="submit" class="primary">
            {{ written ? t("reviews.save") : t("reviews.publish") }}
          </button>
          <button v-if="written" type="button" class="danger" @click="remove">{{ t("reviews.delete") }}</button>
          <span v-if="badge" :key="badge.id" class="badge">{{ badge.text }}</span>
        </div>
      </fieldset>
    </form>

    <p class="all">
      <RouterLink :to="{ name: 'reviews' }">{{ t("reviews.seeAll") }}</RouterLink>
    </p>
  </template>
</template>

<style scoped>
/* The words above the form, as wide as the form */
.intro,
.notice {
  max-width: 760px;
}

.intro {
  margin-top: 0;
  color: var(--mt-muted);
}

.review-form {
  max-width: 760px;
  margin-top: 20px;
}

/* The frame that disables the whole form at once */
fieldset {
  margin: 0;
  padding: 0;
  border: none;
}

/* The four scores, two by two while the width allows */
.criteria {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px 32px;
  margin: 24px 0;
  padding: 20px 0;
  border-top: 1px solid var(--mt-border);
  border-bottom: 1px solid var(--mt-border);
}

textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--mt-border);
  border-radius: 6px;
  background: var(--mt-background);
  color: var(--mt-text);
  font: inherit;
  resize: vertical;
}

fieldset:disabled textarea {
  background: var(--mt-surface);
  cursor: not-allowed;
}

.length {
  margin: 4px 0 0;
  color: var(--mt-muted);
  font-size: 0.8rem;
  text-align: right;
}

.signature {
  color: var(--mt-muted);
  font-size: 0.9rem;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}

/* Deleting: outlined in red, apart from the main button */
.danger {
  padding: 8px 16px;
  border: 1px solid var(--mt-error);
  border-radius: 6px;
  background: var(--mt-background);
  color: var(--mt-error);
  font: inherit;
  cursor: pointer;
}

.danger:disabled {
  opacity: 0.6;
  cursor: default;
}

.all {
  margin-top: 24px;
}

/* A confirmation: a check mark and a few words in a green pill, faded
   away over its last second, as on the profile */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--mt-success-surface);
  color: var(--mt-success);
  font-size: 0.9rem;
  animation: badge 3s ease forwards;
}

.badge::before {
  content: "✓";
  font-weight: 600;
}

@keyframes badge {
  0% {
    opacity: 0;
    transform: translateY(4px);
  }
  10% {
    opacity: 1;
    transform: none;
  }
  70% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}
</style>
