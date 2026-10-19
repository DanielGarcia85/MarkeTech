<!--
  frontend/src/pages/NotFoundPage.vue

  Not-found page — shown for any address the router does not know
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the catch-all route of router.ts, the address staying as it
  was typed. Says that there is nothing here and offers the home page. The
  server itself answers 200 with the application for every address, as a
  single-page application needs: only the page says "not found".
-->

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>

<template>
  <h1>{{ t("notFound.title") }}</h1>
  <p>{{ t("notFound.text") }}</p>
  <p>
    <RouterLink :to="{ name: 'home' }">{{ t("notFound.homeLink") }}</RouterLink>
  </p>
</template>
