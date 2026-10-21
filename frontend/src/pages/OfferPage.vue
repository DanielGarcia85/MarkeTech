<!--
  frontend/src/pages/OfferPage.vue

  Offer page — one job offer in full
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/offers/<id>", to anyone: the backend serves
  a published offer to all, and an unpublished one to its employer only;
  anything else is "not found" here, with a way back to the list. The
  company, the title, the facts in a list, then the description as it was
  typed, line breaks kept. Under the heading, the way to apply: a button
  for a candidate, an invitation to log in for a visitor, and, once
  applied, the date and the state of the application sent. For the
  employer of the offer: its state, its numbers of applications and of
  favorites, and the way to its form and to its applications. In the
  heading, on the right, the heart that puts the offer aside
  (FavoriteButton).
-->

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

import { listApplications, type Application } from "../api/applications";
import { getOffer, type Offer } from "../api/offers";
import { getCountries, type Country } from "../api/profile";
import { useApplicationText } from "../applications";
import FavoriteButton from "../components/FavoriteButton.vue";
import { useOfferText } from "../offers";
import { useSession, whenLoaded } from "../session";

const { t, locale } = useI18n();
const route = useRoute();
const text = useOfferText();
const applicationText = useApplicationText();
const session = useSession();

const offer = ref<Offer | null>(null);
// True once the backend has said there is no such offer for this visitor
const notFound = ref(false);
const countries = ref<Country[]>([]);
// The application of the logged-in candidate to this offer, if any
const myApplication = ref<Application | null>(null);

const isCandidate = computed(() => session.user?.role === "candidate");

const initial = computed(() => offer.value?.company.name.trim().charAt(0).toUpperCase() || "?");

async function load(): Promise<void> {
  notFound.value = false;
  myApplication.value = null;
  try {
    offer.value = await getOffer(Number(route.params.id));
  } catch {
    // 404 for anyone who may not see it, or no such offer: the same page
    offer.value = null;
    notFound.value = true;
    return;
  }
  // A candidate: has the offer been applied to already?
  await whenLoaded();
  if (!isCandidate.value) return;
  try {
    myApplication.value = (await listApplications({ offer: offer.value.id }))[0] ?? null;
  } catch {
    // The button shows; the backend would refuse a second application
  }
}

async function loadCountries(): Promise<void> {
  try {
    countries.value = await getCountries();
  } catch {
    // The code shows instead of the name
  }
}

watch(locale, loadCountries);
// From one offer to another without leaving the page (a link in a list)
watch(() => route.params.id, load);

onMounted(() => {
  load();
  loadCountries();
});
</script>

<template>
  <p class="back">
    <RouterLink :to="{ name: 'home' }">← {{ t("offers.back") }}</RouterLink>
  </p>

  <p v-if="notFound" class="notice">{{ t("offers.notFound") }}</p>

  <article v-else-if="offer" class="offer">
    <header class="head">
      <div class="logo-box">
        <img v-if="offer.company.logo" :src="offer.company.logo" alt="" class="logo" />
        <span v-else class="logo-empty" aria-hidden="true">{{ initial }}</span>
      </div>
      <div class="heading">
        <p class="company">{{ offer.company.name }}</p>
        <h1 class="title">{{ offer.title }}</h1>
        <p class="date">{{ t("offers.publishedOn", { date: text.published(offer) }) }}</p>
      </div>
      <!-- The heart, for a published offer: a candidate's, or a visitor's
           way to the login page; nothing for an employer -->
      <FavoriteButton
        v-if="offer.status === 'published'"
        :offer="offer"
        @change="offer.favorite = $event"
      />
    </header>

    <!-- The employer of the offer: its state, its form, its applications -->
    <div v-if="offer.mine" class="apply mine">
      <p>
        {{ t("offers.yours") }}
        <span class="pill" :class="offer.status">{{ t("offers.status." + offer.status) }}</span>
      </p>
      <RouterLink :to="{ name: 'offerEdit', params: { id: offer.id } }" class="secondary">
        {{ t("offers.editLink") }}
      </RouterLink>
      <RouterLink
        v-if="offer.status !== 'draft'"
        :to="{ name: 'offerApplications', params: { id: offer.id } }"
        class="secondary"
      >
        {{ t("myOffers.applications", offer.applications_count ?? 0) }}
      </RouterLink>
      <span v-if="offer.status !== 'draft'" class="muted">{{ t("myOffers.favorites", offer.favorites_count ?? 0) }}</span>
    </div>
    <!-- Applying: the application sent, or the button, or the invitation
         to log in; nothing for an employer, nor once the offer is closed -->
    <div v-else-if="myApplication" class="apply applied">
      <p>
        {{ t("offers.applied", { date: applicationText.date(myApplication.created_at) }) }}
        <span class="pill" :class="myApplication.status">{{ applicationText.status(myApplication.status) }}</span>
      </p>
      <RouterLink :to="{ name: 'myApplications' }">{{ t("offers.myApplicationsLink") }}</RouterLink>
    </div>
    <div v-else-if="offer.status === 'published' && isCandidate" class="apply">
      <RouterLink :to="{ name: 'apply', params: { id: offer.id } }" class="primary button">{{ t("offers.apply") }}</RouterLink>
    </div>
    <p v-else-if="offer.status === 'published' && !session.user" class="apply">
      <i18n-t keypath="offers.loginToApply" tag="span">
        <template #login>
          <RouterLink :to="{ name: 'login', query: { next: route.fullPath } }">{{ t("offers.loginLink") }}</RouterLink>
        </template>
      </i18n-t>
    </p>

    <!-- The facts, as a list of terms and values -->
    <section class="section">
      <h2>{{ t("offers.facts") }}</h2>
      <dl class="facts">
        <dt>{{ t("offers.place") }}</dt>
        <dd>{{ text.place(offer, countries) }}</dd>
        <dt>{{ t("offers.contractLabel") }}</dt>
        <dd>{{ text.conditions(offer) }}</dd>
        <template v-if="text.salary(offer)">
          <dt>{{ t("offers.salaryLabel") }}</dt>
          <dd>{{ text.salary(offer) }}</dd>
        </template>
        <template v-if="text.experience(offer)">
          <dt>{{ t("offers.experienceLabel") }}</dt>
          <dd>{{ text.experience(offer) }}</dd>
        </template>
      </dl>
    </section>

    <section class="section">
      <h2>{{ t("offers.description") }}</h2>
      <p class="description">{{ offer.description }}</p>
    </section>
  </article>
