<!--
  frontend/src/components/OfferList.vue

  Offer list — the public list of the published job offers
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the home page, to anyone. A form of filters above a list of
  cards, newest first, ten by page, with the numbers of the pages. The
  filters and the page live in the address of the page (?title=...&page=2):
  a search can be shared or reloaded, and the back button goes back to the
  previous search. On a narrow screen the filters fold behind a button.
  Each card links to the page of its offer.
-->

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter, type LocationQuery } from "vue-router";

import {
  CONTRACTS,
  CURRENCIES,
  EMPTY_FILTERS,
  PAGE_SIZE,
  REMOTES,
  SALARY_PERIODS,
  listOffers,
  type OfferFilters,
  type OfferPage,
} from "../api/offers";
import { getCountries, type Country } from "../api/profile";
import OfferCard from "./OfferCard.vue";

const { t, locale } = useI18n();
const route = useRoute();
const router = useRouter();

// ── The state ─────────────────────────────────────────────────────────

// The filters of the form and the page shown, read from the address
const filters = reactive<OfferFilters>({ ...EMPTY_FILTERS, ...fromQuery(route.query) });
const page = ref(pageOf(route.query));

// The answer of the backend, or null until it arrives
const result = ref<OfferPage | null>(null);
const loadFailed = ref(false);
const countries = ref<Country[]>([]);

const pages = computed(() => (result.value ? Math.max(1, Math.ceil(result.value.count / PAGE_SIZE)) : 1));

// The numbers shown between Previous and Next: all of them up to seven
// pages, else the first, the last, the current one with its neighbours,
// and "…" (0) for what is skipped
const pageItems = computed<number[]>(() => {
  const last = pages.value;
  if (last <= 7) return Array.from({ length: last }, (_, i) => i + 1);
  const around = [page.value - 1, page.value, page.value + 1].filter((n) => n > 1 && n < last);
  const items = [1, ...around, last];
  const withGaps: number[] = [];
  for (const [i, n] of items.entries()) {
    if (i > 0 && n - (items[i - 1] ?? 0) > 1) withGaps.push(0);
    withGaps.push(n);
  }
  return withGaps;
});

// On a narrow screen, the filters are folded until this is true; the
// button shows how many filters are set (the period and the currency only
// qualify the amount)
const filtersOpen = ref(false);
const activeFilters = computed(
  () => Object.entries(filters).filter(([key, value]) => value && !qualifies(key)).length,
);

function qualifies(key: string): boolean {
  return key === "salary_period" || key === "currency";
}

// ── The address ───────────────────────────────────────────────────────

// The filters found in the address: the known keys with a text value only
function fromQuery(query: LocationQuery): Partial<OfferFilters> {
  const found: Partial<OfferFilters> = {};
  for (const key of Object.keys(EMPTY_FILTERS) as (keyof OfferFilters)[]) {
    const value = query[key];
    if (typeof value === "string") found[key] = value as never;
  }
  return found;
}

function pageOf(query: LocationQuery): number {
  const value = Number(query.page);
  return Number.isInteger(value) && value > 1 ? value : 1;
}

// The address of the current search: the filters that are set, the page
// when it is not the first
function toQuery(): Record<string, string> {
  const query: Record<string, string> = {};
  for (const [key, value] of Object.entries(filters)) {
    if (value && (!qualifies(key) || filters.salary_min)) query[key] = value;
  }
  if (page.value > 1) query.page = String(page.value);
  return query;
}

// ── Loading ───────────────────────────────────────────────────────────

async function load(): Promise<void> {
  loadFailed.value = false;
  try {
    result.value = await listOffers(filters, page.value);
  } catch {
    loadFailed.value = true;
  }
}

async function loadCountries(): Promise<void> {
  try {
    countries.value = await getCountries();
  } catch {
    // The codes show instead of the names: not worth an error message
  }
}

