<!--
  frontend/src/pages/HomePage.vue

  Home page — first page displayed when the application opens
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for the address "/". The logo and one line on
  what MarkeTech is for, in the language of the visitor, then the job
  offers: the list is the heart of the site, so it is the first thing seen
  (the notice and the state of the API are in the header since 21.10.2026).
-->

<script setup lang="ts">
import { useI18n } from "vue-i18n";

import logoUrl from "../assets/logo.svg";
import OfferList from "../components/OfferList.vue";

// t translates a key into the language currently displayed
const { t } = useI18n();
</script>

<template>
  <section class="hero">
    <img :src="logoUrl" alt="MarkeTech" class="logo" />
    <h1 class="tagline">{{ t("app.tagline") }}</h1>
  </section>
  <OfferList />
</template>

<style scoped>
.hero {
  text-align: center;
  padding: 16px 0 24px;
}

.logo {
  width: 220px;
  max-width: 100%;
}

.tagline {
  margin: 24px 0 0;
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--mt-blue);
}
</style>
