<!--
  frontend/src/pages/MyFavoritesPage.vue

  My favorites page — the offers the logged-in candidate put aside
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/candidate/favorites", to a candidate only
  (the router sends anyone else away). The offers as the cards of the
  public list, newest favorite first, the heart filled on each; a click on
  it takes the offer back and the card leaves the list. An offer closed
  since it was put aside stays, with its state, until the candidate takes
  it back (decision of 21.10.2026).
-->

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import { listFavorites, type Favorite } from "../api/favorites";
import { getCountries, type Country } from "../api/profile";
import EmptyState from "../components/EmptyState.vue";
import OfferCard from "../components/OfferCard.vue";

const { t, locale } = useI18n();

const favorites = ref<Favorite[] | null>(null);
const loadFailed = ref(false);
const countries = ref<Country[]>([]);

async function load(): Promise<void> {
  loadFailed.value = false;
  try {
    favorites.value = await listFavorites();
  } catch {
    loadFailed.value = true;
  }
}

async function loadCountries(): Promise<void> {
  try {
    countries.value = await getCountries();
  } catch {
    // The codes show instead of the names
  }
}

// The heart of a card was clicked: taken back, the offer leaves the list
function changed(favorite: Favorite, kept: boolean): void {
  if (!kept) favorites.value = (favorites.value ?? []).filter((item) => item.id !== favorite.id);
}

watch(locale, loadCountries);

onMounted(() => {
  load();
  loadCountries();
});
</script>

<template>
  <h1>{{ t("myFavorites.title") }}</h1>

  <p v-if="loadFailed" class="error">{{ t("myFavorites.loadFailed") }}</p>

  <template v-else-if="favorites">
    <EmptyState v-if="favorites.length === 0" icon="heart" :text="t('myFavorites.none')">
      <RouterLink :to="{ name: 'home' }">{{ t("empty.browse") }}</RouterLink>
    </EmptyState>
    <ul v-else class="cards">
      <li v-for="favorite in favorites" :key="favorite.id">
        <OfferCard :offer="favorite.offer" :countries="countries" @favorite="changed(favorite, $event)" />
      </li>
    </ul>
  </template>
</template>

<style scoped>
.cards {
  margin: 16px 0 0;
  padding: 0;
  list-style: none;
}
</style>