// A new search starts at the first page; writing the address is what
// triggers the loading (watch below), so that the back button works alike
function search(): void {
  page.value = 1;
  filtersOpen.value = false;
  router.push({ query: toQuery() });
}

function reset(): void {
  Object.assign(filters, EMPTY_FILTERS);
  search();
}

function goTo(target: number): void {
  page.value = target;
  router.push({ query: toQuery() });
  window.scrollTo(0, 0);
}

// The address changed (a search, a page, the back button): read it again
// and ask the backend
watch(
  () => route.query,
  (query) => {
    Object.assign(filters, EMPTY_FILTERS, fromQuery(query));
    page.value = pageOf(query);
    load();
  },
);

// The names of the countries follow the language displayed
watch(locale, loadCountries);

onMounted(() => {
  load();
  loadCountries();
});
</script>

<template>
  <h2 class="heading">{{ t("offers.title") }}</h2>

  <!-- Narrow screens only (CSS): unfolds the filters -->
  <button type="button" class="toggle" :aria-expanded="filtersOpen" @click="filtersOpen = !filtersOpen">
    {{ t("offers.filters") }}<span v-if="activeFilters"> ({{ activeFilters }})</span>
  </button>

  <!-- The filters: sent on Search, or Enter in a field -->
  <form class="filters" :class="{ open: filtersOpen }" novalidate @submit.prevent="search">
    <div class="field">
      <label for="title">{{ t("offers.keyword") }}</label>
      <input id="title" v-model.trim="filters.title" type="text" :placeholder="t('offers.keywordHint')" />
    </div>
    <div class="field">
      <label for="city">{{ t("offers.city") }}</label>
      <input id="city" v-model.trim="filters.city" type="text" />
    </div>
    <div class="field">
      <label for="country">{{ t("offers.country") }}</label>
      <select id="country" v-model="filters.country">
        <option value="">{{ t("offers.anyCountry") }}</option>
        <option v-for="(country, index) in countries" :key="index" :value="country.code">
          {{ country.name }}
        </option>
      </select>
    </div>
    <div class="field">
      <label for="contract">{{ t("offers.contractLabel") }}</label>
      <select id="contract" v-model="filters.contract">
        <option value="">{{ t("offers.anyContract") }}</option>
        <option v-for="contract in CONTRACTS" :key="contract" :value="contract">
          {{ t("offers.contract." + contract) }}
        </option>
      </select>
    </div>
    <div class="field">
      <label for="remote">{{ t("offers.remoteLabel") }}</label>
      <select id="remote" v-model="filters.remote">
        <option value="">{{ t("offers.anyRemote") }}</option>
        <option v-for="remote in REMOTES" :key="remote" :value="remote">
          {{ t("offers.remote." + remote) }}
        </option>
      </select>
    </div>
    <div class="field salary">
      <label for="salary">{{ t("offers.salaryMin") }}</label>
      <div class="pair">
        <input id="salary" v-model.trim="filters.salary_min" type="number" min="0" step="100" />
        <select v-model="filters.currency" :aria-label="t('offers.currencyLabel')">
          <option v-for="currency in CURRENCIES" :key="currency" :value="currency">{{ currency }}</option>
        </select>
        <select v-model="filters.salary_period" :aria-label="t('offers.periodLabel')">
          <option v-for="period in SALARY_PERIODS" :key="period" :value="period">
            {{ t("offers.period." + period) }}
          </option>
        </select>
      </div>
    </div>
    <div class="field">
      <label for="since">{{ t("offers.publishedAfter") }}</label>
      <input id="since" v-model="filters.published_after" type="date" />
    </div>
    <p class="actions">
      <button type="submit" class="primary">{{ t("offers.search") }}</button>
      <button type="button" class="as-link" @click="reset">{{ t("offers.reset") }}</button>
    </p>
  </form>

  <p v-if="loadFailed" class="error">{{ t("offers.loadFailed") }}</p>

  <template v-else-if="result">
    <p class="count">{{ t("offers.count", result.count) }}</p>
    <p v-if="result.count === 0" class="muted">{{ t("offers.none") }}</p>
    <ul v-else class="cards">
      <li v-for="offer in result.results" :key="offer.id">
        <OfferCard :offer="offer" :countries="countries" />
      </li>
    </ul>

    <!-- The pages, when there is more than one -->
    <nav v-if="pages > 1" class="pages" :aria-label="t('offers.page', { page, pages })">
      <button type="button" class="as-link" :disabled="!result.previous" @click="goTo(page - 1)">
        {{ t("offers.previous") }}
      </button>
      <ol class="numbers">
        <li v-for="(item, index) in pageItems" :key="index">
          <span v-if="item === 0" class="gap">…</span>
          <button
            v-else
            type="button"
            class="number"
            :class="{ current: item === page }"
            :aria-current="item === page ? 'page' : undefined"
            @click="goTo(item)"
          >
            {{ item }}
          </button>
        </li>
      </ol>
      <button type="button" class="as-link" :disabled="!result.next" @click="goTo(page + 1)">
        {{ t("offers.next") }}
      </button>
    </nav>
  </template>
