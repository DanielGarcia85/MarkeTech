<!--
  frontend/src/pages/HomePage.vue

  Home page — first page displayed when the application opens
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for the address "/". A band in the light blue,
  fading to white: the logo, a short rule in the accent colour, one line
  on what MarkeTech is for, in the language of the visitor; then the job
  offers: the list is the heart of the site, so it comes right under (the
  notice and the state of the API are in the header since 21.10.2026).
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
/* The band: the light blue fading to white towards the bottom, soft
   corners */
.hero {
  margin: 0 0 20px;
  padding: 24px 16px 22px;
  border: 1px solid var(--mt-blue-border);
  border-radius: 14px;
  background: linear-gradient(180deg, var(--mt-blue-surface), var(--mt-background));
  text-align: center;
}

.logo {
  width: 220px;
  max-width: 100%;
}

/* The short rule in the accent colour between the logo and the line */
.tagline::before {
  content: "";
  display: block;
  width: 56px;
  height: 4px;
  margin: 6px auto 12px;
  border-radius: 2px;
  background: var(--mt-accent);
}

.tagline {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--mt-blue-dark);
}
</style>