</template>

<style scoped>
.back {
  margin: 0 0 16px;
}

.back a {
  text-decoration: none;
}

.back a:hover {
  text-decoration: underline;
}

/* The logo on the left, the company, the title and the date on the right */
.head {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

/* The company, the title and the date take the room; the heart stays on
   the right */
.heading {
  flex: 1;
  min-width: 0;
}

.muted {
  color: var(--mt-muted);
}

.logo-box {
  flex: 0 0 96px;
}

.logo,
.logo-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 96px;
  height: 96px;
  border: 1px solid var(--mt-border);
  border-radius: 8px;
  background: var(--mt-background);
}

.logo {
  padding: 8px;
  object-fit: contain;
}

.logo-empty {
  background: var(--mt-surface);
  color: var(--mt-muted);
  font-size: 2rem;
  font-weight: 600;
}

.company {
  margin: 0;
  color: var(--mt-muted);
}

.title {
  margin: 2px 0 6px;
  font-size: 1.6rem;
}

.date {
  margin: 0;
  color: var(--mt-muted);
  font-size: 0.9rem;
}

/* The way to apply, under the heading */
.apply {
  margin: 20px 0 0;
}

.apply .button {
  display: inline-block;
  text-decoration: none;
}

/* The application sent, or the employer's own offer: a line and links in
   a box */
.applied,
.mine {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 16px;
  padding: 12px 16px;
  border: 1px solid var(--mt-border);
  border-radius: 4px;
  background: var(--mt-surface);
}

.applied p,
.mine p {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

.secondary {
  padding: 8px 16px;
  border: 1px solid var(--mt-border);
  border-radius: 4px;
  background: var(--mt-background);
  color: var(--mt-text);
  text-decoration: none;
}

.secondary:hover {
  background: var(--mt-border);
}

.pill {
  display: inline-block;
  padding: 1px 10px;
  border: 1px solid var(--mt-border);
  border-radius: 999px;
  background: var(--mt-background);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.pill.in_progress {
  border-color: var(--mt-blue);
  color: var(--mt-blue);
}

.pill.published,
.pill.accepted {
  border-color: var(--mt-success-surface);
  background: var(--mt-success-surface);
  color: var(--mt-success);
}

.pill.rejected {
  border-color: var(--mt-error);
  color: var(--mt-error);
}

.pill.closed {
  background: var(--mt-border);
  color: var(--mt-text);
}

/* The sections, separated by a rule, as on the profile page */
.section {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--mt-border);
}

.section h2 {
  margin: 0 0 12px;
  color: var(--mt-blue);
  font-size: 1.2rem;
}

/* Terms on the left, values on the right */
.facts {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 6px 24px;
  margin: 0;
}

.facts dt {
  font-weight: 600;
}

.facts dd {
  margin: 0;
}

/* The description as typed: paragraphs and line breaks kept */
.description {
  margin: 0;
  max-width: 760px;
  white-space: pre-wrap;
}
</style>