</template>

<style scoped>
.heading {
  margin: 0 0 12px;
  color: var(--mt-blue);
  font-size: 1.3rem;
}

/* The filters on a grid: as many fields per line as the width allows */
.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0 16px;
  padding: 16px 16px 4px;
  border: 1px solid var(--mt-border);
  border-radius: 8px;
  background: var(--mt-surface);
}

/* The fields of the grid take its whole column */
.filters .field input,
.filters .field select {
  max-width: none;
}

/* An amount, its currency and its period, side by side: the amount takes
   the width the two lists leave, and keeps room for six figures */
.pair {
  display: flex;
  gap: 8px;
}

.pair input {
  flex: 1;
  min-width: 100px;
}

.pair select {
  flex: none;
  width: auto;
}

/* The two buttons, on a line of their own at the end of the grid */
.actions {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 0 0 12px;
}

.count {
  margin: 20px 0 8px;
  color: var(--mt-muted);
}

.muted {
  color: var(--mt-muted);
}

/* The cards, one under the other, without bullets */
.cards {
  margin: 0;
  padding: 0;
  list-style: none;
}

/* Previous, the numbers of the pages, next */
.pages {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 16px 24px;
  margin: 24px 0;
}

.pages > button:disabled {
  color: var(--mt-muted);
  text-decoration: none;
  cursor: default;
}

.numbers {
  display: flex;
  gap: 4px;
  margin: 0;
  padding: 0;
  list-style: none;
}

/* A number is a small square; the current page is filled in blue */
.number,
.gap {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 36px;
  padding: 0 6px;
  border: 1px solid var(--mt-border);
  border-radius: 4px;
  background: var(--mt-background);
  color: var(--mt-blue);
  font: inherit;
  cursor: pointer;
}

.number:hover {
  background: var(--mt-surface);
}

.number.current {
  border-color: var(--mt-blue);
  background: var(--mt-blue);
  color: #ffffff;
  cursor: default;
}

.gap {
  border: none;
  color: var(--mt-muted);
  cursor: default;
}

/* The button that unfolds the filters: narrow screens only */
.toggle {
  display: none;
  margin-bottom: 12px;
  padding: 8px 16px;
  border: 1px solid var(--mt-border);
  border-radius: 4px;
  background: var(--mt-surface);
  color: var(--mt-text);
  font: inherit;
  cursor: pointer;
}

@media (max-width: 720px) {
  .toggle {
    display: inline-block;
  }

  .filters:not(.open) {
    display: none;
  }
}

/* Wide enough for several columns: the salary and its two lists take two */
@media (min-width: 721px) {
  .salary {
    grid-column: span 2;
  }
}
</style>
