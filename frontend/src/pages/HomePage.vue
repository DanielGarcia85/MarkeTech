<!--
  frontend/src/pages/HomePage.vue

  Home page — first page displayed when the application opens
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for the address "/". Says in one line what
  MarkeTech is for, in the language of the visitor, then shows the job
  offers: the list is the heart of the site, so it is the first thing seen.
-->

<script setup lang="ts">
import { useI18n } from "vue-i18n";

import logoUrl from "../assets/logo.svg";
import ApiStatus from "../components/ApiStatus.vue";
import OfferList from "../components/OfferList.vue";

// t translates a key into the language currently displayed
const { t } = useI18n();
</script>

<template>
  <section class="hero">
    <img :src="logoUrl" alt="MarkeTech" class="logo" />
    <h1 class="tagline">{{ t("app.tagline") }}</h1>
    <p>{{ t("app.notice") }}</p>
    <ApiStatus class="status" />
  </section>
  <OfferList />
</template>

<style scoped>
.hero {
  text-align: center;
  padding: 16px 0 32px;
}

.logo {
  width: 220px;
  max-width: 100%;
}

.tagline {
  margin: 24px 0 8px;
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--mt-blue);
}

/* Small and muted: a detail, under the notice */
.status {
  margin: 4px 0 0;
  color: var(--mt-muted);
  font-size: 0.85rem;
}
</style>
